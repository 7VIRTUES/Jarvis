import json

from jarvis_core.approvals import ApprovalQueue
from jarvis_core.audit import JsonlLogger
from jarvis_core.db import init_db
from jarvis_core.diagnostics import DiagnosticExporter
from jarvis_core.events import EventBus
from jarvis_core.reports import REQUIRED_IMPLEMENTATION_REPORT_SECTIONS, missing_implementation_report_sections
from jarvis_core.risk import validate_risk_budget
from jarvis_core.runtime import SafeActionRuntime
from jarvis_core.tasks import TaskQueue


def stack(tmp_path):
    conn = init_db(tmp_path / "jarvis.sqlite")
    logger = JsonlLogger(tmp_path / "logs")
    events = EventBus(conn, logger)
    runtime = SafeActionRuntime(logger, conn, events)
    approvals = ApprovalQueue(conn, events)
    tasks = TaskQueue(conn, events, runtime, approvals)
    return conn, logger, events, runtime, approvals, tasks


def test_task_create_list_read_cancel(tmp_path):
    _, _, _, _, _, tasks = stack(tmp_path)

    task = tasks.create_task("sample", "coding_agent", "inspect", dry_run=False)
    canceled = tasks.cancel_task(task["task_id"])

    assert task["status"] == "queued"
    assert tasks.get_task(task["task_id"])["task_id"] == task["task_id"]
    assert len(tasks.list_tasks()) == 1
    assert canceled["status"] == "canceled"


def test_event_creation_and_query(tmp_path):
    _, _, events, _, _, _ = stack(tmp_path)

    event = events.emit("task.created", "task-1", {"ok": True})

    assert events.list_events()[0]["event_id"] == event["event_id"]
    assert events.list_events("task-1")[0]["payload"] == {"ok": True}


def test_approval_request_approve_reject(tmp_path):
    _, _, _, _, approvals, _ = stack(tmp_path)

    approval = approvals.request_approval("task-1", "sensitive_write", "sample", "medium", "needs human review")
    approved = approvals.approve(approval["approval_id"], "local_user", "ok")
    rejected_source = approvals.request_approval("task-2", "sensitive_write", "sample", "medium", "reject this")
    rejected = approvals.reject(rejected_source["approval_id"], "local_user", "no")

    assert approved["status"] == "approved"
    assert rejected["status"] == "rejected"


def test_resolved_approval_cannot_be_reopened(tmp_path):
    _, _, _, _, approvals, _ = stack(tmp_path)

    approval = approvals.request_approval("task-1", "sensitive_write", "sample", "medium", "reject then try approve")
    rejected = approvals.reject(approval["approval_id"], "local_user", "no")
    reopened = approvals.approve(approval["approval_id"], "local_user", "try reopen")

    assert rejected["status"] == "rejected"
    assert reopened["status"] == "rejected"


def test_risk_budget_approval_can_be_approved(tmp_path):
    _, _, _, _, approvals, _ = stack(tmp_path)

    approval = approvals.request_approval("task-1", "risk_budget", "sample", "high", "over budget")
    approved = approvals.approve(approval["approval_id"], "local_user", "accepted")

    assert approved["status"] == "approved"


def test_approval_does_not_override_hard_blocked_actions(tmp_path):
    _, _, _, _, approvals, _ = stack(tmp_path)

    approval = approvals.request_approval("task-1", "codex_execute", "sample", "high", "blocked in v0.1B")
    resolved = approvals.approve(approval["approval_id"], "local_user", "try approve")

    assert resolved["status"] == "rejected"
    assert "cannot override" in resolved["resolution_note"]


def test_project_lock_blocks_concurrent_write_tasks(tmp_path):
    _, _, _, _, _, tasks = stack(tmp_path)

    first = tasks.create_task("sample", "coding_agent", "operate", dry_run=False, write_capable=True)
    second = tasks.create_task("sample", "coding_agent", "operate", dry_run=False, write_capable=True)

    assert first["status"] == "queued"
    assert second["status"] == "blocked"


def test_write_capable_task_type_cannot_bypass_lock_with_false_flag(tmp_path):
    _, _, _, _, _, tasks = stack(tmp_path)

    first = tasks.create_task("sample", "coding_agent", "operate", dry_run=False, write_capable=True)
    second = tasks.create_task("sample", "coding_agent", "operate", dry_run=False, write_capable=False)

    assert first["write_capable"] is True
    assert second["write_capable"] is True
    assert second["status"] == "blocked"


def test_dry_run_creates_plan_and_receipts_without_execution(tmp_path):
    _, _, events, runtime, _, tasks = stack(tmp_path)

    task = tasks.create_task(
        "sample",
        "coding_agent",
        "inspect",
        dry_run=True,
        proposed_actions=[{"tool_id": "report_tool", "action_type": "inspect_project", "target": "sample"}],
    )

    receipts = runtime.list_receipts(task["task_id"])
    assert task["status"] == "succeeded"
    assert receipts[0]["approved"] is True
    assert events.list_events(task["task_id"])


def test_action_receipts_for_blocked_and_approval_required_actions(tmp_path):
    _, _, _, runtime, approvals, tasks = stack(tmp_path)

    blocked = tasks.create_task(
        "sample",
        "coding_agent",
        "plan",
        dry_run=True,
        proposed_actions=[{"tool_id": "codex_tool", "action_type": "codex_execute", "target": "codex exec"}],
    )
    approval_required = tasks.create_task(
        "sample",
        "coding_agent",
        "plan",
        dry_run=True,
        proposed_actions=[{"tool_id": "filesystem_tool", "action_type": "sensitive_write", "target": "future"}],
    )

    assert runtime.list_receipts(blocked["task_id"])[0]["blocked"] is True
    assert runtime.list_receipts(approval_required["task_id"])[0]["approval_required"] is True
    assert approvals.list_approvals()


def test_risk_budget_validation_and_task_waiting_for_approval(tmp_path):
    _, _, _, _, approvals, tasks = stack(tmp_path)

    result = validate_risk_budget({"changedFiles": 11})
    task = tasks.create_task("sample", "coding_agent", "plan", dry_run=True, risk_plan={"changedFiles": 11})

    assert result.approval_required is True
    assert task["status"] == "waiting_for_approval"
    assert approvals.list_approvals()[0]["action_type"] == "risk_budget"


def test_invalid_risk_budget_requires_approval(tmp_path):
    result = validate_risk_budget({"changedFiles": "many"})

    assert result.approval_required is True
    assert "must be an integer" in result.reason


def test_diagnostic_export_excludes_secret_values(tmp_path):
    conn, logger, events, runtime, approvals, tasks = stack(tmp_path)
    connector_root = tmp_path / "connectors"
    placeholders = connector_root / "placeholders"
    placeholders.mkdir(parents=True)
    (placeholders / "gmail.json").write_text(
        json.dumps({"id": "gmail", "provider": "Gmail", "implemented": False, "defaultEnabled": False, "readinessLevel": "placeholder_only", "tokenStorage": "not_implemented"}),
        encoding="utf-8",
    )
    (tmp_path / ".env").write_text("SECRET_VALUE_SHOULD_NOT_EXPORT=1", encoding="utf-8")
    tasks.create_task("sample", "coding_agent", "inspect", dry_run=True)

    exported = DiagnosticExporter(conn, tmp_path, tmp_path / "logs", connector_root).export()
    exported_text = json.dumps(exported)

    assert "SECRET_VALUE_SHOULD_NOT_EXPORT" not in exported_text
    assert exported["connectors"][0]["implemented"] is False


def test_report_required_sections_validation():
    report = "\n".join(f"## {section}" for section in REQUIRED_IMPLEMENTATION_REPORT_SECTIONS)

    assert missing_implementation_report_sections(report) == []
    assert missing_implementation_report_sections("## Summary") == REQUIRED_IMPLEMENTATION_REPORT_SECTIONS[1:]
