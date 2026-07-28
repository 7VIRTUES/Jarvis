from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import uuid4

from .events import EventBus
from .time_utils import utc_now


MEMORY_TYPES = frozenset(
    {
        "preference",
        "personal_fact",
        "goal",
        "constraint",
        "project_fact",
        "decision",
        "routine",
        "terminology",
        "agent_instruction",
    }
)
MEMORY_STATUSES = frozenset({"pending", "approved", "disabled", "rejected"})
SCOPE_TYPES = frozenset({"global", "project", "agent"})
CONFIDENCE_VALUES = frozenset({"low", "medium", "high"})
SENSITIVITY_VALUES = frozenset({"standard", "sensitive"})
SOURCE_TYPES = frozenset({"manual", "agent_proposal", "feedback_proposal", "migration"})

MAX_CONTENT_LENGTH = 4000
MAX_REASON_LENGTH = 1000
MAX_QUERY_LENGTH = 200
DEFAULT_LIST_LIMIT = 50
MAX_LIST_LIMIT = 200

_MEMORY_COLUMNS = (
    "memory_id",
    "memory_type",
    "content",
    "status",
    "scope_type",
    "scope_value",
    "source_type",
    "source_agent_id",
    "source_reference",
    "proposal_reason",
    "confidence",
    "sensitivity",
    "expires_at",
    "created_at",
    "updated_at",
    "approved_at",
    "approved_by",
    "last_confirmed_at",
    "disabled_at",
    "rejected_at",
    "rejected_by",
    "rejection_reason",
    "content_hash",
)
_SELECT_MEMORY = ", ".join(_MEMORY_COLUMNS)
_EDITABLE_FIELDS = frozenset(
    {
        "memory_type",
        "content",
        "scope_type",
        "scope_value",
        "source_type",
        "source_agent_id",
        "source_reference",
        "proposal_reason",
        "confidence",
        "sensitivity",
        "expires_at",
    }
)
_SUBSTANTIVE_FIELDS = frozenset(
    {
        "memory_type",
        "content",
        "scope_type",
        "scope_value",
        "source_type",
        "source_agent_id",
        "source_reference",
        "proposal_reason",
        "sensitivity",
        "expires_at",
    }
)
_ACTOR_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{1,100}$")
_PEM_PRIVATE_KEY_PATTERN = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----",
    re.IGNORECASE,
)
_ASSIGNMENT_SECRET_PATTERN = re.compile(
    r"(?im)^\s*(?:password|passwd|pwd|api[_ -]?key|access[_ -]?token|refresh[_ -]?token|"
    r"client[_ -]?secret|private[_ -]?key|session[_ -]?token)\s*=\s*[\"']?\S+"
)
_LABELED_SECRET_PATTERN = re.compile(
    r"(?im)^\s*(?:password|passwd|api[_ -]?key|access[_ -]?token|refresh[_ -]?token|"
    r"client[_ -]?secret|private[_ -]?key|session[_ -]?token)\s*:\s*[\"']?[A-Za-z0-9_+/=.-]{12,}"
)
_COOKIE_DUMP_PATTERN = re.compile(
    r"(?im)^\s*(?:cookie|set-cookie|sessionid|session[_ -]?cookie)\s*[:=]\s*\S{12,}"
)
_BEARER_JWT_PATTERN = re.compile(
    r"(?i)(?:authorization|auth|token|bearer)[^\r\n]{0,30}\beyJ[A-Za-z0-9_-]{8,}\."
    r"[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"
)


class MemoryValidationError(ValueError):
    pass


class MemorySecretError(MemoryValidationError):
    pass


class MemoryConflictError(ValueError):
    pass


class MemoryNotFoundError(KeyError):
    pass


@dataclass(frozen=True)
class MemoryUseContext:
    private_session: bool = False
    project_name: str | None = None
    agent_id: str | None = None


class MemoryService:
    def __init__(
        self,
        conn: sqlite3.Connection,
        event_bus: EventBus | None = None,
        *,
        agent_exists: Callable[[str], bool] | None = None,
    ):
        self.conn = conn
        self.event_bus = event_bus
        self.agent_exists = agent_exists

    def create_proposal(
        self,
        *,
        memory_type: str,
        content: str,
        scope_type: str,
        scope_value: str | None,
        source_type: str,
        confidence: str,
        sensitivity: str,
        source_agent_id: str | None = None,
        source_reference: str | None = None,
        proposal_reason: str | None = None,
        expires_at: str | None = None,
        actor: str = "local_user",
    ) -> dict[str, Any]:
        actor = _normalize_actor(actor)
        values = self._validated_values(
            {
                "memory_type": memory_type,
                "content": content,
                "scope_type": scope_type,
                "scope_value": scope_value,
                "source_type": source_type,
                "source_agent_id": source_agent_id,
                "source_reference": source_reference,
                "proposal_reason": proposal_reason,
                "confidence": confidence,
                "sensitivity": sensitivity,
                "expires_at": expires_at,
            }
        )
        memory_id = str(uuid4())
        now = utc_now()
        content_hash = _content_hash(values["content"], values["scope_type"], values["scope_value"])
        self.conn.execute(
            """
            insert into memories (
              memory_id, memory_type, content, status, scope_type, scope_value,
              source_type, source_agent_id, source_reference, proposal_reason,
              confidence, sensitivity, expires_at, created_at, updated_at,
              content_hash
            ) values (?, ?, ?, 'pending', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                memory_id,
                values["memory_type"],
                values["content"],
                values["scope_type"],
                values["scope_value"],
                values["source_type"],
                values["source_agent_id"],
                values["source_reference"],
                values["proposal_reason"],
                values["confidence"],
                values["sensitivity"],
                values["expires_at"],
                now,
                now,
                content_hash,
            ),
        )
        metadata = self._safe_metadata(
            memory_id,
            values,
            status="pending",
            transition="created_pending",
        )
        self._record_event("memory.proposed", memory_id, actor, metadata)
        return self.get_memory(memory_id)

    def get_memory(self, memory_id: str) -> dict[str, Any]:
        row = self._get_row(memory_id)
        return self._serialize(row)

    def list_memories(
        self,
        *,
        query: str | None = None,
        status: str | None = None,
        memory_type: str | None = None,
        scope_type: str | None = None,
        scope_value: str | None = None,
        limit: int = DEFAULT_LIST_LIMIT,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        limit, offset = _validate_pagination(limit, offset)
        conditions: list[str] = []
        parameters: list[Any] = []
        normalized_query = _normalize_optional_text(query, MAX_QUERY_LENGTH, "search query")
        if normalized_query is not None:
            escaped_query = _escape_like_pattern(normalized_query)
            search_pattern = f"%{escaped_query}%"
            search_fields = (
                "content",
                "memory_type",
                "scope_type",
                "scope_value",
                "source_type",
                "source_agent_id",
                "source_reference",
                "proposal_reason",
            )
            conditions.append(
                "("
                + " or ".join(
                    f"lower(coalesce({field}, '')) like lower(?) escape '\\'"
                    for field in search_fields
                )
                + ")"
            )
            parameters.extend([search_pattern] * len(search_fields))
        if status is not None:
            _validate_choice("status", status, MEMORY_STATUSES)
            conditions.append("status = ?")
            parameters.append(status)
        if memory_type is not None:
            _validate_choice("memory type", memory_type, MEMORY_TYPES)
            conditions.append("memory_type = ?")
            parameters.append(memory_type)
        if scope_type is not None:
            _validate_choice("scope type", scope_type, SCOPE_TYPES)
            conditions.append("scope_type = ?")
            parameters.append(scope_type)
        if scope_value is not None:
            normalized_scope_value = _normalize_optional_text(scope_value, 1000, "scope value")
            conditions.append("scope_value = ?")
            parameters.append(normalized_scope_value)
        where_clause = f" where {' and '.join(conditions)}" if conditions else ""
        rows = self.conn.execute(
            f"select {_SELECT_MEMORY} from memories{where_clause} "
            "order by created_at desc, memory_id limit ? offset ?",
            (*parameters, limit, offset),
        ).fetchall()
        return [self._serialize(row) for row in rows]

    def summary(self) -> dict[str, Any]:
        counts = {status: 0 for status in sorted(MEMORY_STATUSES)}
        for status, count in self.conn.execute(
            "select status, count(*) from memories group by status"
        ).fetchall():
            if status in counts:
                counts[status] = int(count)
        now = utc_now()
        expired = int(
            self.conn.execute(
                "select count(*) from memories "
                "where status = 'approved' and expires_at is not null and expires_at <= ?",
                (now,),
            ).fetchone()[0]
        )
        active = int(
            self.conn.execute(
                "select count(*) from memories "
                "where status = 'approved' and (expires_at is null or expires_at > ?)",
                (now,),
            ).fetchone()[0]
        )
        total = sum(counts.values())
        return {
            "total": total,
            "counts": counts,
            "active": active,
            "expired": expired,
            "inactive": total - active,
        }

    def approve(
        self,
        memory_id: str,
        *,
        approved_by: str = "local_user",
    ) -> dict[str, Any]:
        approved_by = _normalize_actor(approved_by)
        row = self._get_row(memory_id)
        record = self._row_dict(row)
        self._require_status(record, "pending", "approve")
        now = utc_now()
        self.conn.execute(
            """
            update memories
            set status = 'approved', updated_at = ?, approved_at = ?,
                approved_by = ?, last_confirmed_at = ?, disabled_at = null,
                rejected_at = null, rejected_by = null, rejection_reason = null
            where memory_id = ?
            """,
            (now, now, approved_by, now, memory_id),
        )
        metadata = self._safe_metadata(
            memory_id,
            record,
            status="approved",
            transition="pending_to_approved",
        )
        self._record_event("memory.approved", memory_id, approved_by, metadata)
        return self.get_memory(memory_id)

    def reject(
        self,
        memory_id: str,
        *,
        rejected_by: str = "local_user",
        rejection_reason: str | None = None,
    ) -> dict[str, Any]:
        rejected_by = _normalize_actor(rejected_by)
        reason = _normalize_optional_text(rejection_reason, MAX_REASON_LENGTH, "rejection reason")
        row = self._get_row(memory_id)
        record = self._row_dict(row)
        self._require_status(record, "pending", "reject")
        now = utc_now()
        self.conn.execute(
            """
            update memories
            set status = 'rejected', updated_at = ?, rejected_at = ?,
                rejected_by = ?, rejection_reason = ?, approved_at = null,
                approved_by = null, last_confirmed_at = null, disabled_at = null
            where memory_id = ?
            """,
            (now, now, rejected_by, reason, memory_id),
        )
        metadata = self._safe_metadata(
            memory_id,
            record,
            status="rejected",
            transition="pending_to_rejected",
            reasonCategory="user_provided" if reason else "not_provided",
        )
        self._record_event("memory.rejected", memory_id, rejected_by, metadata)
        return self.get_memory(memory_id)

    def edit(
        self,
        memory_id: str,
        updates: dict[str, Any],
        *,
        actor: str = "local_user",
    ) -> dict[str, Any]:
        actor = _normalize_actor(actor)
        unknown = set(updates) - _EDITABLE_FIELDS
        if unknown:
            raise MemoryValidationError("unknown memory update fields")
        row = self._get_row(memory_id)
        current = self._row_dict(row)
        candidate = {field: current[field] for field in _EDITABLE_FIELDS}
        candidate.update(updates)
        validated = self._validated_values(candidate)
        changed_fields = sorted(
            field for field in _EDITABLE_FIELDS if validated[field] != current[field]
        )
        if not changed_fields:
            response = self._serialize(row)
            response.update(
                {
                    "changedFields": [],
                    "statusChanged": False,
                    "reapprovalRequired": False,
                }
            )
            return response

        previous_status = current["status"]
        substantive_change = bool(set(changed_fields) & _SUBSTANTIVE_FIELDS)
        next_status = previous_status
        if previous_status == "rejected":
            next_status = "pending"
        elif previous_status in {"approved", "disabled"} and substantive_change:
            next_status = "pending"

        reset_resolution = next_status == "pending" and previous_status != "pending"
        content_hash = current["content_hash"]
        if {"content", "scope_type", "scope_value"} & set(changed_fields):
            content_hash = _content_hash(
                validated["content"],
                validated["scope_type"],
                validated["scope_value"],
            )
        now = utc_now()
        assignments = [f"{field} = ?" for field in sorted(_EDITABLE_FIELDS)]
        parameters = [validated[field] for field in sorted(_EDITABLE_FIELDS)]
        assignments.extend(["status = ?", "updated_at = ?", "content_hash = ?"])
        parameters.extend([next_status, now, content_hash])
        if reset_resolution:
            assignments.extend(
                [
                    "approved_at = null",
                    "approved_by = null",
                    "last_confirmed_at = null",
                    "disabled_at = null",
                    "rejected_at = null",
                    "rejected_by = null",
                    "rejection_reason = null",
                ]
            )
        parameters.append(memory_id)
        self.conn.execute(
            f"update memories set {', '.join(assignments)} where memory_id = ?",
            parameters,
        )
        metadata = self._safe_metadata(
            memory_id,
            validated,
            status=next_status,
            transition=f"{previous_status}_to_{next_status}",
            changedFields=[_camel_case(field) for field in changed_fields],
            reapprovalRequired=reset_resolution,
        )
        self._record_event("memory.updated", memory_id, actor, metadata)
        response = self.get_memory(memory_id)
        response.update(
            {
                "changedFields": [_camel_case(field) for field in changed_fields],
                "statusChanged": previous_status != next_status,
                "reapprovalRequired": reset_resolution,
            }
        )
        return response

    def disable(self, memory_id: str, *, actor: str = "local_user") -> dict[str, Any]:
        actor = _normalize_actor(actor)
        row = self._get_row(memory_id)
        record = self._row_dict(row)
        self._require_status(record, "approved", "disable")
        now = utc_now()
        self.conn.execute(
            "update memories set status = 'disabled', updated_at = ?, disabled_at = ? "
            "where memory_id = ?",
            (now, now, memory_id),
        )
        metadata = self._safe_metadata(
            memory_id,
            record,
            status="disabled",
            transition="approved_to_disabled",
        )
        self._record_event("memory.disabled", memory_id, actor, metadata)
        return self.get_memory(memory_id)

    def enable(self, memory_id: str, *, actor: str = "local_user") -> dict[str, Any]:
        actor = _normalize_actor(actor)
        row = self._get_row(memory_id)
        record = self._row_dict(row)
        self._require_status(record, "disabled", "enable")
        now = utc_now()
        self.conn.execute(
            "update memories set status = 'approved', updated_at = ?, disabled_at = null "
            "where memory_id = ?",
            (now, memory_id),
        )
        metadata = self._safe_metadata(
            memory_id,
            record,
            status="approved",
            transition="disabled_to_approved",
        )
        self._record_event("memory.enabled", memory_id, actor, metadata)
        return self.get_memory(memory_id)

    def delete(self, memory_id: str, *, actor: str = "local_user") -> dict[str, Any]:
        actor = _normalize_actor(actor)
        row = self._get_row(memory_id)
        record = self._row_dict(row)
        metadata = self._safe_metadata(
            memory_id,
            record,
            status="deleted",
            transition=f"{record['status']}_to_deleted",
        )
        self.conn.execute("delete from memories where memory_id = ?", (memory_id,))
        self._record_event("memory.deleted", memory_id, actor, metadata)
        return {"memoryId": memory_id, "deleted": True}

    def is_active(self, memory: dict[str, Any] | str) -> bool:
        record = self.get_memory(memory) if isinstance(memory, str) else memory
        status = record.get("status")
        expires_at = record.get("expiresAt", record.get("expires_at"))
        return status == "approved" and not _is_expired(expires_at)

    def list_active_memories(
        self,
        context: MemoryUseContext,
        *,
        limit: int = MAX_LIST_LIMIT,
    ) -> list[dict[str, Any]]:
        limit, _ = _validate_pagination(limit, 0)
        if context.private_session:
            return []
        scope_conditions = ["scope_type = 'global'"]
        parameters: list[Any] = []
        if context.project_name and context.project_name.strip():
            scope_conditions.append("(scope_type = 'project' and scope_value = ?)")
            parameters.append(context.project_name.strip())
        if context.agent_id and context.agent_id.strip():
            scope_conditions.append("(scope_type = 'agent' and scope_value = ?)")
            parameters.append(context.agent_id.strip())
        parameters.extend([utc_now(), limit])
        rows = self.conn.execute(
            f"select {_SELECT_MEMORY} from memories "
            "where status = 'approved' and (expires_at is null or expires_at > ?) "
            f"and ({' or '.join(scope_conditions)}) "
            "order by updated_at desc, memory_id limit ?",
            (parameters[-2], *parameters[:-2], parameters[-1]),
        ).fetchall()
        return [self._serialize(row) for row in rows]

    def apply_private_session_policy(self, context: MemoryUseContext) -> dict[str, bool]:
        return {
            "privateSession": context.private_session,
            "memoryUseAllowed": not context.private_session,
            "automaticProposalAllowed": False,
            "automaticPersistenceAllowed": False,
        }

    def list_memory_events(self, memory_id: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            select event_id, memory_id, event_type, actor, metadata, created_at
            from memory_events where memory_id = ?
            order by created_at, event_id
            """,
            (memory_id,),
        ).fetchall()
        return [
            {
                "eventId": row[0],
                "memoryId": row[1],
                "eventType": row[2],
                "actor": row[3],
                "metadata": json.loads(row[4]),
                "createdAt": row[5],
            }
            for row in rows
        ]

    def _validated_values(self, values: dict[str, Any]) -> dict[str, Any]:
        memory_type = _validate_choice("memory type", values.get("memory_type"), MEMORY_TYPES)
        content = _normalize_content(values.get("content"))
        reject_secret_like_content(content, label="memory content")
        scope_type = _validate_choice("scope type", values.get("scope_type"), SCOPE_TYPES)
        scope_value = _normalize_scope(scope_type, values.get("scope_value"))
        source_type = _validate_choice("source type", values.get("source_type"), SOURCE_TYPES)
        source_agent_id = _normalize_optional_text(
            values.get("source_agent_id"), 200, "source agent ID"
        )
        if source_type in {"agent_proposal", "feedback_proposal"} and not source_agent_id:
            raise MemoryValidationError(
                f"source agent ID is required for a {source_type.replace('_', ' ')}"
            )
        if source_agent_id:
            self._validate_agent(source_agent_id, "source agent ID")
        if scope_type == "agent":
            self._validate_agent(scope_value, "agent scope")
        return {
            "memory_type": memory_type,
            "content": content,
            "scope_type": scope_type,
            "scope_value": scope_value,
            "source_type": source_type,
            "source_agent_id": source_agent_id,
            "source_reference": _normalize_optional_text(
                values.get("source_reference"), MAX_REASON_LENGTH, "source reference"
            ),
            "proposal_reason": _normalize_optional_text(
                values.get("proposal_reason"), MAX_REASON_LENGTH, "proposal reason"
            ),
            "confidence": _validate_choice(
                "confidence", values.get("confidence"), CONFIDENCE_VALUES
            ),
            "sensitivity": _validate_choice(
                "sensitivity", values.get("sensitivity"), SENSITIVITY_VALUES
            ),
            "expires_at": _normalize_expiration(values.get("expires_at")),
        }

    def _validate_agent(self, agent_id: str, label: str) -> None:
        if self.agent_exists is None or not self.agent_exists(agent_id):
            raise MemoryValidationError(f"{label} must reference an existing local response agent")

    def _get_row(self, memory_id: str) -> tuple[Any, ...]:
        normalized_id = str(memory_id or "").strip()
        row = self.conn.execute(
            f"select {_SELECT_MEMORY} from memories where memory_id = ?",
            (normalized_id,),
        ).fetchone()
        if row is None:
            raise MemoryNotFoundError("memory not found")
        return row

    def _require_status(
        self,
        record: dict[str, Any],
        required_status: str,
        operation: str,
    ) -> None:
        if record["status"] != required_status:
            raise MemoryConflictError(
                f"cannot {operation} memory from status {record['status']}"
            )

    def _record_event(
        self,
        event_type: str,
        memory_id: str,
        actor: str,
        metadata: dict[str, Any],
    ) -> None:
        created_at = utc_now()
        self.conn.execute(
            """
            insert into memory_events (
              event_id, memory_id, event_type, actor, metadata, created_at
            ) values (?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid4()),
                memory_id,
                event_type,
                actor,
                json.dumps(metadata, sort_keys=True),
                created_at,
            ),
        )
        self.conn.commit()
        if self.event_bus is not None:
            self.event_bus.emit(event_type, payload=metadata)

    def _safe_metadata(
        self,
        memory_id: str,
        values: dict[str, Any],
        *,
        status: str,
        transition: str,
        **extra: Any,
    ) -> dict[str, Any]:
        metadata = {
            "memoryId": memory_id,
            "memoryType": values["memory_type"],
            "status": status,
            "scopeType": values["scope_type"],
            "sensitivity": values["sensitivity"],
            "transition": transition,
        }
        metadata.update(extra)
        return metadata

    def _row_dict(self, row: tuple[Any, ...]) -> dict[str, Any]:
        return dict(zip(_MEMORY_COLUMNS, row, strict=True))

    def _serialize(self, row: tuple[Any, ...]) -> dict[str, Any]:
        record = self._row_dict(row)
        effective_status = (
            "expired"
            if record["status"] == "approved" and _is_expired(record["expires_at"])
            else record["status"]
        )
        return {
            "memoryId": record["memory_id"],
            "memoryType": record["memory_type"],
            "content": record["content"],
            "status": record["status"],
            "effectiveStatus": effective_status,
            "active": effective_status == "approved",
            "scopeType": record["scope_type"],
            "scopeValue": record["scope_value"],
            "sourceType": record["source_type"],
            "sourceAgentId": record["source_agent_id"],
            "sourceReference": record["source_reference"],
            "proposalReason": record["proposal_reason"],
            "confidence": record["confidence"],
            "sensitivity": record["sensitivity"],
            "expiresAt": record["expires_at"],
            "createdAt": record["created_at"],
            "updatedAt": record["updated_at"],
            "approvedAt": record["approved_at"],
            "approvedBy": record["approved_by"],
            "lastConfirmedAt": record["last_confirmed_at"],
            "disabledAt": record["disabled_at"],
            "rejectedAt": record["rejected_at"],
            "rejectedBy": record["rejected_by"],
            "rejectionReason": record["rejection_reason"],
        }


def _normalize_content(value: Any) -> str:
    if not isinstance(value, str):
        raise MemoryValidationError("memory content must be text")
    normalized = value.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        raise MemoryValidationError("memory content must contain 1 to 4000 characters")
    if len(normalized) > MAX_CONTENT_LENGTH:
        raise MemoryValidationError("memory content must contain 1 to 4000 characters")
    return normalized


def _normalize_optional_text(value: Any, maximum: int, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise MemoryValidationError(f"{label} must be text")
    normalized = value.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        return None
    if len(normalized) > maximum:
        raise MemoryValidationError(f"{label} exceeds the maximum length")
    return normalized


def _normalize_scope(scope_type: str, scope_value: Any) -> str | None:
    normalized = _normalize_optional_text(scope_value, 1000, "scope value")
    if scope_type == "global":
        if normalized is not None:
            raise MemoryValidationError("global scope must not include a scope value")
        return None
    if normalized is None:
        raise MemoryValidationError(f"{scope_type} scope requires a scope value")
    return normalized


def _normalize_actor(value: Any) -> str:
    if not isinstance(value, str) or not _ACTOR_PATTERN.fullmatch(value.strip()):
        raise MemoryValidationError("actor must be a safe local identifier")
    return value.strip()


def _normalize_expiration(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise MemoryValidationError("expiration must be a valid UTC timestamp or null")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise MemoryValidationError("expiration must be a valid UTC timestamp or null") from exc
    if parsed.tzinfo is None:
        raise MemoryValidationError("expiration must include a UTC offset")
    return parsed.astimezone(timezone.utc).isoformat()


def _validate_choice(label: str, value: Any, allowed: frozenset[str]) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise MemoryValidationError(f"unsupported {label}")
    return value


def _validate_pagination(limit: Any, offset: Any) -> tuple[int, int]:
    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1 or limit > MAX_LIST_LIMIT:
        raise MemoryValidationError("list limit must be between 1 and 200")
    if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
        raise MemoryValidationError("list offset must be non-negative")
    return limit, offset


def reject_secret_like_content(content: str, *, label: str = "content") -> None:
    """Reject credential-like text without reproducing it in errors or audit data."""
    if any(
        pattern.search(content)
        for pattern in (
            _PEM_PRIVATE_KEY_PATTERN,
            _ASSIGNMENT_SECRET_PATTERN,
            _LABELED_SECRET_PATTERN,
            _COOKIE_DUMP_PATTERN,
            _BEARER_JWT_PATTERN,
        )
    ):
        raise MemorySecretError(
            f"{label} rejected: credential_or_secret_material"
        )


def _content_hash(content: str, scope_type: str, scope_value: str | None) -> str:
    effective_scope = f"{scope_type}:{scope_value or ''}"
    material = f"{content}\n--effective-scope--\n{effective_scope}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def _escape_like_pattern(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _is_expired(expires_at: Any) -> bool:
    if not expires_at:
        return False
    try:
        parsed = datetime.fromisoformat(str(expires_at).replace("Z", "+00:00"))
    except ValueError:
        return True
    if parsed.tzinfo is None:
        return True
    return parsed.astimezone(timezone.utc) <= datetime.now(timezone.utc)


def _camel_case(value: str) -> str:
    head, *tail = value.split("_")
    return head + "".join(part.capitalize() for part in tail)
