import json
import subprocess

from jarvis_core.approvals import ApprovalQueue
from jarvis_core.audit import JsonlLogger
from jarvis_core.codex_execution import CodexExecutionService
from jarvis_core.codex_plans import CodexPlanInput, CodexPlanService
from jarvis_core.db import init_db
from jarvis_core.diagnostics import DiagnosticExporter
from jarvis_core.events import EventBus
from jarvis_core.project_registry import ProjectRegistry
from jarvis_core.runtime import SafeActionRuntime


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
    projects.add_project("sample", project)
    return conn, events, runtime, approvals, projects, plans, execution, project


def success_runner(argv, **kwargs):
    assert kwargs["shell"] is False
    assert argv[0:2] == ["codex", "exec"]
    return subprocess.CompletedProcess(argv, 0, stdout="completed", stderr="")


def approved_plan(plans):
    plan = plans.create_plan(
        CodexPlanInput(
            task_id="task-1",
            project_name="sample",
            task_goal="Safe execution test.",
            exact_scope="Only a mocked execution.",
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
    assert (project / ".jarvis" / "prompts" / "current-task.md").exists()


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


def test_no_generic_codex_or_shell_endpoints_exist():
    from jarvis_core.app import app

    routes = {route.path for route in app.routes}
    assert "/codex/plans/{plan_id}/execute" in routes
    assert "/codex/run" not in routes
    assert "/codex/exec" not in routes
    assert "/shell" not in routes
