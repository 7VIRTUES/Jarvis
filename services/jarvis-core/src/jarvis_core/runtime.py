from __future__ import annotations

import sqlite3
from dataclasses import asdict, dataclass
from uuid import uuid4

from .audit import JsonlLogger
from .events import EventBus
from .permissions import PolicyCheckResult, check_action
from .time_utils import utc_now


@dataclass(frozen=True)
class ActionRequest:
    agent_id: str
    action_type: str
    target: str | None = None
    task_id: str | None = None
    tool_id: str = "policy_engine"
    risk_level: str = "low"


@dataclass(frozen=True)
class ActionReceipt:
    receipt_id: str
    task_id: str | None
    agent_id: str
    tool_id: str
    action_type: str
    target: str | None
    approved: bool
    blocked: bool
    approval_required: bool
    risk_level: str
    started_at: str
    finished_at: str
    result: str | None
    reason: str


class SafeActionRuntime:
    def __init__(self, logger: JsonlLogger, conn: sqlite3.Connection | None = None, events: EventBus | None = None):
        self.logger = logger
        self.conn = conn
        self.events = events

    def validate(self, request: ActionRequest) -> ActionReceipt:
        started_at = utc_now()
        result: PolicyCheckResult = check_action(request.action_type, request.target)
        receipt = ActionReceipt(
            receipt_id=str(uuid4()),
            task_id=request.task_id,
            agent_id=request.agent_id,
            tool_id=request.tool_id,
            action_type=request.action_type,
            target=request.target,
            approved=result.allowed,
            blocked=result.status == "blocked",
            approval_required=result.status == "approval_required",
            risk_level=request.risk_level,
            started_at=started_at,
            finished_at=utc_now(),
            result=result.status,
            reason=result.reason,
        )
        self.logger.append("actions", asdict(receipt))
        self._store_receipt(receipt)
        if self.events:
            event_type = "action.blocked" if receipt.blocked else "action.receipt_created"
            self.events.emit(event_type, request.task_id, {"receipt_id": receipt.receipt_id, "action_type": receipt.action_type})
        if receipt.blocked:
            self.logger.append("security", {"eventType": "action_blocked", **asdict(receipt)})
            if self.events:
                self.events.emit("security.blocked", request.task_id, {"receipt_id": receipt.receipt_id, "reason": receipt.reason})
        elif receipt.approval_required and self.events:
            self.events.emit("approval.requested", request.task_id, {"receipt_id": receipt.receipt_id, "reason": receipt.reason})
        return receipt

    def _store_receipt(self, receipt: ActionReceipt) -> None:
        if not self.conn:
            return
        self.conn.execute(
            """
            insert into action_receipts (
              receipt_id, task_id, agent_id, tool_id, action_type, target, approved, blocked,
              approval_required, risk_level, started_at, finished_at, result, reason
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                receipt.receipt_id,
                receipt.task_id,
                receipt.agent_id,
                receipt.tool_id,
                receipt.action_type,
                receipt.target,
                int(receipt.approved),
                int(receipt.blocked),
                int(receipt.approval_required),
                receipt.risk_level,
                receipt.started_at,
                receipt.finished_at,
                receipt.result,
                receipt.reason,
            ),
        )
        self.conn.commit()

    def get_receipt(self, receipt_id: str) -> dict[str, object] | None:
        if not self.conn:
            return None
        row = self.conn.execute(
            "select receipt_id, task_id, agent_id, tool_id, action_type, target, approved, blocked, approval_required, risk_level, started_at, finished_at, result, reason from action_receipts where receipt_id = ?",
            (receipt_id,),
        ).fetchone()
        if not row:
            return None
        return {
            "receipt_id": row[0],
            "task_id": row[1],
            "agent_id": row[2],
            "tool_id": row[3],
            "action_type": row[4],
            "target": row[5],
            "approved": bool(row[6]),
            "blocked": bool(row[7]),
            "approval_required": bool(row[8]),
            "risk_level": row[9],
            "started_at": row[10],
            "finished_at": row[11],
            "result": row[12],
            "reason": row[13],
        }

    def finalize_execution_receipt(
        self,
        receipt_id: str,
        result_status: str,
        execution_note: str | None = None,
        task_id: str | None = None,
    ) -> dict[str, object]:
        if result_status not in {"executed_read_only", "execution_failed"}:
            raise ValueError(f"Invalid execution receipt finalization status: {result_status}")
        receipt = self.get_receipt(receipt_id)
        if not receipt:
            raise KeyError(f"Receipt not found: {receipt_id}")
        if task_id and receipt["task_id"] != task_id:
            raise ValueError("Task ID mismatch for execution receipt")
        if receipt["blocked"]:
            raise PermissionError("Blocked receipts cannot be finalized as executed")
        if receipt["approval_required"] and not receipt["approved"]:
            raise PermissionError("Unresolved approval-required receipts cannot be finalized as executed")

        finished_at = utc_now()
        reason = str(receipt["reason"])
        if execution_note:
            reason = f"{reason} | {execution_note}"

        if self.conn:
            self.conn.execute(
                "update action_receipts set result = ?, finished_at = ?, reason = ? where receipt_id = ?",
                (result_status, finished_at, reason, receipt_id),
            )
            self.conn.commit()

        updated_receipt = self.get_receipt(receipt_id) or receipt
        self.logger.append("actions", {"eventType": "receipt_finalized", **updated_receipt})
        if self.events:
            event_type = "action.executed" if result_status == "executed_read_only" else "action.execution_failed"
            self.events.emit(
                event_type,
                str(receipt["task_id"]) if receipt["task_id"] else None,
                {
                    "receipt_id": receipt_id,
                    "action_type": receipt["action_type"],
                    "result": result_status,
                },
            )
        return updated_receipt

    def list_receipts(self, task_id: str | None = None) -> list[dict[str, object]]:
        if not self.conn:
            return []
        if task_id:
            rows = self.conn.execute(
                "select receipt_id, task_id, agent_id, tool_id, action_type, target, approved, blocked, approval_required, risk_level, started_at, finished_at, result, reason from action_receipts where task_id = ? order by started_at",
                (task_id,),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "select receipt_id, task_id, agent_id, tool_id, action_type, target, approved, blocked, approval_required, risk_level, started_at, finished_at, result, reason from action_receipts order by started_at"
            ).fetchall()
        return [
            {
                "receipt_id": row[0],
                "task_id": row[1],
                "agent_id": row[2],
                "tool_id": row[3],
                "action_type": row[4],
                "target": row[5],
                "approved": bool(row[6]),
                "blocked": bool(row[7]),
                "approval_required": bool(row[8]),
                "risk_level": row[9],
                "started_at": row[10],
                "finished_at": row[11],
                "result": row[12],
                "reason": row[13],
            }
            for row in rows
        ]



