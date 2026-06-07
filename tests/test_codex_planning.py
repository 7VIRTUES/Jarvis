import json
from pathlib import Path

import pytest

from jarvis_core.approvals import ApprovalQueue
from jarvis_core.audit import JsonlLogger
from jarvis_core.codex_paths import validate_codex_project_paths
from jarvis_core.codex_plans import ALLOWED_SANDBOX_MODE, CodexPlanInput, CodexPlanService
from jarvis_core.db import init_db
from jarvis_core.diagnostics import DiagnosticExporter
from jarvis_core.events import EventBus
from jarvis_core.permissions import check_action
from jarvis_core.project_registry import ProjectRegistry
from jarvis_core.registries import load_manifest
from jarvis_core.reports import REQUIRED_IMPLEMENTATION_REPORT_SECTIONS, missing_implementation_report_sections
from jarvis_core.runtime import SafeActionRuntime


def symlink_or_skip(link, target):
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable in this environment: {exc}")


def stack(tmp_path):
    conn = init_db(tmp_path / "jarvis.sqlite")
    logger = JsonlLogger(tmp_path / "logs")
    events = EventBus(conn, logger)
    runtime = SafeActionRuntime(logger, conn, events)
    approvals = ApprovalQueue(conn, events)
    projects = ProjectRegistry(conn, tmp_path)
    service = CodexPlanService(conn, events, runtime, approvals, projects)
    project = tmp_path / "sample"
    project.mkdir()
    projects.add_project("sample", project)
    return conn, logger, events, runtime, approvals, projects, service, project


def plan_payload(**overrides):
    values = {
        "task_id": "task-1",
        "project_name": "sample",
        "task_goal": "Add a small safe report.",
        "exact_scope": "Only update report files.",
        "non_goals": "No execution.",
        "allowed_files": [".jarvis/reports"],
        "test_commands": ["python -m pytest"],
        "risk_plan": {"changedFiles": 1, "diffLines": 20},
    }
    values.update(overrides)
    return CodexPlanInput(**values)


def test_create_list_read_codex_plan_requires_approval(tmp_path):
    _, _, events, runtime, approvals, _, service, project = stack(tmp_path)

    plan = service.create_plan(plan_payload())

    assert plan["status"] == "waiting_for_approval"
    assert plan["mode"] == "approval_required"
    assert plan["approval_required"] is True
    assert plan["approval_id"]
    assert service.list_plans()[0]["plan_id"] == plan["plan_id"]
    assert service.get_plan(plan["plan_id"])["project_path"] == str(project.resolve())
    assert approvals.get_approval(plan["approval_id"])["status"] == "pending"
    assert runtime.list_receipts("task-1")
    assert any(event["event_type"] == "codex.plan_created" for event in events.list_events("task-1"))


def test_command_preview_uses_only_allowed_flags_and_does_not_execute(tmp_path):
    _, _, _, _, _, _, service, _ = stack(tmp_path)

    plan = service.create_plan(plan_payload())
    preview = plan["command_preview"]
    argv = preview["argv"]

    assert argv[0:2] == ["codex", "exec"]
    assert "--cd" in argv
    assert "--sandbox" in argv
    assert argv[argv.index("--sandbox") + 1] == ALLOWED_SANDBOX_MODE
    assert "--ask-for-approval" in argv
    assert argv[argv.index("--ask-for-approval") + 1] == "never"
    assert "--output-last-message" in argv
    assert preview["executed"] is False
    assert "--browser" not in argv
    assert "--api-key" not in argv


def test_approval_marks_plan_approved_for_future_execution_without_execution(tmp_path):
    _, _, events, runtime, approvals, _, service, _ = stack(tmp_path)
    plan = service.create_plan(plan_payload())

    approved = service.approve_for_future_execution(plan["plan_id"], "local_user", "approved for future slice")

    assert approved["status"] == "approved_for_future_execution"
    assert approvals.get_approval(plan["approval_id"])["status"] == "approved"
    assert all(receipt["action_type"] != "codex.execute" for receipt in runtime.list_receipts("task-1"))
    assert any(event["event_type"] == "codex.approved_for_future_execution" for event in events.list_events("task-1"))


def test_rejection_marks_plan_rejected_without_execution(tmp_path):
    _, _, events, runtime, approvals, _, service, _ = stack(tmp_path)
    plan = service.create_plan(plan_payload())

    rejected = service.reject_plan(plan["plan_id"], "local_user", "not now")

    assert rejected["status"] == "rejected"
    assert approvals.get_approval(plan["approval_id"])["status"] == "rejected"
    assert all(receipt["action_type"] != "codex.execute" for receipt in runtime.list_receipts("task-1"))
    assert any(event["event_type"] == "codex.rejected" for event in events.list_events("task-1"))


def test_hard_blocked_action_inside_plan_is_blocked(tmp_path):
    _, _, _, _, _, _, service, _ = stack(tmp_path)

    plan = service.create_plan(plan_payload(task_goal="Run git push after edits."))

    assert plan["status"] == "blocked"
    assert "git" in plan["risk_reasons"][0].lower()


def test_malformed_command_fields_are_blocked(tmp_path):
    _, _, _, _, _, _, service, _ = stack(tmp_path)

    plan = service.create_plan(plan_payload(sandbox_mode="danger-full-access"))

    assert plan["status"] == "blocked"
    assert "sandbox mode" in plan["risk_reasons"][0]


def test_project_path_outside_registered_project_is_blocked(tmp_path):
    _, _, _, _, _, _, service, _ = stack(tmp_path)

    plan = service.create_plan(plan_payload(project_name="missing"))

    assert plan["status"] == "blocked"
    assert "registered project" in plan["risk_reasons"][0]


def test_prompt_path_outside_jarvis_prompts_is_blocked(tmp_path):
    _, _, _, _, _, _, service, _ = stack(tmp_path)

    plan = service.create_plan(plan_payload(prompt_path="README.md"))

    assert plan["status"] == "blocked"
    assert ".jarvis/prompts" in plan["risk_reasons"][0]


def test_output_path_outside_jarvis_reports_is_blocked(tmp_path):
    _, _, _, _, _, _, service, _ = stack(tmp_path)

    plan = service.create_plan(plan_payload(output_path="reports/latest.md"))

    assert plan["status"] == "blocked"
    assert ".jarvis/reports" in plan["risk_reasons"][0]


def test_symlinked_prompts_root_escaping_project_is_blocked(tmp_path):
    _, _, _, _, _, _, service, project = stack(tmp_path)
    outside = tmp_path / "outside-prompts"
    outside.mkdir()
    (project / ".jarvis").mkdir()
    symlink_or_skip(project / ".jarvis" / "prompts", outside)

    plan = service.create_plan(plan_payload())

    assert plan["status"] == "blocked"
    assert "prompts" in plan["risk_reasons"][0]


def test_symlinked_reports_root_escaping_project_is_blocked(tmp_path):
    _, _, _, _, _, _, service, project = stack(tmp_path)
    outside = tmp_path / "outside-reports"
    outside.mkdir()
    (project / ".jarvis").mkdir()
    symlink_or_skip(project / ".jarvis" / "reports", outside)

    plan = service.create_plan(plan_payload())

    assert plan["status"] == "blocked"
    assert "reports" in plan["risk_reasons"][0]


def test_resolved_prompt_and_report_roots_outside_project_are_blocked(tmp_path):
    _, _, _, _, _, _, service, project = stack(tmp_path)
    outside = tmp_path / "outside-jarvis"
    outside.mkdir()
    symlink_or_skip(project / ".jarvis", outside)

    prompt_plan = service.create_plan(plan_payload())

    assert prompt_plan["status"] == "blocked"
    assert "project" in prompt_plan["risk_reasons"][0]


def test_mocked_resolved_prompts_root_outside_project_is_blocked(tmp_path, monkeypatch):
    project = tmp_path / "sample"
    project.mkdir()
    outside = tmp_path / "outside"
    original_resolve = Path.resolve

    def fake_resolve(self, *args, **kwargs):
        if self.parts[-3:] == (".jarvis", "prompts", "current-task.md"):
            return outside / "current-task.md"
        if self.parts[-2:] == (".jarvis", "prompts"):
            return outside
        return original_resolve(self, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", fake_resolve)

    reason, _, _, _ = validate_codex_project_paths(project, ".jarvis/prompts/current-task.md", ".jarvis/reports/latest-codex-output.md", "workspace-write")

    assert reason is not None
    assert "prompts" in reason


def test_mocked_resolved_reports_root_outside_project_is_blocked(tmp_path, monkeypatch):
    project = tmp_path / "sample"
    project.mkdir()
    outside = tmp_path / "outside"
    original_resolve = Path.resolve

    def fake_resolve(self, *args, **kwargs):
        if self.parts[-3:] == (".jarvis", "reports", "latest-codex-output.md"):
            return outside / "latest-codex-output.md"
        if self.parts[-2:] == (".jarvis", "reports"):
            return outside
        return original_resolve(self, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", fake_resolve)

    reason, _, _, _ = validate_codex_project_paths(project, ".jarvis/prompts/current-task.md", ".jarvis/reports/latest-codex-output.md", "workspace-write")

    assert reason is not None
    assert "reports" in reason


def test_protected_file_paths_are_blocked(tmp_path):
    _, _, _, _, _, _, service, _ = stack(tmp_path)

    plan = service.create_plan(plan_payload(prompt_path=".jarvis/prompts/.env"))

    assert plan["status"] == "blocked"
    assert "protected" in plan["risk_reasons"][0]


def test_execution_actions_return_blocked():
    for action_type in ["codex.execute", "codex.exec", "codex.run", "run_codex_exec_workspace_write"]:
        result = check_action(action_type)
        assert result.status == "blocked"


def test_diagnostics_include_plan_summary_but_not_prompt_content_or_secrets(tmp_path):
    conn, logger, _, _, _, _, service, _ = stack(tmp_path)
    connector_root = tmp_path / "connectors"
    placeholders = connector_root / "placeholders"
    placeholders.mkdir(parents=True)
    (placeholders / "github.json").write_text(
        json.dumps({"id": "github", "provider": "GitHub", "implemented": False, "defaultEnabled": False, "readinessLevel": "placeholder_only", "tokenStorage": "not_implemented"}),
        encoding="utf-8",
    )
    secret_goal = "Do not export SECRET_VALUE_IN_PROMPT"
    plan = service.create_plan(plan_payload(task_goal=secret_goal))

    exported = DiagnosticExporter(conn, tmp_path, tmp_path / "logs", connector_root).export()
    exported_text = json.dumps(exported)

    assert exported["codexPlans"][0]["plan_id"] == plan["plan_id"]
    assert "SECRET_VALUE_IN_PROMPT" not in exported_text
    assert '"command_preview":' not in exported_text


def test_codex_tool_manifest_and_future_connectors_validate():
    root = __import__("pathlib").Path(__file__).resolve().parents[1]

    tool = load_manifest(root / "connectors" / "tools" / "codex_tool.json", "tool")
    assert "plan_codex_execution" in tool["capabilities"]
    for path in (root / "connectors" / "placeholders").glob("*.json"):
        manifest = load_manifest(path, "connector")
        assert manifest["implemented"] is False
        assert manifest["defaultEnabled"] is False


def test_report_validation_still_passes():
    report = "\n".join(f"## {section}" for section in REQUIRED_IMPLEMENTATION_REPORT_SECTIONS)
    assert missing_implementation_report_sections(report) == []
