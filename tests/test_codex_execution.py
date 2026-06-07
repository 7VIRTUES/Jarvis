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
from jarvis_core.post_execution_review import safe_check_argv
from jarvis_core.project_registry import ProjectRegistry
from jarvis_core.runtime import SafeActionRuntime


def symlink_or_skip(link, target):
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable in this environment: {exc}")


def stack(tmp_path, runner=None, detector=None, check_runner=None):
    conn = init_db(tmp_path / "jarvis.sqlite")
    logger = JsonlLogger(tmp_path / "logs")
    events = EventBus(conn, logger)
    runtime = SafeActionRuntime(logger, conn, events)
    approvals = ApprovalQueue(conn, events)
    projects = ProjectRegistry(conn, tmp_path)
    plans = CodexPlanService(conn, events, runtime, approvals, projects)
    execution = CodexExecutionService(conn, events, runtime, approvals, projects, plans, detector or (lambda: "codex"), runner or success_runner, check_runner or success_check_runner)
    project = tmp_path / "sample"
    project.mkdir()
    subprocess.run(["git", "init"], cwd=project, shell=False, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "jarvis@example.invalid"], cwd=project, shell=False, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Jarvis Tests"], cwd=project, shell=False, check=True, capture_output=True, text=True)
    projects.add_project("sample", project)
    return conn, events, runtime, approvals, projects, plans, execution, project


def success_runner(argv, **kwargs):
    assert kwargs["shell"] is False
    assert argv[0:2] == ["codex", "exec"]
    return subprocess.CompletedProcess(argv, 0, stdout="completed", stderr="")


def repair_success_runner(argv, **kwargs):
    assert kwargs["shell"] is False
    assert argv[0:2] == ["codex", "exec"]
    return subprocess.CompletedProcess(argv, 0, stdout="repair completed" if "repair-attempt" in argv[-1] else "completed", stderr="")


def success_check_runner(argv, **kwargs):
    assert kwargs["shell"] is False
    assert argv[0].startswith("npm")
    return subprocess.CompletedProcess(argv, 0, stdout=f"{argv[-1]} ok", stderr="")


def dependency_change_runner(argv, **kwargs):
    project = __import__("pathlib").Path(kwargs["cwd"])
    (project / "package.json").write_text('{"scripts":{"test":"node test.js"},"dependencies":{"x":"1.0.0"}}\n', encoding="utf-8")
    return subprocess.CompletedProcess(argv, 0, stdout="changed dependency file", stderr="")


def write_package_scripts(project, scripts):
    script_json = ",".join(f'"{name}":"{command}"' for name, command in scripts.items())
    (project / "package.json").write_text(f'{{"scripts":{{{script_json}}}}}\n', encoding="utf-8")
    subprocess.run(["git", "add", "package.json"], cwd=project, shell=False, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "package scripts"], cwd=project, shell=False, check=True, capture_output=True, text=True)


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


def test_acquire_lock_allows_same_task_reentry(tmp_path):
    conn, _, _, _, _, _, execution, _ = stack(tmp_path)
    conn.execute(
        "insert into project_locks (project_name, task_id, lock_type, locked_at) values (?, ?, ?, ?)",
        ("sample", "task-1", "write", "now"),
    )
    conn.commit()

    assert execution._acquire_lock("sample", "task-1") is True
    assert conn.execute("select count(*) from project_locks where project_name = ?", ("sample",)).fetchone()[0] == 1


def test_acquire_lock_blocks_different_task(tmp_path):
    conn, _, _, _, _, _, execution, _ = stack(tmp_path)
    conn.execute(
        "insert into project_locks (project_name, task_id, lock_type, locked_at) values (?, ?, ?, ?)",
        ("sample", "task-1", "write", "now"),
    )
    conn.commit()

    assert execution._acquire_lock("sample", "task-2") is False
    assert conn.execute("select task_id from project_locks where project_name = ?", ("sample",)).fetchone()[0] == "task-1"


def test_release_lock_does_not_remove_different_task_lock(tmp_path):
    conn, _, _, _, _, _, execution, _ = stack(tmp_path)
    conn.execute(
        "insert into project_locks (project_name, task_id, lock_type, locked_at) values (?, ?, ?, ?)",
        ("sample", "task-2", "write", "now"),
    )
    conn.commit()

    execution._release_lock("sample", "task-1")

    assert conn.execute("select task_id from project_locks where project_name = ?", ("sample",)).fetchone()[0] == "task-2"


def test_execution_reenters_same_task_lock_without_releasing_it(tmp_path):
    conn, _, _, _, _, plans, execution, _ = stack(tmp_path)
    plan = approved_plan(plans)
    conn.execute(
        "insert into project_locks (project_name, task_id, lock_type, locked_at) values (?, ?, ?, ?)",
        ("sample", plan["task_id"], "write", "now"),
    )
    conn.commit()

    result = execution.execute_plan(plan["plan_id"])

    assert result["status"] == "succeeded"
    row = conn.execute("select task_id, lock_type from project_locks where project_name = ?", ("sample",)).fetchone()
    assert row == (plan["task_id"], "write")


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
    assert result["check_results"]["status"] == "skipped"
    assert (project / ".jarvis" / "prompts" / "current-task.md").exists()


def test_successful_check_plan_executes_all_checks_in_order_and_stores_results(tmp_path):
    calls = []

    def check_runner(argv, **kwargs):
        calls.append(list(argv))
        return subprocess.CompletedProcess(argv, 0, stdout=f"{argv[-1]} completed", stderr="")

    conn, _, runtime, _, _, plans, execution, project = stack(tmp_path, check_runner=check_runner)
    write_package_scripts(project, {"build": "vite build", "lint": "eslint .", "test": "node test.js", "typecheck": "tsc --noEmit"})
    plan = approved_plan(plans)

    result = execution.execute_plan(plan["plan_id"])
    stored = execution.get_execution(result["execution_id"])
    command_receipts = [receipt for receipt in runtime.list_receipts(plan["task_id"]) if receipt["action_type"] == "command"]

    assert result["status"] == "succeeded"
    assert [call[-1] for call in calls] == ["typecheck", "lint", "test", "build"]
    assert result["check_results"]["status"] == "succeeded"
    assert [check["name"] for check in result["check_results"]["checks"]] == ["typecheck", "lint", "test", "build"]
    assert stored["check_results"] == result["check_results"]
    assert len(command_receipts) == 4
    assert conn.execute("select check_results from codex_executions where execution_id = ?", (result["execution_id"],)).fetchone()[0] != "{}"
    assert result["repair_results"]["status"] == "skipped"


def test_failed_first_check_stops_later_checks(tmp_path):
    calls = []

    def check_runner(argv, **kwargs):
        calls.append(list(argv))
        return subprocess.CompletedProcess(argv, 1, stdout="typecheck failed", stderr="")

    _, _, runtime, _, _, plans, execution, project = stack(tmp_path, check_runner=check_runner)
    write_package_scripts(project, {"typecheck": "tsc --noEmit", "lint": "eslint .", "test": "node test.js"})
    plan = approved_plan(plans)

    result = execution.execute_plan(plan["plan_id"])

    assert result["status"] == "failed"
    assert [call[-1] for call in calls] == ["typecheck", "typecheck"]
    assert result["check_results"]["status"] == "failed"
    assert result["check_results"]["checks"][0]["status"] == "failed"
    assert result["repair_results"]["reason"] == "same check failure repeated"
    assert len([receipt for receipt in runtime.list_receipts(plan["task_id"]) if receipt["action_type"] == "command"]) == 2


def test_failed_check_triggers_repair_and_passing_repair_stops_loop(tmp_path):
    check_calls = []

    def check_runner(argv, **kwargs):
        check_calls.append(list(argv))
        return subprocess.CompletedProcess(argv, 1 if len(check_calls) == 1 else 0, stdout=f"check call {len(check_calls)}", stderr="")

    conn, _, _, _, _, plans, execution, project = stack(tmp_path, runner=repair_success_runner, check_runner=check_runner)
    write_package_scripts(project, {"test": "node test.js"})
    plan = approved_plan(plans)

    result = execution.execute_plan(plan["plan_id"])
    stored = execution.get_execution(result["execution_id"])

    assert result["status"] == "succeeded"
    assert len(check_calls) == 2
    assert result["repair_results"]["status"] == "succeeded"
    assert len(result["repair_results"]["attempts"]) == 1
    assert result["repair_results"]["attempts"][0]["check_results"]["status"] == "succeeded"
    assert stored["repair_results"] == result["repair_results"]
    assert conn.execute("select repair_results from codex_executions where execution_id = ?", (result["execution_id"],)).fetchone()[0] != "{}"


def test_repair_loop_enforces_max_two_attempts(tmp_path):
    check_calls = []

    def check_runner(argv, **kwargs):
        check_calls.append(list(argv))
        return subprocess.CompletedProcess(argv, 1, stdout=f"failure {len(check_calls)}", stderr="")

    _, _, _, _, _, plans, execution, project = stack(tmp_path, runner=repair_success_runner, check_runner=check_runner)
    write_package_scripts(project, {"test": "node test.js"})
    plan = approved_plan(plans)

    result = execution.execute_plan(plan["plan_id"])

    assert result["status"] == "failed"
    assert result["repair_results"]["status"] == "stopped"
    assert result["repair_results"]["reason"] == "max repair attempts reached"
    assert len(result["repair_results"]["attempts"]) == 2
    assert len(check_calls) == 3


def test_repair_loop_respects_max_codex_runs_per_task(tmp_path):
    def check_runner(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 1, stdout="check failed", stderr="")

    conn, _, _, _, _, plans, execution, project = stack(tmp_path, runner=repair_success_runner, check_runner=check_runner)
    write_package_scripts(project, {"test": "node test.js"})
    plan = approved_plan(plans)
    for index in range(2):
        conn.execute(
            "insert into codex_executions (execution_id, plan_id, task_id, project_name, status, started_at, codex_command_preview) values (?, ?, ?, ?, ?, ?, ?)",
            (f"prior-exec-{index}", plan["plan_id"], plan["task_id"], plan["project_name"], "succeeded", "now", "codex exec"),
        )
    conn.commit()

    result = execution.execute_plan(plan["plan_id"])

    assert result["status"] == "failed"
    assert result["repair_results"]["status"] == "stopped"
    assert result["repair_results"]["reason"] == "maxCodexRunsPerTask reached before repair"
    assert result["repair_results"]["attempts"] == []


def test_same_failure_repeated_stops_repair_loop(tmp_path):
    def check_runner(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 1, stdout="same failure", stderr="")

    _, _, _, _, _, plans, execution, project = stack(tmp_path, runner=repair_success_runner, check_runner=check_runner)
    write_package_scripts(project, {"test": "node test.js"})
    plan = approved_plan(plans)

    result = execution.execute_plan(plan["plan_id"])

    assert result["status"] == "failed"
    assert result["repair_results"]["status"] == "stopped"
    assert result["repair_results"]["reason"] == "same check failure repeated"
    assert len(result["repair_results"]["attempts"]) == 1


def test_repair_codex_failure_stops_loop(tmp_path):
    def runner(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 1 if "repair-attempt" in argv[-1] else 0, stdout="repair failed", stderr="")

    def check_runner(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 1, stdout="check failed", stderr="")

    _, _, _, _, _, plans, execution, project = stack(tmp_path, runner=runner, check_runner=check_runner)
    write_package_scripts(project, {"test": "node test.js"})
    plan = approved_plan(plans)

    result = execution.execute_plan(plan["plan_id"])

    assert result["status"] == "failed"
    assert result["repair_results"]["status"] == "failed"
    assert result["repair_results"]["reason"] == "Codex repair run failed"
    assert result["repair_results"]["attempts"][0]["codex_return_code"] == 1


def test_post_repair_protected_file_review_stops_loop(tmp_path):
    def runner(argv, **kwargs):
        if "repair-attempt" in argv[-1]:
            project = __import__("pathlib").Path(kwargs["cwd"])
            (project / ".env").write_text("SECRET_VALUE_SHOULD_NOT_READ=1\n", encoding="utf-8")
        return subprocess.CompletedProcess(argv, 0, stdout="ok", stderr="")

    def check_runner(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 1, stdout="check failed", stderr="")

    _, _, _, _, _, plans, execution, project = stack(tmp_path, runner=runner, check_runner=check_runner)
    write_package_scripts(project, {"test": "node test.js"})
    plan = approved_plan(plans)

    result = execution.execute_plan(plan["plan_id"])
    attempt = result["repair_results"]["attempts"][0]

    assert result["status"] == "failed"
    assert result["repair_results"]["status"] == "review_required"
    assert "protected file" in result["repair_results"]["reason"]
    assert attempt["post_review"]["protectedFilesChanged"] == [".env"]
    assert "SECRET_VALUE_SHOULD_NOT_READ" not in json.dumps(result["repair_results"])


def test_post_repair_dependency_file_review_stops_loop(tmp_path):
    def runner(argv, **kwargs):
        if "repair-attempt" in argv[-1]:
            project = __import__("pathlib").Path(kwargs["cwd"])
            (project / "package.json").write_text('{"scripts":{"test":"node test.js"},"dependencies":{"x":"1.0.0"}}\n', encoding="utf-8")
        return subprocess.CompletedProcess(argv, 0, stdout="ok", stderr="")

    def check_runner(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 1, stdout="check failed", stderr="")

    _, _, _, _, _, plans, execution, project = stack(tmp_path, runner=runner, check_runner=check_runner)
    write_package_scripts(project, {"test": "node test.js"})
    plan = approved_plan(plans)

    result = execution.execute_plan(plan["plan_id"])

    assert result["status"] == "failed"
    assert result["repair_results"]["status"] == "review_required"
    assert "dependency/package" in result["repair_results"]["reason"]
    assert result["repair_results"]["attempts"][0]["post_review"]["dependencyFilesChanged"] == ["package.json"]


def test_post_repair_risk_budget_failure_stops_loop(tmp_path):
    def runner(argv, **kwargs):
        if "repair-attempt" in argv[-1]:
            project = __import__("pathlib").Path(kwargs["cwd"])
            for index in range(12):
                (project / f"repair-{index}.txt").write_text("changed\n", encoding="utf-8")
        return subprocess.CompletedProcess(argv, 0, stdout="ok", stderr="")

    def check_runner(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 1, stdout="check failed", stderr="")

    _, _, _, _, _, plans, execution, project = stack(tmp_path, runner=runner, check_runner=check_runner)
    write_package_scripts(project, {"test": "node test.js"})
    plan = approved_plan(plans)

    result = execution.execute_plan(plan["plan_id"])

    assert result["status"] == "failed"
    assert result["repair_results"]["status"] == "review_required"
    assert "changedFiles=" in result["repair_results"]["reason"]


def test_repair_prompt_includes_failed_check_context_with_redacted_output(tmp_path):
    def check_runner(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 1, stdout="api_key=SECRET_VALUE", stderr="password=HIDDEN")

    _, _, _, _, _, plans, execution, project = stack(tmp_path, runner=repair_success_runner, check_runner=check_runner)
    write_package_scripts(project, {"test": "node test.js"})
    plan = plans.create_plan(
        CodexPlanInput(
            task_id="task-1",
            project_name="sample",
            task_goal="Approved repair prompt goal",
            exact_scope="Only repair the failing test.",
            non_goals="No unrelated work.",
            risk_plan={"changedFiles": 1},
        )
    )
    approved = plans.approve_for_future_execution(plan["plan_id"], "local_user", "approved")

    execution.execute_plan(approved["plan_id"])
    prompt_text = (project / ".jarvis" / "prompts" / "repair-attempt-1.md").read_text(encoding="utf-8")

    assert "Approved repair prompt goal" in prompt_text
    assert "Name: test" in prompt_text
    assert "Command: npm run test" in prompt_text
    assert "api_key=[REDACTED]" in prompt_text
    assert "password=[REDACTED]" in prompt_text
    assert "SECRET_VALUE" not in prompt_text
    assert "HIDDEN" not in prompt_text
    assert "Fix only the failed check above" in prompt_text


def test_failed_middle_check_stops_later_checks(tmp_path):
    calls = []

    def check_runner(argv, **kwargs):
        calls.append(list(argv))
        return subprocess.CompletedProcess(argv, 1 if argv[-1] == "lint" else 0, stdout=f"{argv[-1]} result", stderr="")

    _, _, _, _, _, plans, execution, project = stack(tmp_path, check_runner=check_runner)
    write_package_scripts(project, {"typecheck": "tsc --noEmit", "lint": "eslint .", "test": "node test.js"})
    plan = approved_plan(plans)

    result = execution.execute_plan(plan["plan_id"])

    assert result["status"] == "failed"
    assert [call[-1] for call in calls] == ["typecheck", "lint", "typecheck", "lint"]
    assert [check["status"] for check in result["check_results"]["checks"]] == ["succeeded", "failed"]
    assert result["repair_results"]["reason"] == "same check failure repeated"


def test_no_scripts_creates_skipped_check_result(tmp_path):
    calls = []
    _, _, _, _, _, plans, execution, _ = stack(tmp_path, check_runner=lambda argv, **kwargs: calls.append(list(argv)))
    plan = approved_plan(plans)

    result = execution.execute_plan(plan["plan_id"])

    assert result["status"] == "succeeded"
    assert result["check_results"] == {"status": "skipped", "reason": "no detected package scripts for safe checks", "checks": []}
    assert calls == []


def test_controlled_codex_flow_stops_before_checks_when_post_review_fails(tmp_path):
    calls = []
    _, events, _, _, _, plans, execution, project = stack(tmp_path, runner=dependency_change_runner, check_runner=lambda argv, **kwargs: calls.append(list(argv)))
    plan = approved_plan(plans)

    result = execution.execute_plan(plan["plan_id"])
    event_types = [event["event_type"] for event in events.list_events(plan["task_id"])]

    assert result["status"] == "blocked"
    assert "dependency/package" in result["blocked_reason"]
    assert result["post_review"]["checksMayProceed"] is False
    assert result["check_plan"]["checks"] == [{"name": "test", "command": "npm run test", "argv": safe_check_argv("test"), "source": "package.json scripts"}]
    assert result["check_results"]["status"] == "skipped"
    assert result["repair_results"]["status"] == "skipped"
    assert "codex.post_review_blocked" in event_types
    assert "codex.check_plan_generated" not in event_types
    assert calls == []
    assert (project / "package.json").exists()


def test_unsafe_check_plan_entry_is_blocked_and_not_executed(tmp_path, monkeypatch):
    calls = []
    _, _, runtime, _, _, plans, execution, project = stack(tmp_path, check_runner=lambda argv, **kwargs: calls.append(list(argv)))
    write_package_scripts(project, {"test": "node test.js"})
    plan = approved_plan(plans)

    monkeypatch.setattr(
        "jarvis_core.codex_execution.review_post_codex_diff",
        lambda project_path, package_scripts: {
            "requiresUserReview": False,
            "checksMayProceed": True,
            "reasons": ["post-Codex diff is within policy"],
            "checkPlan": {"checks": [{"name": "test", "command": "git push", "argv": ["git", "push"], "source": "package.json scripts"}], "reason": "planned detected package scripts only"},
        },
    )

    result = execution.execute_plan(plan["plan_id"])
    command_receipts = [receipt for receipt in runtime.list_receipts(plan["task_id"]) if receipt["action_type"] == "command"]

    assert result["status"] == "blocked"
    assert result["check_results"]["status"] == "blocked"
    assert "blocked command pattern" in result["check_results"]["reason"]
    assert calls == []
    assert command_receipts[-1]["blocked"] is True


def test_non_detected_check_script_is_blocked_and_not_executed(tmp_path, monkeypatch):
    calls = []
    _, _, runtime, _, _, plans, execution, project = stack(tmp_path, check_runner=lambda argv, **kwargs: calls.append(list(argv)))
    write_package_scripts(project, {"test": "node test.js"})
    plan = approved_plan(plans)

    monkeypatch.setattr(
        "jarvis_core.codex_execution.review_post_codex_diff",
        lambda project_path, package_scripts: {
            "requiresUserReview": False,
            "checksMayProceed": True,
            "reasons": ["post-Codex diff is within policy"],
            "checkPlan": {"checks": [{"name": "start", "command": "npm run start", "argv": safe_check_argv("start"), "source": "package.json scripts"}], "reason": "planned detected package scripts only"},
        },
    )

    result = execution.execute_plan(plan["plan_id"])
    command_receipts = [receipt for receipt in runtime.list_receipts(plan["task_id"]) if receipt["action_type"] == "command"]

    assert result["status"] == "blocked"
    assert result["check_results"]["reason"] == "check plan entry does not match a detected safe script"
    assert calls == []
    assert command_receipts[-1]["approved"] is True


def test_check_output_is_redacted_and_truncated(tmp_path):
    def check_runner(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 0, stdout=f"api_key=SECRET_VALUE {'x' * 2500}", stderr="password=HIDDEN")

    _, _, _, _, _, plans, execution, project = stack(tmp_path, check_runner=check_runner)
    write_package_scripts(project, {"test": "node test.js"})
    plan = approved_plan(plans)

    result = execution.execute_plan(plan["plan_id"])
    check = result["check_results"]["checks"][0]

    assert result["status"] == "succeeded"
    assert "SECRET_VALUE" not in check["stdout_excerpt"]
    assert "HIDDEN" not in check["stderr_excerpt"]
    assert len(check["stdout_excerpt"]) <= 2100


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
    assert "Post-Codex review findings" in prompt_text
    assert "Safe check results" in prompt_text
    assert "Repair attempts/results" in prompt_text


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
