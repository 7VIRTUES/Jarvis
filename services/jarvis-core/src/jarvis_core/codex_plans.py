from __future__ import annotations

import json
import shlex
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from .approvals import ApprovalQueue
from .events import EventBus
from .permissions import check_action, check_command, is_protected_path
from .project_registry import ProjectRegistry
from .risk import validate_risk_budget
from .runtime import ActionRequest, SafeActionRuntime
from .time_utils import utc_now


PLAN_MODES = {"plan_only", "approval_required"}
PLAN_STATUSES = {"planned", "waiting_for_approval", "approved_for_future_execution", "rejected", "blocked", "canceled"}
ALLOWED_SANDBOX_MODE = "workspace-write"
PROMPT_RELATIVE = Path(".jarvis") / "prompts" / "current-task.md"
OUTPUT_RELATIVE = Path(".jarvis") / "reports" / "latest-codex-output.md"
COMMAND_TEMPLATE = [
    "codex",
    "exec",
    "--cd",
    "{PROJECT_PATH}",
    "--sandbox",
    "workspace-write",
    "--ask-for-approval",
    "never",
    "--output-last-message",
    "{OUTPUT_PATH}",
    "Read {PROMPT_PATH} and complete the task exactly.",
]


@dataclass(frozen=True)
class CodexPlanInput:
    task_id: str
    project_name: str
    agent_id: str = "coding_agent"
    tool_id: str = "codex_tool"
    action_type: str = "codex.plan_execution"
    task_goal: str = ""
    exact_scope: str = ""
    non_goals: str = ""
    allowed_files: list[str] | None = None
    test_commands: list[str] | None = None
    risk_plan: dict[str, Any] | None = None
    sandbox_mode: str = ALLOWED_SANDBOX_MODE
    prompt_path: str = str(PROMPT_RELATIVE)
    output_path: str = str(OUTPUT_RELATIVE)


class CodexPlanService:
    def __init__(
        self,
        conn: sqlite3.Connection,
        events: EventBus,
        runtime: SafeActionRuntime,
        approvals: ApprovalQueue,
        projects: ProjectRegistry,
    ):
        self.conn = conn
        self.events = events
        self.runtime = runtime
        self.approvals = approvals
        self.projects = projects

    def create_plan(self, payload: CodexPlanInput) -> dict[str, Any]:
        now = utc_now()
        project = self.projects.get_project(payload.project_name)
        plan_id = str(uuid4())
        if not project:
            return self._blocked_plan(plan_id, payload, "", "", "", "registered project is required", now)

        project_path = Path(str(project["path"])).resolve()
        validation = self._validate_plan_paths(project_path, payload.prompt_path, payload.output_path, payload.sandbox_mode)
        risk = validate_risk_budget(payload.risk_plan)
        policy = check_action(payload.action_type)
        hard_block = self._hard_block_reason(payload)
        if validation or hard_block or policy.status == "blocked":
            reason = validation or hard_block or policy.reason
            return self._blocked_plan(plan_id, payload, str(project_path), payload.prompt_path, payload.output_path, reason, now)

        prompt = self.build_prompt(payload, project_path)
        preview = self.build_command_preview(project_path, project_path / payload.prompt_path, project_path / payload.output_path, payload.sandbox_mode)
        risk_reasons = [risk.reason]
        risk_level = risk.risk_level if risk.approval_required else "medium"
        status = "waiting_for_approval"
        mode = "approval_required"
        approval_required = True
        approval = self.approvals.request_approval(payload.task_id, payload.action_type, payload.project_name, risk_level, "; ".join(risk_reasons), plan_id)
        self._insert_plan(
            plan_id,
            payload,
            mode,
            status,
            str(project_path),
            str(project_path / payload.prompt_path),
            str(project_path / payload.output_path),
            json.dumps(COMMAND_TEMPLATE),
            json.dumps(preview),
            approval_required,
            approval["approval_id"],
            risk_level,
            risk_reasons,
            now,
        )
        self.runtime.validate(ActionRequest(payload.agent_id, "codex.prepare_prompt", str(project_path / payload.prompt_path), payload.task_id, payload.tool_id, risk_level))
        self.runtime.validate(ActionRequest(payload.agent_id, "codex.preview_command", payload.project_name, payload.task_id, payload.tool_id, risk_level))
        self.events.emit("codex.prompt_prepared", payload.task_id, {"plan_id": plan_id, "prompt_path": str(project_path / payload.prompt_path), "prompt_preview_length": len(prompt)})
        self.events.emit("codex.command_preview_created", payload.task_id, {"plan_id": plan_id})
        self.events.emit("codex.approval_requested", payload.task_id, {"plan_id": plan_id, "approval_id": approval["approval_id"]})
        self.events.emit("codex.plan_created", payload.task_id, {"plan_id": plan_id, "status": status})
        return self.get_plan(plan_id)  # type: ignore[return-value]

    def list_plans(self) -> list[dict[str, Any]]:
        rows = self.conn.execute(self._select_sql() + " order by created_at").fetchall()
        return [self._row(row) for row in rows]

    def get_plan(self, plan_id: str) -> dict[str, Any] | None:
        row = self.conn.execute(self._select_sql() + " where plan_id = ?", (plan_id,)).fetchone()
        return self._row(row) if row else None

    def cancel_plan(self, plan_id: str) -> dict[str, Any]:
        plan = self.get_plan(plan_id)
        if not plan:
            raise KeyError("codex plan not found")
        if plan["status"] not in {"approved_for_future_execution", "rejected", "blocked", "canceled"}:
            self._set_status(plan_id, "canceled")
            self.events.emit("codex.canceled", plan["task_id"], {"plan_id": plan_id})
        return self.get_plan(plan_id)  # type: ignore[return-value]

    def approve_for_future_execution(self, plan_id: str, resolved_by: str, note: str | None = None) -> dict[str, Any]:
        plan = self.get_plan(plan_id)
        if not plan:
            raise KeyError("codex plan not found")
        if plan["status"] != "waiting_for_approval":
            return plan
        if not plan["approval_id"]:
            self._set_status(plan_id, "blocked")
            return self.get_plan(plan_id)  # type: ignore[return-value]
        approval = self.approvals.approve(str(plan["approval_id"]), resolved_by, note)
        if approval["status"] == "approved":
            self._set_status(plan_id, "approved_for_future_execution")
            self.events.emit("codex.approved_for_future_execution", plan["task_id"], {"plan_id": plan_id, "approval_id": approval["approval_id"]})
        else:
            self._set_status(plan_id, "rejected")
            self.events.emit("codex.rejected", plan["task_id"], {"plan_id": plan_id, "approval_id": approval["approval_id"]})
        return self.get_plan(plan_id)  # type: ignore[return-value]

    def reject_plan(self, plan_id: str, resolved_by: str, note: str | None = None) -> dict[str, Any]:
        plan = self.get_plan(plan_id)
        if not plan:
            raise KeyError("codex plan not found")
        if plan["approval_id"]:
            self.approvals.reject(str(plan["approval_id"]), resolved_by, note)
        self._set_status(plan_id, "rejected")
        self.events.emit("codex.rejected", plan["task_id"], {"plan_id": plan_id})
        return self.get_plan(plan_id)  # type: ignore[return-value]

    def build_prompt(self, payload: CodexPlanInput, project_path: Path) -> str:
        return "\n".join(
            [
                "# Jarvis Codex Task Prompt",
                "",
                f"Project name: {payload.project_name}",
                f"Project path: {project_path}",
                "",
                "## Task Goal",
                payload.task_goal or "No goal provided.",
                "",
                "## Exact Scope",
                payload.exact_scope or "Stay within the requested task only.",
                "",
                "## Non-Goals",
                payload.non_goals or "Do not implement unrelated features.",
                "",
                "## Safety Boundaries",
                "Do not read secrets, run destructive commands, push, merge, reset hard, send email, post publicly, make purchases, use paid APIs, automate browsers, or access future connectors.",
                "",
                "## Allowed Files/Folders",
                "\n".join(f"- {item}" for item in (payload.allowed_files or ["."])) ,
                "",
                "## Blocked Actions",
                "git push; git merge; git reset --hard; rm -rf; del /s; format; diskpart; reg delete; secret reads; browser sessions; email; public posting; payments; connector execution.",
                "",
                "## Test Commands",
                "\n".join(f"- {item}" for item in (payload.test_commands or ["python -m pytest"])),
                "",
                "## Required Final Report Format",
                "Summary; Files created; Files changed; What each file did; Endpoints implemented or changed; Database/schema changes; Agents/tools/connectors changed; Safety boundaries enforced; Commands run; Command results; Tests added or changed; Test results; Blocked actions or safety decisions; Known risks; Whether safe to build on; Recommended next task.",
            ]
        ) + "\n"

    def build_command_preview(self, project_path: Path, prompt_path: Path, output_path: Path, sandbox_mode: str) -> dict[str, Any]:
        argv = [
            "codex",
            "exec",
            "--cd",
            str(project_path),
            "--sandbox",
            sandbox_mode,
            "--ask-for-approval",
            "never",
            "--output-last-message",
            str(output_path),
            f"Read {prompt_path} and complete the task exactly.",
        ]
        preview = " ".join(shlex.quote(part) for part in argv)
        policy = check_command(preview)
        if policy.status == "blocked":
            raise ValueError(policy.reason)
        return {"argv": argv, "preview": preview, "executed": False}

    def _validate_plan_paths(self, project_path: Path, prompt_path: str, output_path: str, sandbox_mode: str) -> str | None:
        if sandbox_mode != ALLOWED_SANDBOX_MODE:
            return "sandbox mode must be workspace-write"
        prompt = (project_path / prompt_path).resolve()
        output = (project_path / output_path).resolve()
        prompts_root = (project_path / ".jarvis" / "prompts").resolve()
        reports_root = (project_path / ".jarvis" / "reports").resolve()
        if not prompt.is_relative_to(prompts_root):
            return "prompt path must stay under .jarvis/prompts"
        if not output.is_relative_to(reports_root):
            return "output path must stay under .jarvis/reports"
        if is_protected_path(prompt) or is_protected_path(output):
            return "protected prompt or output paths are blocked"
        return None

    def _hard_block_reason(self, payload: CodexPlanInput) -> str | None:
        haystack = " ".join(
            [
                payload.task_goal,
                payload.exact_scope,
                payload.non_goals,
                " ".join(payload.allowed_files or []),
                " ".join(payload.test_commands or []),
            ]
        )
        policy = check_command(haystack or "python -m pytest")
        return policy.reason if policy.status == "blocked" else None

    def _blocked_plan(self, plan_id: str, payload: CodexPlanInput, project_path: str, prompt_path: str, output_path: str, reason: str, now: str) -> dict[str, Any]:
        self._insert_plan(plan_id, payload, "plan_only", "blocked", project_path, prompt_path, output_path, json.dumps(COMMAND_TEMPLATE), "{}", False, None, "high", [reason], now)
        self.runtime.validate(ActionRequest(payload.agent_id, payload.action_type, reason, payload.task_id, payload.tool_id, "high"))
        self.events.emit("codex.plan_blocked", payload.task_id, {"plan_id": plan_id, "reason": reason})
        return self.get_plan(plan_id)  # type: ignore[return-value]

    def _insert_plan(
        self,
        plan_id: str,
        payload: CodexPlanInput,
        mode: str,
        status: str,
        project_path: str,
        prompt_path: str,
        output_path: str,
        command_template: str,
        command_preview: str,
        approval_required: bool,
        approval_id: str | None,
        risk_level: str,
        risk_reasons: list[str],
        now: str,
    ) -> None:
        if mode not in PLAN_MODES or status not in PLAN_STATUSES:
            raise ValueError("invalid codex plan mode or status")
        self.conn.execute(
            """
            insert into codex_plans (
              plan_id, task_id, project_name, agent_id, tool_id, action_type, mode, status,
              project_path, prompt_path, output_path, command_template, command_preview,
              sandbox_mode, approval_required, approval_id, risk_level, risk_reasons,
              created_at, updated_at
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                plan_id,
                payload.task_id,
                payload.project_name,
                payload.agent_id,
                payload.tool_id,
                payload.action_type,
                mode,
                status,
                project_path,
                prompt_path,
                output_path,
                command_template,
                command_preview,
                payload.sandbox_mode,
                int(approval_required),
                approval_id,
                risk_level,
                json.dumps(risk_reasons),
                now,
                now,
            ),
        )
        self.conn.commit()

    def _set_status(self, plan_id: str, status: str) -> None:
        if status not in PLAN_STATUSES:
            raise ValueError("invalid codex plan status")
        self.conn.execute("update codex_plans set status = ?, updated_at = ? where plan_id = ?", (status, utc_now(), plan_id))
        self.conn.commit()

    def _select_sql(self) -> str:
        return (
            "select plan_id, task_id, project_name, agent_id, tool_id, action_type, mode, status, "
            "project_path, prompt_path, output_path, command_template, command_preview, sandbox_mode, "
            "approval_required, approval_id, risk_level, risk_reasons, created_at, updated_at from codex_plans"
        )

    def _row(self, row: tuple[Any, ...]) -> dict[str, Any]:
        return {
            "plan_id": row[0],
            "task_id": row[1],
            "project_name": row[2],
            "agent_id": row[3],
            "tool_id": row[4],
            "action_type": row[5],
            "mode": row[6],
            "status": row[7],
            "project_path": row[8],
            "prompt_path": row[9],
            "output_path": row[10],
            "command_template": json.loads(row[11]),
            "command_preview": json.loads(row[12]) if row[12] else {},
            "sandbox_mode": row[13],
            "approval_required": bool(row[14]),
            "approval_id": row[15],
            "risk_level": row[16],
            "risk_reasons": json.loads(row[17]),
            "created_at": row[18],
            "updated_at": row[19],
        }

