from __future__ import annotations

import sqlite3
from typing import Any
from uuid import uuid4

from .approvals import ApprovalQueue
from .events import EventBus
from .risk import validate_risk_budget
from .runtime import ActionRequest, SafeActionRuntime
from .time_utils import utc_now


TASK_STATUSES = {"queued", "running", "waiting_for_approval", "succeeded", "failed", "blocked", "canceled"}
TERMINAL_STATUSES = {"succeeded", "failed", "blocked", "canceled"}
READ_ONLY_TASK_TYPES = {"inspect", "report", "plan"}


class TaskQueue:
    def __init__(self, conn: sqlite3.Connection, events: EventBus, runtime: SafeActionRuntime, approvals: ApprovalQueue):
        self.conn = conn
        self.events = events
        self.runtime = runtime
        self.approvals = approvals

    def create_task(
        self,
        project_name: str,
        agent_id: str,
        task_type: str,
        autonomy_level: str = "supervised",
        dry_run: bool = True,
        write_capable: bool | None = None,
        proposed_actions: list[dict[str, Any]] | None = None,
        risk_plan: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        task_id = str(uuid4())
        write_capable = self._is_write_capable(task_type, write_capable)
        now = utc_now()
        if write_capable and self._locked(project_name):
            self._insert_task(task_id, project_name, agent_id, task_type, "blocked", autonomy_level, dry_run, write_capable, now, now, now, None, "project is locked")
            self.events.emit("task.blocked", task_id, {"project_name": project_name, "reason": "project is locked"})
            return self.get_task(task_id)  # type: ignore[return-value]

        self._insert_task(task_id, project_name, agent_id, task_type, "queued", autonomy_level, dry_run, write_capable, now, None, None, None, None)
        if write_capable:
            self._acquire_lock(project_name, task_id)
        self.events.emit("task.created", task_id, {"project_name": project_name, "dry_run": dry_run, "write_capable": write_capable})

        if dry_run:
            self._run_dry_plan(task_id, project_name, agent_id, proposed_actions or [], risk_plan or {})
        return self.get_task(task_id)  # type: ignore[return-value]

    def list_tasks(self) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "select task_id, project_name, agent_id, task_type, status, autonomy_level, dry_run, write_capable, created_at, started_at, finished_at, summary, error from tasks order by created_at"
        ).fetchall()
        return [self._row(row) for row in rows]

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            "select task_id, project_name, agent_id, task_type, status, autonomy_level, dry_run, write_capable, created_at, started_at, finished_at, summary, error from tasks where task_id = ?",
            (task_id,),
        ).fetchone()
        return self._row(row) if row else None

    def cancel_task(self, task_id: str) -> dict[str, Any]:
        task = self.get_task(task_id)
        if not task:
            raise KeyError("task not found")
        if task["status"] not in TERMINAL_STATUSES:
            self._set_status(task_id, "canceled", finished=True, error="cancel requested")
            self.events.emit("task.canceled", task_id, {"reason": "cancel requested"})
            self._release_lock(task["project_name"], task_id)
        return self.get_task(task_id)  # type: ignore[return-value]

    def _run_dry_plan(self, task_id: str, project_name: str, agent_id: str, proposed_actions: list[dict[str, Any]], risk_plan: dict[str, Any]) -> None:
        self._set_status(task_id, "running", started=True)
        self.events.emit("task.started", task_id, {"mode": "dry_run"})
        budget = validate_risk_budget(risk_plan)
        if budget.approval_required:
            self.approvals.request_approval(task_id, "risk_budget", project_name, budget.risk_level, budget.reason)
            self._set_status(task_id, "waiting_for_approval", summary=budget.reason)
            self.events.emit("task.waiting_for_approval", task_id, {"reason": budget.reason})
            return

        actions = proposed_actions or [{"tool_id": "report_tool", "action_type": "inspect_project", "target": project_name, "risk_level": "low"}]
        blocked = False
        approval_required = False
        for action in actions:
            self.events.emit("action.proposed", task_id, action)
            receipt = self.runtime.validate(
                ActionRequest(
                    task_id=task_id,
                    agent_id=agent_id,
                    tool_id=str(action.get("tool_id", "policy_engine")),
                    action_type=str(action.get("action_type", "")),
                    target=action.get("target"),
                    risk_level=str(action.get("risk_level", "low")),
                )
            )
            blocked = blocked or receipt.blocked
            approval_required = approval_required or receipt.approval_required
            if receipt.approval_required:
                self.approvals.request_approval(task_id, receipt.action_type, project_name, receipt.risk_level, receipt.reason, receipt.receipt_id)

        if blocked:
            self._set_status(task_id, "blocked", finished=True, error="one or more dry-run actions were blocked")
            self.events.emit("task.blocked", task_id, {"reason": "one or more dry-run actions were blocked"})
        elif approval_required:
            self._set_status(task_id, "waiting_for_approval", summary="one or more actions require approval")
            self.events.emit("task.waiting_for_approval", task_id, {"reason": "one or more actions require approval"})
        else:
            self._set_status(task_id, "succeeded", finished=True, summary="dry-run plan validated without execution")
            self.events.emit("task.succeeded", task_id, {"summary": "dry-run plan validated without execution"})

        task = self.get_task(task_id)
        if task and task["status"] in TERMINAL_STATUSES:
            self._release_lock(project_name, task_id)

    def _insert_task(
        self,
        task_id: str,
        project_name: str,
        agent_id: str,
        task_type: str,
        status: str,
        autonomy_level: str,
        dry_run: bool,
        write_capable: bool,
        created_at: str,
        started_at: str | None,
        finished_at: str | None,
        summary: str | None,
        error: str | None,
    ) -> None:
        self.conn.execute(
            """
            insert into tasks (
              task_id, project_name, agent_id, task_type, status, autonomy_level, dry_run,
              write_capable, created_at, started_at, finished_at, summary, error
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (task_id, project_name, agent_id, task_type, status, autonomy_level, int(dry_run), int(write_capable), created_at, started_at, finished_at, summary, error),
        )
        self.conn.commit()

    def _set_status(self, task_id: str, status: str, started: bool = False, finished: bool = False, summary: str | None = None, error: str | None = None) -> None:
        if status not in TASK_STATUSES:
            raise ValueError(f"unsupported task status: {status}")
        fields = ["status = ?"]
        values: list[Any] = [status]
        if started:
            fields.append("started_at = ?")
            values.append(utc_now())
        if finished:
            fields.append("finished_at = ?")
            values.append(utc_now())
        if summary is not None:
            fields.append("summary = ?")
            values.append(summary)
        if error is not None:
            fields.append("error = ?")
            values.append(error)
        values.append(task_id)
        self.conn.execute(f"update tasks set {', '.join(fields)} where task_id = ?", values)
        self.conn.commit()

    def _is_write_capable(self, task_type: str, explicit: bool | None) -> bool:
        inferred = task_type not in READ_ONLY_TASK_TYPES
        return inferred or explicit is True

    def _locked(self, project_name: str) -> bool:
        return self.conn.execute("select 1 from project_locks where project_name = ?", (project_name,)).fetchone() is not None

    def _acquire_lock(self, project_name: str, task_id: str) -> None:
        self.conn.execute(
            "insert into project_locks (project_name, task_id, lock_type, locked_at) values (?, ?, ?, ?)",
            (project_name, task_id, "write", utc_now()),
        )
        self.conn.commit()

    def _release_lock(self, project_name: str, task_id: str) -> None:
        self.conn.execute("delete from project_locks where project_name = ? and task_id = ?", (project_name, task_id))
        self.conn.commit()

    def _row(self, row: tuple[Any, ...]) -> dict[str, Any]:
        return {
            "task_id": row[0],
            "project_name": row[1],
            "agent_id": row[2],
            "task_type": row[3],
            "status": row[4],
            "autonomy_level": row[5],
            "dry_run": bool(row[6]),
            "write_capable": bool(row[7]),
            "created_at": row[8],
            "started_at": row[9],
            "finished_at": row[10],
            "summary": row[11],
            "error": row[12],
        }
