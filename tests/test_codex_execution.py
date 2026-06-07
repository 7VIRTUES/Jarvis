import json
import subprocess

import pytest

from jarvis_core.approvals import ApprovalQueue
from jarvis_core.audit import JsonlLogger
from jarvis_core.codex_execution import CodexExecutionService
from jarvis_core.codex_plans import CodexPlanInput, CodexPlanService
from jarvis_core.db import init_db
from jarvis_core.diagnostics import DiagnosticExporter
from jarvis_core.events import EventBus
from jarvis_core.project_registry import ProjectRegistry
from jarvis_core.runtime import SafeActionRuntime


def symlink_or_skip(link, target):
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable in this environment: {exc}")


def stack(tmp_path, runner=None, detector=None):
    conn = init_db(tmp_path / "jarvis.sqlite")
    logger = JsonlLogger(tmp_path / "logs")
    events = EventBus(conn, logger)
    runtime = SafeActionRuntime(logger, conn, events)
    approvals = ApprovalQueue(conn, events)
    projects = ProjectRegistry(conn, tmp_path)
    plans = CodexPlanService(conn, events, runtime, approvals, projects)
    execution = CodexExecutionService(conn, events, runtime, approvals, projects, plans, detector or (lambda: "codex"), runner or success_runner)
    project = tmp_path / "sample"
    project.mkdir()
    subprocess.run(["git", "init"], cwd=project, shell=False, check=True, capture_output=True, text=True)
    projects.add_project("sample", project)
    return conn, events, runtime, approvals, projects, plans, execution, project


def success_runner(argv, **kwargs):
    assert kwargs["shell"] is False
    assert argv[0:2] == ["codex", "exec"]
    return subprocess.CompletedProcess(argv, 0, stdout="completed", stderr="")


def dependency_change_runner(argv, **kwargs):
    project = __import__("pathlib").Path(kwargs["cwd"])
    (project / "package.json").write_text('{"scripts":{"test":"node test.js"},"dependencies":{"x":"1.0.0"}}\n', encoding="utf-8")
    return subprocess.CompletedProcess(argv, 0, stdout="changed dependency file", stderr="")


def approved_plan(plans):
    plan = plans.create_plan(
        CodexPlanInput(
            task_id="task-1",
            project_name="sample",
            task_goal="Safe execution test.",
            exact_scope="Only a mocked execution.",
            non_goals="Do not broaden scope.",
            test_commands=["python -m pytest tests/test_codex_execution.py"],
            risk_plan={"changedFiles": 1},
        )
    )
    return plans.approve_for_future_execution(plan["plan_id"], "local_user", "approved")


def test_execution_blocked_for_missing_plan(tmp_path):
    _, events, runtime, _, _, _, execution, _ = stack(tmp_path)

    result = execution.execute_plan("missing")

    assert result["status"] == "blocked"
    assert "not found" in result["blocked_reason"]
    assert runtime.list_receipts()[0]["blocked"] is True
    assert any(event["event_type"] == "codex.execution_blocked" for event in events.list_events())


def test_execution_blocked_without_approval(tmp_path):
    _, _, _, _, _, plans, execution, _ = stack(tmp_path)
    plan = plans.create_plan(CodexPlanInput(task_id="task-1", project_name="sample"))

    result = execution.execute_plan(plan["plan_id"])

    assert result["status"] == "blocked"
    assert "approved_for_future_execution" in result["blocked_reason"]


def test_execution_blocked_for_rejected_plan(tmp_path):
    _, _, _, _, _, plans, execution, _ = stack(tmp_path)
    plan = plans.create_plan(CodexPlanInput(task_id="task-1", project_name="sample"))
    rejected = plans.reject_plan(plan["plan_id"], "local_user", "no")

    result = execution.execute_plan(rejected["plan_id"])

    assert result["status"] == "blocked"
    assert "approved_for_future_execution" in result["blocked_reason"]


def test_execution_blocked_for_project_path_outside_registered_project(tmp_path):
    conn, _, _, _, _, plans, execution, _ = stack(tmp_path)
    plan = approved_plan(plans)
    conn.execute("update codex_plans set project_path = ? where plan_id = ?", (str(tmp_path.parent), plan["plan_id"]))
    conn.commit()

    result = execution.execute_plan(plan["plan_id"])

    assert result["status"] == "blocked"
    assert "registered project" in result["blocked_reason"]


def test_execution_blocked_for_prompt_path_outside_prompts(tmp_path):
    conn, _, _, _, _, plans, execution, project = stack(tmp_path)
    plan = approved_plan(plans)
    conn.execute("update codex_plans set prompt_path = ? where plan_id = ?", (str(project / "README.md"), plan["plan_id"]))
    conn.commit()

    result = execution.execute_plan(plan["plan_id"])

    assert result["status"] == "blocked"
    assert ".jarvis/prompts" in result["blocked_reason"]


def test_execution_blocked_for_output_path_outside_reports(tmp_path):
    conn, _, _, _, _, plans, execution, project = stack(tmp_path)
    plan = approved_plan(plans)
    conn.execute("update codex_plans set output_path = ? where plan_id = ?", (str(project / "latest.md"), plan["plan_id"]))
    conn.commit()

    result = execution.execute_plan(plan["plan_id"])

    assert result["status"] == "blocked"
    assert ".jarvis/reports" in result["blocked_reason"]


def test_execution_blocks_symlinked_prompt_root(tmp_path):
    conn, _, _, _, _, plans, execution, project = stack(tmp_path)
    plan = approved_plan(plans)
    outside = tmp_path / "outside-prompts"
    outside.mkdir()
    (project / ".jarvis").mkdir(exist_ok=True)
    symlink_or_skip(project / ".jarvis" / "prompts", outside)

    result = execution.execute_plan(plan["plan_id"])

    assert result["status"] == "blocked"
    assert "prompts" in result["blocked_reason"]


def test_execution_blocks_symlinked_report_root(tmp_path):
    conn, _, _, _, _, plans, execution, project = stack(tmp_path)
    plan = approved_plan(plans)
    outside = tmp_path / "outside-reports"
    outside.mkdir()
    (project / ".jarvis").mkdir(exist_ok=True)
    symlink_or_skip(project / ".jarvis" / "reports", outside)

    result = execution.execute_plan(plan["plan_id"])

    assert result["status"] == "blocked"
    assert "reports" in result["blocked_reason"]


def test_execution_blocked_for_non_workspace_sandbox(tmp_path):
    conn, _, _, _, _, plans, execution, _ = stack(tmp_path)
    plan = approved_plan(plans)
    conn.execute("update codex_plans set sandbox_mode = ? where plan_id = ?", ("danger-full-access", plan["plan_id"]))
    conn.commit()

    result = execution.execute_plan(plan["plan_id"])

    assert result["status"] == "blocked"
    assert "workspace-write" in result["blocked_reason"]


def test_execution_blocked_if_command_preview_differs(tmp_path):
    conn, _, _, _, _, plans, execution, _ = stack(tmp_path)
    plan = approved_plan(plans)
    preview = dict(plan["command_preview"])
    preview["argv"] = ["codex", "exec", "--cd", "elsewhere"]
    conn.execute("update codex_plans set command_preview = ? where plan_id = ?", (json.dumps(preview), plan["plan_id"]))
    conn.commit()

    result = execution.execute_plan(plan["plan_id"])

    assert result["status"] == "blocked"
    assert "command preview" in result["blocked_reason"]


def test_execution_blocked_for_hard_blocked_approved_plan(tmp_path):
    conn, _, _, _, _, plans, execution, _ = stack(tmp_path)
    plan = approved_plan(plans)
    preview = dict(plan["command_preview"])
    preview["argv"] = [*preview["argv"], "git push"]
    conn.execute("update codex_plans set command_preview = ? where plan_id = ?", (json.dumps(preview), plan["plan_id"]))
    conn.commit()

    result = execution.execute_plan(plan["plan_id"])

    assert result["status"] == "blocked"


def test_execution_blocked_when_max_codex_runs_exceeded(tmp_path):
    conn, _, _, _, _, plans, execution, _ = stack(tmp_path)
    plan = approved_plan(plans)
    for index in range(3):
        conn.execute(
            "insert into codex_executions (execution_id, plan_id, task_id, project_name, status, started_at, codex_command_preview) values (?, ?, ?, ?, ?, ?, ?)",
            (f"exec-{index}", plan["plan_id"], plan["task_id"], plan["project_name"], "succeeded", "now", "codex exec"),
        )
    conn.commit()

    result = execution.execute_plan(plan["plan_id"])

    assert result["status"] == "blocked"
    assert "maxCodexRunsPerTask" in result["blocked_reason"]


def test_project_lock_acquired_and_released_on_success(tmp_path):
    conn, _, _, _, _, plans, execution, _ = stack(tmp_path)
    plan = approved_plan(plans)

    result = execution.execute_plan(plan["plan_id"])

    assert result["status"] == "succeeded"
    assert conn.execute("select count(*) from project_locks").fetchone()[0] == 0


def test_receipt_and_events_created_for_successful_mocked_execution(tmp_path):
    _, events, runtime, _, _, plans, execution, project = stack(tmp_path)
    plan = approved_plan(plans)

    result = execution.execute_plan(plan["plan_id"])
    event_types = [event["event_type"] for event in events.list_events(plan["task_id"])]
    receipts = runtime.list_receipts(plan["task_id"])

    assert result["status"] == "succeeded"
    assert result["receipt_id"]
    assert any(receipt["action_type"] == "codex.execute_approved_plan" for receipt in receipts)
    assert "codex.execution_started" in event_types
    assert "codex.execution_succeeded" in event_types
    assert "codex.check_plan_generated" in event_types
    assert (project / ".jarvis" / "prompts" / "current-task.md").exists()


def test_controlled_codex_flow_stops_before_checks_when_post_review_fails(tmp_path):
    _, events, _, _, _, plans, execution, project = stack(tmp_path, runner=dependency_change_runner)
    plan = approved_plan(plans)

    result = execution.execute_plan(plan["plan_id"])
    event_types = [event["event_type"] for event in events.list_events(plan["task_id"])]

    assert result["status"] == "blocked"
    assert "dependency/package" in result["blocked_reason"]
    assert result["post_review"]["checksMayProceed"] is False
    assert result["check_plan"]["checks"] == [{"name": "test", "command": "npm run test", "source": "package.json scripts"}]
    assert "codex.post_review_blocked" in event_types
    assert "codex.check_plan_generated" not in event_types
    assert (project / "package.json").exists()


def test_execution_prompt_includes_approved_plan_fields(tmp_path):
    _, _, _, _, _, plans, execution, project = stack(tmp_path)
    plan = plans.create_plan(
        CodexPlanInput(
            task_id="task-1",
            project_name="sample",
            task_goal="Approved goal from review",
            exact_scope="Approved exact scope",
            non_goals="Approved non goals",
            allowed_files=["src/allowed.py"],
            test_commands=["python -m pytest tests/test_codex_execution.py"],
            risk_plan={"changedFiles": 1},
        )
    )
    approved = plans.approve_for_future_execution(plan["plan_id"], "local_user", "approved")

    result = execution.execute_plan(approved["plan_id"])
    prompt_text = (project / ".jarvis" / "prompts" / "current-task.md").read_text(encoding="utf-8")

    assert result["status"] == "succeeded"
    assert "Execute only the approved plan represented by this prompt and command preview." in prompt_text
    assert "Approved goal from review" in prompt_text
    assert "Approved exact scope" in prompt_text
    assert "Approved non goals" in prompt_text
    assert "src/allowed.py" in prompt_text
    assert "python -m pytest tests/test_codex_execution.py" in prompt_text


def test_diagnostics_include_execution_summary_but_not_secret_output(tmp_path):
    def secret_runner(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 0, stdout="api_key=SECRET_VALUE", stderr="password=HIDDEN")

    conn, _, _, _, _, plans, execution, _ = stack(tmp_path, runner=secret_runner)
    connector_root = tmp_path / "connectors"
    (connector_root / "placeholders").mkdir(parents=True)
    plan = approved_plan(plans)
    result = execution.execute_plan(plan["plan_id"])

    exported = DiagnosticExporter(conn, tmp_path, tmp_path / "logs", connector_root).export()
    text = json.dumps(exported)

    assert exported["codexExecutions"][0]["execution_id"] == result["execution_id"]
    assert "SECRET_VALUE" not in text
    assert "HIDDEN" not in text


def test_diagnostics_redacts_raw_security_event_fields(tmp_path):
    conn, _, runtime, _, _, _, execution, _ = stack(tmp_path)
    connector_root = tmp_path / "connectors"
    (connector_root / "placeholders").mkdir(parents=True)
    runtime.validate(
        __import__("jarvis_core.runtime", fromlist=["ActionRequest"]).ActionRequest(
            "coding_agent",
            "codex.execute",
            "https://example.test/path?token=SECRET_TOKEN C:/Users/russe/private/.env",
            "task-1",
            "codex_tool",
            "high",
        )
    )

    exported = DiagnosticExporter(conn, tmp_path, tmp_path / "logs", connector_root).export()
    text = json.dumps(exported)

    assert exported["configSummary"]["secretValuesExported"] is False
    assert "SECRET_TOKEN" not in text
    assert "example.test/path" not in text
    assert "private/.env" not in text
    assert "target" not in exported["recentSecurityEvents"][0]


def test_no_generic_codex_or_shell_endpoints_exist():
    from jarvis_core.app import app

    routes = {route.path for route in app.routes}
    assert "/codex/plans/{plan_id}/execute" in routes
    assert "/codex/run" not in routes
    assert "/codex/exec" not in routes
    assert "/shell" not in routes
