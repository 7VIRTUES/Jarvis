from __future__ import annotations

import json
import re
import sqlite3
from typing import Any, Callable
from uuid import UUID, uuid4

from .events import EventBus
from .memory import (
    MemoryConflictError,
    MemorySecretError,
    MemoryService,
    MemoryValidationError,
    reject_secret_like_content,
)
from .time_utils import utc_now


RATINGS = frozenset({"helpful", "partially_helpful", "not_helpful"})
ISSUE_TAGS = frozenset(
    {
        "correct",
        "incorrect",
        "missed_constraint",
        "outdated",
        "too_long",
        "too_short",
        "unclear",
        "good_structure",
        "good_detail",
        "good_tone",
        "unsafe_or_risky",
    }
)
MAX_TAGS = 6
MAX_NOTE_LENGTH = 1500
MAX_LIST_LIMIT = 200
_ACTOR_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{1,100}$")
_FEEDBACK_COLUMNS = (
    "feedback_id",
    "response_id",
    "agent_id",
    "rating",
    "issue_tags",
    "note",
    "linked_memory_id",
    "created_at",
    "updated_at",
)
_SELECT_FEEDBACK = ", ".join(_FEEDBACK_COLUMNS)


class FeedbackValidationError(ValueError):
    pass


class FeedbackConflictError(ValueError):
    pass


class FeedbackNotFoundError(KeyError):
    pass


class FeedbackService:
    """Explicit local feedback storage with redacted append-only audit metadata."""

    def __init__(
        self,
        conn: sqlite3.Connection,
        event_bus: EventBus | None,
        memory_service: MemoryService,
        *,
        agent_exists: Callable[[str], bool] | None = None,
    ):
        self.conn = conn
        self.event_bus = event_bus
        self.memory_service = memory_service
        self.agent_exists = agent_exists

    def create(
        self,
        *,
        response_id: str,
        agent_id: str,
        rating: str,
        issue_tags: list[str],
        note: str = "",
        private_session: bool = False,
        actor: str = "local_user",
    ) -> dict[str, Any]:
        if private_session:
            raise FeedbackConflictError("private session blocks feedback persistence")
        response_id = self._response_id(response_id)
        agent_id = self._agent_id(agent_id)
        rating = self._rating(rating)
        issue_tags = self._issue_tags(issue_tags)
        note = self._note(note)
        actor = self._actor(actor)
        feedback_id = str(uuid4())
        now = utc_now()
        try:
            self.conn.execute(
                "insert into response_feedback (feedback_id, response_id, agent_id, rating, "
                "issue_tags, note, linked_memory_id, created_at, updated_at) "
                "values (?, ?, ?, ?, ?, ?, null, ?, ?)",
                (
                    feedback_id,
                    response_id,
                    agent_id,
                    rating,
                    json.dumps(issue_tags, sort_keys=True),
                    note,
                    now,
                    now,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise FeedbackConflictError("feedback already exists for this response ID") from exc
        self._record_event(
            "feedback.created",
            feedback_id,
            actor,
            self._safe_metadata(
                feedback_id=feedback_id,
                response_id=response_id,
                agent_id=agent_id,
                rating=rating,
                issue_tags=issue_tags,
                note_present=bool(note),
                linked_memory_id=None,
                transition="created",
            ),
        )
        return self.get(feedback_id)

    def update(
        self,
        feedback_id: str,
        updates: dict[str, Any],
        *,
        actor: str = "local_user",
    ) -> dict[str, Any]:
        current = self._row_dict(self._row(feedback_id))
        actor = self._actor(actor)
        allowed = {"rating", "issue_tags", "note"}
        if not set(updates).issubset(allowed):
            raise FeedbackValidationError("feedback update contains unsupported fields")
        normalized: dict[str, Any] = {}
        if "rating" in updates:
            normalized["rating"] = self._rating(updates["rating"])
        if "issue_tags" in updates:
            normalized["issue_tags"] = self._issue_tags(updates["issue_tags"])
        if "note" in updates:
            normalized["note"] = self._note(updates["note"])
        changed = [
            field
            for field, value in normalized.items()
            if value != (json.loads(current[field]) if field == "issue_tags" else current[field])
        ]
        if not changed:
            return self._serialize(tuple(current[column] for column in _FEEDBACK_COLUMNS))
        assignments: list[str] = []
        parameters: list[Any] = []
        for field in changed:
            assignments.append(f"{field} = ?")
            value = normalized[field]
            parameters.append(json.dumps(value, sort_keys=True) if field == "issue_tags" else value)
        assignments.append("updated_at = ?")
        parameters.extend([utc_now(), feedback_id])
        self.conn.execute(
            f"update response_feedback set {', '.join(assignments)} where feedback_id = ?",
            parameters,
        )
        updated = self.get(feedback_id)
        self._record_event(
            "feedback.updated",
            feedback_id,
            actor,
            self._safe_metadata(
                **self._metadata_values(updated),
                changed_fields=[self._api_field(field) for field in changed],
                transition="updated",
            ),
        )
        return self.get(feedback_id)

    def list(
        self,
        *,
        agent_id: str | None = None,
        rating: str | None = None,
        issue_tag: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        limit, offset = self._pagination(limit, offset)
        conditions: list[str] = []
        parameters: list[Any] = []
        if agent_id is not None:
            conditions.append("agent_id = ?")
            parameters.append(self._agent_id(agent_id))
        if rating is not None:
            conditions.append("rating = ?")
            parameters.append(self._rating(rating))
        if issue_tag is not None:
            if issue_tag not in ISSUE_TAGS:
                raise FeedbackValidationError("unsupported feedback issue tag")
            conditions.append("issue_tags like ?")
            parameters.append(f'%"{issue_tag}"%')
        where = f" where {' and '.join(conditions)}" if conditions else ""
        rows = self.conn.execute(
            f"select {_SELECT_FEEDBACK} from response_feedback{where} "
            "order by created_at desc, feedback_id desc limit ? offset ?",
            (*parameters, limit, offset),
        ).fetchall()
        return [self._serialize(row, include_note=False) for row in rows]

    def get(self, feedback_id: str) -> dict[str, Any]:
        return self._serialize(self._row(feedback_id))

    def events(self, feedback_id: str) -> list[dict[str, Any]]:
        feedback_id = self._normalize_id(feedback_id, "feedback ID")
        rows = self.conn.execute(
            "select event_id, feedback_id, event_type, actor, metadata, created_at "
            "from feedback_events where feedback_id = ? order by created_at, event_id",
            (feedback_id,),
        ).fetchall()
        if not rows:
            self._row(feedback_id)
        return [
            {
                "eventId": row[0],
                "feedbackId": row[1],
                "eventType": row[2],
                "actor": row[3],
                "metadata": json.loads(row[4]),
                "createdAt": row[5],
            }
            for row in rows
        ]

    def summary(self) -> dict[str, Any]:
        total = int(self.conn.execute("select count(*) from response_feedback").fetchone()[0])
        rating_counts = {rating: 0 for rating in RATINGS}
        for rating, count in self.conn.execute(
            "select rating, count(*) from response_feedback group by rating"
        ).fetchall():
            if rating in rating_counts:
                rating_counts[rating] = int(count)
        tag_counts = {tag: 0 for tag in ISSUE_TAGS}
        for (tags_json,) in self.conn.execute("select issue_tags from response_feedback").fetchall():
            for tag in json.loads(tags_json):
                if tag in tag_counts:
                    tag_counts[tag] += 1
        linked = int(
            self.conn.execute(
                "select count(*) from response_feedback where linked_memory_id is not null"
            ).fetchone()[0]
        )
        return {
            "totalFeedback": total,
            "countsByRating": rating_counts,
            "countsByIssueTag": tag_counts,
            "linkedPreferenceProposalCount": linked,
            "unlinkedFeedbackCount": total - linked,
        }

    def delete(self, feedback_id: str, *, actor: str = "local_user") -> dict[str, Any]:
        record = self.get(feedback_id)
        actor = self._actor(actor)
        self.conn.execute("delete from response_feedback where feedback_id = ?", (feedback_id,))
        self._record_event(
            "feedback.deleted",
            feedback_id,
            actor,
            self._safe_metadata(**self._metadata_values(record), transition="hard_deleted"),
        )
        return {"feedbackId": feedback_id, "deleted": True}

    def create_preference_proposal(
        self,
        feedback_id: str,
        *,
        content: str,
        scope_type: str,
        project_name: str | None,
        confidence: str,
        sensitivity: str,
        expires_at: str | None,
        actor: str = "local_user",
    ) -> dict[str, Any]:
        feedback = self.get(feedback_id)
        if feedback["linkedMemoryId"]:
            raise FeedbackConflictError("feedback already has a linked preference proposal")
        if scope_type not in {"agent", "project", "global"}:
            raise FeedbackValidationError("unsupported preference proposal scope")
        if scope_type == "agent":
            scope_value = feedback["agentId"]
        elif scope_type == "project":
            scope_value = self._optional_text(project_name, 200, "project name")
            if scope_value is None:
                raise FeedbackValidationError("project scope requires a project name")
        else:
            scope_value = None
        try:
            memory = self.memory_service.create_proposal(
                memory_type="preference",
                content=content,
                scope_type=scope_type,
                scope_value=scope_value,
                source_type="feedback_proposal",
                source_agent_id=feedback["agentId"],
                source_reference=f"feedback:{feedback_id}",
                proposal_reason="Explicit user feedback-derived preference proposal.",
                confidence=confidence,
                sensitivity=sensitivity,
                expires_at=expires_at,
                actor=actor,
            )
        except MemorySecretError as exc:
            raise FeedbackValidationError("preference content rejected: credential_or_secret_material") from exc
        except (MemoryValidationError, MemoryConflictError) as exc:
            raise FeedbackValidationError(str(exc)) from exc
        cursor = self.conn.execute(
            "update response_feedback set linked_memory_id = ?, updated_at = ? "
            "where feedback_id = ? and linked_memory_id is null",
            (memory["memoryId"], utc_now(), feedback_id),
        )
        if cursor.rowcount != 1:
            raise FeedbackConflictError("feedback already has a linked preference proposal")
        event_values = self._metadata_values(feedback)
        event_values["linked_memory_id"] = memory["memoryId"]
        self._record_event(
            "feedback.preference_proposed",
            feedback_id,
            self._actor(actor),
            self._safe_metadata(
                **event_values,
                scope_type=scope_type,
                transition="pending_preference_proposed",
            ),
        )
        return {
            "feedbackId": feedback_id,
            "linked": True,
            "memory": memory,
            "message": "Pending preference proposal created. Approval must occur separately.",
        }

    def _record_event(
        self,
        event_type: str,
        feedback_id: str,
        actor: str,
        metadata: dict[str, Any],
    ) -> None:
        created_at = utc_now()
        self.conn.execute(
            "insert into feedback_events (event_id, feedback_id, event_type, actor, metadata, created_at) "
            "values (?, ?, ?, ?, ?, ?)",
            (
                str(uuid4()),
                feedback_id,
                event_type,
                actor,
                json.dumps(metadata, sort_keys=True),
                created_at,
            ),
        )
        self.conn.commit()
        if self.event_bus is not None:
            self.event_bus.emit(event_type, payload=metadata)

    def _row(self, feedback_id: str) -> tuple[Any, ...]:
        feedback_id = self._normalize_id(feedback_id, "feedback ID")
        row = self.conn.execute(
            f"select {_SELECT_FEEDBACK} from response_feedback where feedback_id = ?",
            (feedback_id,),
        ).fetchone()
        if row is None:
            raise FeedbackNotFoundError("feedback not found")
        return row

    @staticmethod
    def _row_dict(row: tuple[Any, ...]) -> dict[str, Any]:
        return dict(zip(_FEEDBACK_COLUMNS, row, strict=True))

    @staticmethod
    def _serialize(row: tuple[Any, ...], *, include_note: bool = True) -> dict[str, Any]:
        record = dict(zip(_FEEDBACK_COLUMNS, row, strict=True))
        result = {
            "feedbackId": record["feedback_id"],
            "responseId": record["response_id"],
            "agentId": record["agent_id"],
            "rating": record["rating"],
            "issueTags": json.loads(record["issue_tags"]),
            "notePresent": bool(record["note"]),
            "linkedMemoryId": record["linked_memory_id"],
            "createdAt": record["created_at"],
            "updatedAt": record["updated_at"],
        }
        if include_note:
            result["note"] = record["note"]
        return result

    def _agent_id(self, value: Any) -> str:
        normalized = self._normalize_id(value, "agent ID")
        if self.agent_exists is None or not self.agent_exists(normalized):
            raise FeedbackValidationError("agent ID must reference an existing local response agent")
        return normalized

    @staticmethod
    def _response_id(value: Any) -> str:
        normalized = FeedbackService._normalize_id(value, "response ID")
        try:
            return str(UUID(normalized))
        except ValueError as exc:
            raise FeedbackValidationError("response ID must be a valid UUID") from exc

    @staticmethod
    def _rating(value: Any) -> str:
        if value not in RATINGS:
            raise FeedbackValidationError("unsupported feedback rating")
        return str(value)

    @staticmethod
    def _issue_tags(value: Any) -> list[str]:
        if not isinstance(value, list):
            raise FeedbackValidationError("feedback issue tags must be a list")
        normalized: list[str] = []
        for tag in value:
            if tag not in ISSUE_TAGS:
                raise FeedbackValidationError("unsupported feedback issue tag")
            if tag not in normalized:
                normalized.append(tag)
        if len(normalized) > MAX_TAGS:
            raise FeedbackValidationError("feedback supports at most six unique issue tags")
        return normalized

    @staticmethod
    def _note(value: Any) -> str:
        if value is None:
            return ""
        if not isinstance(value, str):
            raise FeedbackValidationError("feedback note must be text")
        normalized = value.replace("\r\n", "\n").replace("\r", "\n").strip()
        if len(normalized) > MAX_NOTE_LENGTH:
            raise FeedbackValidationError("feedback note exceeds 1500 characters")
        try:
            reject_secret_like_content(normalized, label="feedback note")
        except MemorySecretError as exc:
            raise FeedbackValidationError("feedback note rejected: credential_or_secret_material") from exc
        return normalized

    @staticmethod
    def _actor(value: Any) -> str:
        if not isinstance(value, str) or not _ACTOR_PATTERN.fullmatch(value.strip()):
            raise FeedbackValidationError("actor must be a safe local identifier")
        return value.strip()

    @staticmethod
    def _pagination(limit: Any, offset: Any) -> tuple[int, int]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= MAX_LIST_LIMIT:
            raise FeedbackValidationError("feedback list limit must be between 1 and 200")
        if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
            raise FeedbackValidationError("feedback list offset must be non-negative")
        return limit, offset

    @staticmethod
    def _normalize_id(value: Any, label: str) -> str:
        if not isinstance(value, str) or not value.strip() or len(value.strip()) > 200:
            raise FeedbackValidationError(f"{label} must be a nonblank identifier")
        return value.strip()

    @staticmethod
    def _optional_text(value: Any, maximum: int, label: str) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise FeedbackValidationError(f"{label} must be text")
        normalized = " ".join(value.split())
        if not normalized:
            return None
        if len(normalized) > maximum:
            raise FeedbackValidationError(f"{label} exceeds the maximum length")
        return normalized

    @staticmethod
    def _safe_metadata(
        *,
        feedback_id: str,
        response_id: str,
        agent_id: str,
        rating: str,
        issue_tags: list[str],
        note_present: bool,
        linked_memory_id: str | None,
        transition: str,
        changed_fields: list[str] | None = None,
        scope_type: str | None = None,
    ) -> dict[str, Any]:
        metadata: dict[str, Any] = {
            "feedbackId": feedback_id,
            "responseId": response_id,
            "agentId": agent_id,
            "rating": rating,
            "issueTags": issue_tags,
            "notePresent": note_present,
            "linkedMemoryId": linked_memory_id,
            "transition": transition,
        }
        if changed_fields is not None:
            metadata["changedFields"] = changed_fields
        if scope_type is not None:
            metadata["scopeType"] = scope_type
        return metadata

    @staticmethod
    def _metadata_values(record: dict[str, Any]) -> dict[str, Any]:
        return {
            "feedback_id": record["feedbackId"],
            "response_id": record["responseId"],
            "agent_id": record["agentId"],
            "rating": record["rating"],
            "issue_tags": record["issueTags"],
            "note_present": record["notePresent"],
            "linked_memory_id": record["linkedMemoryId"],
        }

    @staticmethod
    def _api_field(field: str) -> str:
        return {"issue_tags": "issueTags"}.get(field, field)
