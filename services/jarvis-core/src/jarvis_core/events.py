from __future__ import annotations

import json
import sqlite3
from typing import Any
from uuid import uuid4

from .audit import JsonlLogger
from .time_utils import utc_now


EVENT_TYPES = {
    "task.created",
    "task.started",
    "task.blocked",
    "task.waiting_for_approval",
    "task.succeeded",
    "task.failed",
    "task.canceled",
    "action.proposed",
    "action.approved",
    "action.blocked",
    "action.receipt_created",
    "approval.requested",
    "approval.approved",
    "approval.rejected",
    "security.blocked",
    "codex.plan_created",
    "codex.plan_blocked",
    "codex.prompt_prepared",
    "codex.command_preview_created",
    "codex.approval_requested",
    "codex.approved_for_future_execution",
    "codex.rejected",
    "codex.canceled",
}


class EventBus:
    def __init__(self, conn: sqlite3.Connection, logger: JsonlLogger):
        self.conn = conn
        self.logger = logger

    def emit(self, event_type: str, task_id: str | None = None, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        if event_type not in EVENT_TYPES:
            raise ValueError(f"unsupported event type: {event_type}")
        event = {
            "event_id": str(uuid4()),
            "task_id": task_id,
            "event_type": event_type,
            "payload": payload or {},
            "created_at": utc_now(),
        }
        self.conn.execute(
            "insert into events (event_id, task_id, event_type, payload, created_at) values (?, ?, ?, ?, ?)",
            (event["event_id"], task_id, event_type, json.dumps(event["payload"], sort_keys=True), event["created_at"]),
        )
        self.conn.commit()
        self.logger.append("actions", {"eventType": event_type, "taskId": task_id, "payload": payload or {}})
        return event

    def list_events(self, task_id: str | None = None) -> list[dict[str, Any]]:
        if task_id:
            rows = self.conn.execute(
                "select event_id, task_id, event_type, payload, created_at from events where task_id = ? order by created_at",
                (task_id,),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "select event_id, task_id, event_type, payload, created_at from events order by created_at"
            ).fetchall()
        return [
            {
                "event_id": row[0],
                "task_id": row[1],
                "event_type": row[2],
                "payload": json.loads(row[3]),
                "created_at": row[4],
            }
            for row in rows
        ]
