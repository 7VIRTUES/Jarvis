from __future__ import annotations

import re
import sqlite3
from datetime import datetime, timezone
from typing import Any
from urllib.parse import unquote


AGENT_ID = "activity_timeline_agent"
AGENT_NAME = "Recent Activity / Audit Trail"
MODE = "local_activity_metadata_only"
DEFAULT_LIMIT = 25
MAX_LIMIT = 100
SUMMARY_CHAR_LIMIT = 300
SECRET_KEYWORDS = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "api_key",
    "secret_key",
    "access_token",
    "refresh_token",
    "private_key",
    "client_secret",
    "password",
    "passwd",
    "token",
]
ASSIGNMENT_VALUE_RE = re.compile(
    r"(?P<key>\b(?:" + "|".join(re.escape(k) for k in SECRET_KEYWORDS) + r")\b\s*(?:=|:)\s*)(?P<quote>['\"]?)(?P<value>[^'\"\s,#;]+)",
    re.IGNORECASE,
)
TOKEN_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{12,}\b", re.IGNORECASE), "Bearer <redacted>"),
    (re.compile(r"\bghp_[A-Za-z0-9_]{12,}\b"), "<redacted-token>"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{12,}\b"), "<redacted-token>"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b"), "<redacted-token>"),
    (re.compile(r"\b(?=[A-Za-z0-9_]{32,}\b)(?=[A-Za-z0-9_]*\d)[A-Za-z0-9_]{32,}\b"), "<redacted-token>"),
]
PRIVATE_PATH_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"C:\\Users\\[^\\\s\"')]+(?:\\[^\\\s\"')]+)*", re.IGNORECASE), "<redacted-user-path>"),
    (re.compile("C:" + r"/Users/[^/\s\"')]+(?:/[^/\s\"')]+)*", re.IGNORECASE), "<redacted-user-path>"),
    (re.compile(r"OneDrive\s+-\s+[^\\/\"\r\n]+", re.IGNORECASE), "<redacted-org-path>"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\b"), "<redacted-email>"),
    (re.compile(r"/home/[^/\s\"')]+(?:/[^\s\"')]+)*", re.IGNORECASE), "<redacted-user-path>"),
    (re.compile(r"/Users/[^/\s\"')]+(?:/[^\s\"')]+)*", re.IGNORECASE), "<redacted-user-path>"),
]


class ActivityTimelineService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def timeline(self, limit: int = DEFAULT_LIMIT) -> dict[str, Any]:
        bounded_limit = self._bounded_limit(limit)
        items = sorted(self._all_items(), key=lambda item: str(item["createdAt"]), reverse=True)[:bounded_limit]
        return {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "agentId": AGENT_ID,
            "agentName": AGENT_NAME,
            "mode": MODE,
            "requestedLimit": limit,
            "limit": bounded_limit,
            "totalRecentItems": len(items),
            "countsByType": self._counts(items, "itemType"),
            "countsByStatus": self._counts(items, "status"),
            "items": items,
            "localOnly": True,
            "rawLogsRead": False,
            "rawCommandOutputIncluded": False,
            "protectedContentIncluded": False,
            "mutation": False,
            "externalServices": False,
            "uploads": False,
            "certification": False,
        }

    def item_detail(self, item_id: str) -> dict[str, Any]:
        safe_id = unquote(item_id)
        if "/" in safe_id or "\\" in safe_id or safe_id in {"", ".", ".."} or ".." in safe_id:
            raise PermissionError("item_id must be a safe recent activity item id")
        for item in self._all_items():
            if item["itemId"] == safe_id:
                detail = dict(item)
                detail["detailType"] = "safe_metadata_only"
                detail["rawPayloadIncluded"] = False
                detail["rawCommandOutputIncluded"] = False
                return detail
        raise FileNotFoundError(f"activity item not found: {safe_id}")

    def dashboard_summary(self) -> dict[str, Any]:
        summary = self.timeline(10)
        return {
            "agentId": AGENT_ID,
            "agentName": AGENT_NAME,
            "mode": MODE,
            "recentActivityCount": summary["totalRecentItems"],
            "countsByType": summary["countsByType"],
            "countsByStatus": summary["countsByStatus"],
            "recentItems": summary["items"],
            "localOnly": True,
            "rawLogsRead": False,
            "rawCommandOutputIncluded": False,
            "mutation": False,
            "externalServices": False,
            "uploads": False,
            "certification": False,
        }

    def _all_items(self) -> list[dict[str, Any]]:
        return self._task_items() + self._event_items() + self._approval_items() + self._security_items() + self._receipt_items()

    def _task_items(self) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            select task_id, project_name, agent_id, task_type, status, dry_run, write_capable,
                   created_at, started_at, finished_at, summary, error
            from tasks
            order by created_at desc
            limit ?
            """,
            (MAX_LIMIT,),
        ).fetchall()
        return [
            {
                "itemId": f"task:{row[0]}",
                "sourceId": row[0],
                "itemType": "task",
                "title": self._redact_text(f"Task {row[3]}"),
                "status": row[4],
                "createdAt": row[7],
                "summary": self._bounded_summary(row[10] or row[11] or f"{row[2]} task for {row[1]}"),
                "metadata": {
                    "projectName": self._redact_text(str(row[1])),
                    "agentId": self._redact_text(str(row[2])),
                    "taskType": self._redact_text(str(row[3])),
                    "dryRun": bool(row[5]),
                    "writeCapable": bool(row[6]),
                    "startedAt": row[8],
                    "finishedAt": row[9],
                },
                "safeDetailEndpoint": f"/activity/timeline/{self._encode_item_id('task', row[0])}",
            }
            for row in rows
        ]

    def _event_items(self) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "select event_id, task_id, event_type, created_at from events order by created_at desc limit ?",
            (MAX_LIMIT,),
        ).fetchall()
        return [
            {
                "itemId": f"event:{row[0]}",
                "sourceId": row[0],
                "itemType": "event",
                "title": self._redact_text(f"Event {row[2]}"),
                "status": row[2],
                "createdAt": row[3],
                "summary": self._bounded_summary(f"Local event metadata recorded for {row[2]}."),
                "metadata": {"taskId": row[1], "eventType": row[2], "payloadIncluded": False},
                "safeDetailEndpoint": f"/activity/timeline/{self._encode_item_id('event', row[0])}",
            }
            for row in rows
        ]

    def _approval_items(self) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            select approval_id, task_id, action_type, project_name, risk_level, reason, status, requested_at, resolved_at
            from approvals
            order by requested_at desc
            limit ?
            """,
            (MAX_LIMIT,),
        ).fetchall()
        return [
            {
                "itemId": f"approval:{row[0]}",
                "sourceId": row[0],
                "itemType": "approval",
                "title": self._redact_text(f"Approval {row[2]}"),
                "status": row[6],
                "createdAt": row[7],
                "summary": self._bounded_summary(row[5]),
                "metadata": {
                    "taskId": row[1],
                    "actionType": self._redact_text(str(row[2])),
                    "projectName": self._redact_text(str(row[3] or "")),
                    "riskLevel": row[4],
                    "resolvedAt": row[8],
                },
                "safeDetailEndpoint": f"/activity/timeline/{self._encode_item_id('approval', row[0])}",
            }
            for row in rows
        ]

    def _security_items(self) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "select id, event_type, detail, created_at from security_events order by created_at desc limit ?",
            (MAX_LIMIT,),
        ).fetchall()
        return [
            {
                "itemId": f"security:{row[0]}",
                "sourceId": str(row[0]),
                "itemType": "security",
                "title": self._redact_text(f"Security note {row[1]}"),
                "status": row[1],
                "createdAt": row[3],
                "summary": self._bounded_summary(row[2]),
                "metadata": {"eventType": self._redact_text(str(row[1]))},
                "safeDetailEndpoint": f"/activity/timeline/{self._encode_item_id('security', row[0])}",
            }
            for row in rows
        ]

    def _receipt_items(self) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            select receipt_id, task_id, agent_id, tool_id, action_type, approved, blocked,
                   approval_required, risk_level, started_at, finished_at, reason
            from action_receipts
            order by started_at desc
            limit ?
            """,
            (MAX_LIMIT,),
        ).fetchall()
        return [
            {
                "itemId": f"receipt:{row[0]}",
                "sourceId": row[0],
                "itemType": "receipt",
                "title": self._redact_text(f"Action receipt {row[4]}"),
                "status": self._receipt_status(bool(row[5]), bool(row[6]), bool(row[7])),
                "createdAt": row[9],
                "summary": self._bounded_summary(row[11]),
                "metadata": {
                    "taskId": row[1],
                    "agentId": self._redact_text(str(row[2])),
                    "toolId": self._redact_text(str(row[3])),
                    "actionType": self._redact_text(str(row[4])),
                    "riskLevel": row[8],
                    "finishedAt": row[10],
                    "resultIncluded": False,
                },
                "safeDetailEndpoint": f"/activity/timeline/{self._encode_item_id('receipt', row[0])}",
            }
            for row in rows
        ]

    def _bounded_limit(self, limit: int) -> int:
        try:
            requested = int(limit)
        except (TypeError, ValueError):
            requested = DEFAULT_LIMIT
        return max(1, min(requested, MAX_LIMIT))

    def _counts(self, items: list[dict[str, Any]], key: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in items:
            value = str(item.get(key) or "unknown")
            counts[value] = counts.get(value, 0) + 1
        return dict(sorted(counts.items()))

    def _receipt_status(self, approved: bool, blocked: bool, approval_required: bool) -> str:
        if blocked:
            return "blocked"
        if approval_required:
            return "approval_required"
        return "approved" if approved else "recorded"

    def _bounded_summary(self, value: Any) -> str:
        text = self._redact_text(str(value or "Safe local activity metadata recorded."))
        return text[:SUMMARY_CHAR_LIMIT]

    def _redact_text(self, text: str) -> str:
        redacted = ASSIGNMENT_VALUE_RE.sub(lambda match: f"{match.group('key')}{match.group('quote')}<redacted>", text)
        for pattern, replacement in TOKEN_PATTERNS:
            redacted = pattern.sub(replacement, redacted)
        for pattern, replacement in PRIVATE_PATH_PATTERNS:
            redacted = pattern.sub(replacement, redacted)
        if ".env" in redacted.lower() and ("=" in redacted or ":" in redacted):
            redacted = re.sub(r"(?im)^.*\.env.*(?:=|:).*$", "<redacted-env-like-line>", redacted)
        return " ".join(redacted.replace("\x00", "").split())

    def _encode_item_id(self, item_type: str, source_id: Any) -> str:
        return f"{item_type}:{source_id}"
