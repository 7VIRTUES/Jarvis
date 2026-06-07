from __future__ import annotations

import re
import shutil
import sqlite3
import subprocess
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from .approvals import ApprovalQueue
from .codex_constants import ALLOWED_SANDBOX_MODE
from .codex_paths import validate_codex_project_paths
from .codex_plans import CodexPlanService
from .events import EventBus
from .permissions import check_action, check_command
from .project_registry import ProjectRegistry
from .risk import DEFAULT_RISK_BUDGET
from .runtime import ActionRequest, SafeActionRuntime
from .time_utils import utc_now


EXECUTION_STATUSES = {"blocked", "running", "succeeded", "failed", "canceled"}
MAX_EXCERPT_CHARS = 2000


class CodexExecutionService:
    def __init__(
        self,
        conn: sqlite3.Connection,
        events: EventBus,
        runtime: SafeActionRuntime,
        approvals: ApprovalQueue,
        projects: ProjectRegistry,
        plans: CodexPlanService,
        codex_detector: Callable[[], str | None] | None = None,
        runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
    ):
        self.conn = conn
        self.events = events
        self.runtime = runtime
        self.approvals = approvals
        self.projects = projects
        self.plans = plans
        self.codex_detector = codex_detector or (lambda: shutil.which("codex"))
        self.runner = runner or subprocess.run

    def execute_plan(self, plan_id: str) -> dict[str, Any]:
        execution_id = str(uuid4())
        started_at = utc_now()
        plan = self.plans.get_plan(plan_id)
        task_id = str(plan["task_id"]) if plan else ""
        project_name = str(plan["project_name"]) if plan else ""
        self.events.emit("codex.execution_requested", task_id or None, {"plan_id": plan_id, "execution_id": execution_id})

        validation = self._validate_plan(plan)
        if validation:
            receipt = self.runtime.validate(ActionRequest("coding_agent", "codex.execute", validation, task_id or None, "codex_tool", "high"))
            return self._record_execution(execution_id, plan_id, task_id, project_name, "blocked", started_at, utc_now(), "{}", None, "", "", None, receipt.receipt_id, validation, None)

        assert plan is not None
        project_path = Path(str(plan["project_path"])).resolve()
        prompt_path = Path(str(plan["prompt_path"])).resolve()
        output_path = Path(str(plan["output_path"])).resolve()
        argv = list(plan["command_preview"]["argv"])
        policy = check_action("codex.execute_approved_plan", plan_id)
        command_policy = check_command(" ".join(argv))
        if policy.status == "blocked" or command_policy.status == "blocked":
            reason = policy.reason if policy.status == "blocked" else command_policy.reason
            receipt = self.runtime.validate(ActionRequest(str(plan["agent_id"]), "codex.execute", reason, str(plan["task_id"]), str(plan["tool_id"]), str(plan["risk_level"])))
            return self._record_execution(execution_id, plan_id, str(plan["task_id"]), str(plan["project_name"]), "blocked", started_at, utc_now(), plan["command_preview"]["preview"], None, "", "", str(output_path), receipt.receipt_id, reason, None)

        if not self._acquire_lock(str(plan["project_name"]), str(plan["task_id"])):
            receipt = self.runtime.validate(ActionRequest(str(plan["agent_id"]), "codex.execute", "project is locked", str(plan["task_id"]), str(plan["tool_id"]), str(plan["risk_level"])))
            return self._record_execution(execution_id, plan_id, str(plan["task_id"]), str(plan["project_name"]), "blocked", started_at, utc_now(), plan["command_preview"]["preview"], None, "", "", str(output_path), receipt.receipt_id, "project is locked", None)

        receipt_id = None
        try:
            prompt_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            prompt_path.write_text(self._execution_prompt(plan), encoding="utf-8")
            self.events.emit("codex.prompt_prepared", str(plan["task_id"]), {"plan_id": plan_id, "prompt_path": str(prompt_path)})
            receipt = self.runtime.validate(ActionRequest(str(plan["agent_id"]), "codex.execute_approved_plan", plan_id, str(plan["task_id"]), str(plan["tool_id"]), str(plan["risk_level"])))
            receipt_id = receipt.receipt_id
            self.events.emit("codex.execution_receipt_created", str(plan["task_id"]), {"plan_id": plan_id, "execution_id": execution_id, "receipt_id": receipt_id})
            self._insert_running(execution_id, plan, started_at, receipt_id)
            self.events.emit("codex.execution_started", str(plan["task_id"]), {"plan_id": plan_id, "execution_id": execution_id})
            completed = self.runner(
                argv,
                cwd=str(project_path),
                shell=False,
                capture_output=True,
                text=True,
                timeout=3600,
            )
            finished_at = utc_now()
            status = "succeeded" if completed.returncode == 0 else "failed"
            stdout_excerpt = redact_output(completed.stdout)
            stderr_excerpt = redact_output(completed.stderr)
            self._finish_execution(execution_id, status, finished_at, completed.returncode, stdout_excerpt, stderr_excerpt, None)
            diff_summary = self._inspect_git_diff(project_path)
            event_type = "codex.execution_succeeded" if status == "succeeded" else "codex.execution_failed"
            self.events.emit(event_type, str(plan["task_id"]), {"plan_id": plan_id, "execution_id": execution_id, "exit_code": completed.returncode, "diff": diff_summary})
            return self.get_execution(execution_id)  # type: ignore[return-value]
        except Exception as exc:  # noqa: BLE001 - store safe error summary for local diagnostics.
            finished_at = utc_now()
            self._finish_execution(execution_id, "failed", finished_at, None, "", "", redact_output(str(exc)))
            self.events.emit("codex.execution_failed", str(plan["task_id"]), {"plan_id": plan_id, "execution_id": execution_id, "error": type(exc).__name__})
            return self.get_execution(execution_id)  # type: ignore[return-value]
        finally:
            self._release_lock(str(plan["project_name"]), str(plan["task_id"]))

    def get_execution(self, execution_id: str) -> dict[str, Any] | None:
        row = self.conn.execute(self._select_sql() + " where execution_id = ?", (execution_id,)).fetchone()
        return self._row(row) if row else None

    def list_executions(self) -> list[dict[str, Any]]:
        rows = self.conn.execute(self._select_sql() + " order by started_at").fetchall()
        return [self._row(row) for row in rows]

    def _validate_plan(self, plan: dict[str, Any] | None) -> str | None:
        if not plan:
            return "codex plan not found"
        if plan["status"] != "approved_for_future_execution":
            return "codex plan must be approved_for_future_execution"
        approval_id = plan.get("approval_id")
        approval = self.approvals.get_approval(str(approval_id)) if approval_id else None
        if not approval or approval["status"] != "approved":
            return "approved approval record is required"
        project = self.projects.get_project(str(plan["project_name"]))
        if not project:
            return "registered project is required"
        registered_path = Path(str(project["path"])).resolve()
        project_path = Path(str(plan["project_path"])).resolve()
        if not project_path.is_relative_to(registered_path):
            return "project path must stay inside registered project"
        validation, _, prompt_path, output_path = validate_codex_project_paths(
            registered_path,
            str(Path(str(plan["prompt_path"])).relative_to(registered_path)) if Path(str(plan["prompt_path"])).is_absolute() and Path(str(plan["prompt_path"])).is_relative_to(registered_path) else str(plan["prompt_path"]),
            str(Path(str(plan["output_path"])).relative_to(registered_path)) if Path(str(plan["output_path"])).is_absolute() and Path(str(plan["output_path"])).is_relative_to(registered_path) else str(plan["output_path"]),
            str(plan["sandbox_mode"]),
        )
        if validation:
            return validation
        assert prompt_path is not None and output_path is not None
        if plan["sandbox_mode"] != ALLOWED_SANDBOX_MODE:
            return "sandbox mode must be workspace-write"
        rebuilt = self.plans.build_command_preview(project_path, prompt_path, output_path, str(plan["sandbox_mode"]))
        if plan["command_preview"] != rebuilt:
            return "approved command preview does not match rebuilt template"
        if self._codex_runs_for_task(str(plan["task_id"])) >= int(DEFAULT_RISK_BUDGET["maxCodexRunsPerTask"]):
            return "maxCodexRunsPerTask exceeded"
        if not self.codex_detector():
            return "official Codex CLI was not detected"
        return None

    def _insert_running(self, execution_id: str, plan: dict[str, Any], started_at: str, receipt_id: str) -> None:
        self.conn.execute(
            """
            insert into codex_executions (
              execution_id, plan_id, task_id, project_name, status, started_at,
              codex_command_preview, output_path, receipt_id
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (execution_id, plan["plan_id"], plan["task_id"], plan["project_name"], "running", started_at, plan["command_preview"]["preview"], plan["output_path"], receipt_id),
        )
        self.conn.commit()

    def _record_execution(
        self,
        execution_id: str,
        plan_id: str,
        task_id: str,
        project_name: str,
        status: str,
        started_at: str,
        finished_at: str | None,
        command_preview: str,
        exit_code: int | None,
        stdout_excerpt: str,
        stderr_excerpt: str,
        output_path: str | None,
        receipt_id: str | None,
        blocked_reason: str | None,
        error: str | None,
    ) -> dict[str, Any]:
        self.conn.execute(
            """
            insert into codex_executions (
              execution_id, plan_id, task_id, project_name, status, started_at, finished_at,
              codex_command_preview, exit_code, stdout_excerpt, stderr_excerpt, output_path,
              receipt_id, blocked_reason, error
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (execution_id, plan_id, task_id, project_name, status, started_at, finished_at, command_preview, exit_code, stdout_excerpt, stderr_excerpt, output_path, receipt_id, blocked_reason, error),
        )
        self.conn.commit()
        self.events.emit("codex.execution_blocked", task_id or None, {"plan_id": plan_id, "execution_id": execution_id, "reason": blocked_reason}) if status == "blocked" else None
        return self.get_execution(execution_id)  # type: ignore[return-value]

    def _finish_execution(self, execution_id: str, status: str, finished_at: str, exit_code: int | None, stdout_excerpt: str, stderr_excerpt: str, error: str | None) -> None:
        self.conn.execute(
            "update codex_executions set status = ?, finished_at = ?, exit_code = ?, stdout_excerpt = ?, stderr_excerpt = ?, error = ? where execution_id = ?",
            (status, finished_at, exit_code, stdout_excerpt, stderr_excerpt, error, execution_id),
        )
        self.conn.commit()

    def _codex_runs_for_task(self, task_id: str) -> int:
        return int(
            self.conn.execute(
                "select count(*) from codex_executions where task_id = ? and status in ('running', 'succeeded', 'failed')",
                (task_id,),
            ).fetchone()[0]
        )

    def _acquire_lock(self, project_name: str, task_id: str) -> bool:
        try:
            self.conn.execute(
                "insert into project_locks (project_name, task_id, lock_type, locked_at) values (?, ?, ?, ?)",
                (project_name, task_id, "codex-execution", utc_now()),
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def _release_lock(self, project_name: str, task_id: str) -> None:
        self.conn.execute("delete from project_locks where project_name = ? and task_id = ?", (project_name, task_id))
        self.conn.commit()

    def _execution_prompt(self, plan: dict[str, Any]) -> str:
        approved_prompt = str(plan.get("prompt_content") or "")
        if approved_prompt:
            return "\n".join(
                [
                    "# Jarvis Controlled Codex Execution",
                    "",
                    f"Plan ID: {plan['plan_id']}",
                    "Execute only the approved plan represented by this prompt and command preview.",
                    "",
                    "## Approved Plan Prompt",
                    approved_prompt.rstrip(),
                    "",
                    "## Execution Boundary",
                    "Do not drift from the approved plan. Do not expand scope, read secrets, run destructive commands, push, merge, reset hard, send email, post publicly, make purchases, automate browsers, use paid APIs, or access future connectors.",
                ]
            ) + "\n"
        return "\n".join(
            [
                "# Jarvis Controlled Codex Execution",
                "",
                f"Plan ID: {plan['plan_id']}",
                f"Project: {plan['project_name']}",
                "",
                "## Exact Scope",
                "Execute only the approved Codex plan represented by this prompt and command preview.",
                "",
                "## Non-Goals",
                "Do not run unrelated repair loops, review loops, browser automation, external connectors, or paid APIs.",
                "",
                "## Safety Boundaries",
                "Do not read secrets, push, merge, reset hard, delete files destructively, send email, post publicly, make purchases, or access browser sessions.",
                "",
                "## Allowed Files/Folders",
                "Stay inside the registered project workspace and the scope described by the approved plan.",
                "",
                "## Blocked Actions",
                "git push; git merge; git reset --hard; rm -rf; del /s; format; diskpart; reg delete; secret reads; browser sessions; email; public posting; payments; connector execution.",
                "",
                "## Tests",
                "Plan checks only unless explicitly available through a later Jarvis check-runner slice.",
                "",
                "## Final Report Requirements",
                "Summarize changed files, commands run by Codex, tests attempted, blocked actions, risks, and recommended next task.",
            ]
        ) + "\n"

    def _inspect_git_diff(self, project_path: Path) -> dict[str, str | None]:
        return {
            "status": self._git_read(project_path, ["status", "--short"]),
            "diffStat": self._git_read(project_path, ["diff", "--stat"]),
        }

    def _git_read(self, project_path: Path, args: list[str]) -> str | None:
        try:
            result = subprocess.run(["git", *args], cwd=str(project_path), shell=False, capture_output=True, text=True, timeout=10)
        except (OSError, subprocess.TimeoutExpired):
            return None
        if result.returncode != 0:
            return None
        return redact_output(result.stdout)

    def _select_sql(self) -> str:
        return (
            "select execution_id, plan_id, task_id, project_name, status, started_at, finished_at, "
            "codex_command_preview, exit_code, stdout_excerpt, stderr_excerpt, output_path, receipt_id, blocked_reason, error from codex_executions"
        )

    def _row(self, row: tuple[Any, ...]) -> dict[str, Any]:
        return {
            "execution_id": row[0],
            "plan_id": row[1],
            "task_id": row[2],
            "project_name": row[3],
            "status": row[4],
            "started_at": row[5],
            "finished_at": row[6],
            "codex_command_preview": row[7],
            "exit_code": row[8],
            "stdout_excerpt": row[9],
            "stderr_excerpt": row[10],
            "output_path": row[11],
            "receipt_id": row[12],
            "blocked_reason": row[13],
            "error": row[14],
        }


def redact_output(value: str | None) -> str:
    if not value:
        return ""
    redacted = value[:MAX_EXCERPT_CHARS]
    redacted = re.sub(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?[^'\"\s]+", r"\1=[REDACTED]", redacted)
    redacted = re.sub(
        r"-----BEGIN [A-Z ]+PRIVATE KEY-----.*?-----END [A-Z ]+PRIVATE KEY-----",
        "[REDACTED_PRIVATE_KEY]",
        redacted,
        flags=re.DOTALL,
    )
    return redacted
