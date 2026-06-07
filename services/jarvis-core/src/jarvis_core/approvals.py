from __future__ import annotations

import sqlite3
from typing import Any
from uuid import uuid4

from .events import EventBus
from .permissions import check_action
from .time_utils import utc_now


APPROVAL_STATUSES = {"pending", "approved", "rejected", "expired", "canceled"}


class ApprovalQueue:
    def __init__(self, conn: sqlite3.Connection, events: EventBus):
        self.conn = conn
        self.events = events

    def request_approval(
        self,
        task_id: str | None,
        action_type: str,
        project_name: str | None,
        risk_level: str,
        reason: str,
        action_id: str | None = None,
    ) -> dict[str, Any]:
        approval = {
            "approval_id": str(uuid4()),
            "task_id": task_id,
            "action_id": action_id,
            "action_type": action_type,
            "project_name": project_name,
            "risk_level": risk_level,
            "reason": reason,
            "status": "pending",
            "requested_at": utc_now(),
            "resolved_at": None,
            "resolved_by": None,
            "resolution_note": None,
        }
        self.conn.execute(
            """
            insert into approvals (
              approval_id, task_id, action_id, action_type, project_name, risk_level,
              reason, status, requested_at, resolved_at, resolved_by, resolution_note
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            tuple(approval.values()),
        )
        self.conn.commit()
        self.events.emit("approval.requested", task_id, {"approval_id": approval["approval_id"], "reason": reason})
        return approval

    def list_approvals(self) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "select approval_id, task_id, action_id, action_type, project_name, risk_level, reason, status, requested_at, resolved_at, resolved_by, resolution_note from approvals order by requested_at"
        ).fetchall()
        return [self._row(row) for row in rows]

    def get_approval(self, approval_id: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            "select approval_id, task_id, action_id, action_type, project_name, risk_level, reason, status, requested_at, resolved_at, resolved_by, resolution_note from approvals where approval_id = ?",
            (approval_id,),
        ).fetchone()
        return self._row(row) if row else None

    def approve(self, approval_id: str, resolved_by: str, note: str | None = None) -> dict[str, Any]:
        approval = self.get_approval(approval_id)
        if not approval:
            raise KeyError("approval not found")
        if approval["status"] != "pending":
            return approval
        if approval["action_type"] == "risk_budget":
            return self._resolve(approval_id, "approved", resolved_by, note)
        policy = check_action(str(approval["action_type"]))
        if policy.status == "blocked":
            return self._resolve(approval_id, "rejected", resolved_by, "approval cannot override hard-blocked actions")
        return self._resolve(approval_id, "approved", resolved_by, note)

    def reject(self, approval_id: str, resolved_by: str, note: str | None = None) -> dict[str, Any]:
        approval = self.get_approval(approval_id)
        if not approval:
            raise KeyError("approval not found")
        if approval["status"] != "pending":
            return approval
        return self._resolve(approval_id, "rejected", resolved_by, note)

    def _resolve(self, approval_id: str, status: str, resolved_by: str, note: str | None) -> dict[str, Any]:
        if status not in {"approved", "rejected"}:
            raise ValueError("approval resolution must be approved or rejected")
        existing = self.get_approval(approval_id)
        if not existing:
            raise KeyError("approval not found")
        if existing["status"] != "pending":
            return existing
        resolved_at = utc_now()
        self.conn.execute(
            "update approvals set status = ?, resolved_at = ?, resolved_by = ?, resolution_note = ? where approval_id = ?",
            (status, resolved_at, resolved_by, note, approval_id),
        )
        self.conn.commit()
        event_type = "approval.approved" if status == "approved" else "approval.rejected"
        self.events.emit(event_type, existing["task_id"], {"approval_id": approval_id, "note": note})
        return self.get_approval(approval_id)  # type: ignore[return-value]

    def _row(self, row: tuple[Any, ...]) -> dict[str, Any]:
        return {
            "approval_id": row[0],
            "task_id": row[1],
            "action_id": row[2],
            "action_type": row[3],
            "project_name": row[4],
            "risk_level": row[5],
            "reason": row[6],
            "status": row[7],
            "requested_at": row[8],
            "resolved_at": row[9],
            "resolved_by": row[10],
            "resolution_note": row[11],
        }
