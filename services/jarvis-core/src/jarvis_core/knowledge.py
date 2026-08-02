from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from typing import Any, Callable
from uuid import uuid4

from .db import knowledge_fts5_available
from .events import EventBus
from .memory import MemorySecretError, reject_secret_like_content
from .time_utils import utc_now

SOURCE_TYPES = frozenset({"pasted_text", "registered_project_file"})
SOURCE_STATUSES = frozenset({"active", "disabled"})
SCOPE_TYPES = frozenset({"global", "project", "agent"})
SENSITIVITY_VALUES = frozenset({"standard", "sensitive"})
MEDIA_TYPES = frozenset({"text/markdown", "text/plain", "text/csv"})
MAX_TITLE_LENGTH = 200
MAX_PASTED_CONTENT_LENGTH = 250_000
MAX_TAGS = 12
MAX_TAG_LENGTH = 40
MAX_QUERY_LENGTH = 200
DEFAULT_LIST_LIMIT = 50
MAX_LIST_LIMIT = 200
TARGET_CHUNK_LENGTH = 1_200
MAX_CHUNK_LENGTH = 1_600
CHUNK_OVERLAP = 160
MAX_CHUNKS = 500
_SOURCE_COLUMNS = (
    "source_id", "title", "source_type", "status", "scope_type", "scope_value",
    "sensitivity", "media_type", "project_name", "relative_path", "content",
    "content_hash", "tags", "char_count", "chunk_count", "source_size_bytes",
    "source_modified_at", "created_at", "updated_at", "imported_at", "disabled_at",
)
_SELECT_SOURCE = ", ".join(_SOURCE_COLUMNS)
_ACTOR_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{1,100}$")
_TAG_CREDENTIAL_ASSIGNMENT = re.compile(
    r"(?i)(?:password|passwd|pwd|api[_ -]?key|access[_ -]?token|refresh[_ -]?token|"
    r"client[_ -]?secret|private[_ -]?key|session[_ -]?token)\s*[:=]"
)
_MARKDOWN_HEADING = re.compile(r"(?m)^#{1,6}[ \t]+")
_SENTENCE_BOUNDARY = re.compile(r"[.!?](?:[\"')\]]*)\s+")


class KnowledgeValidationError(ValueError):
    pass


class KnowledgeSecretError(KnowledgeValidationError):
    pass


class KnowledgeConflictError(ValueError):
    def __init__(self, message: str, *, existing_source_id: str | None = None):
        super().__init__(message)
        self.existing_source_id = existing_source_id


class KnowledgeNotFoundError(KeyError):
    pass


def normalize_knowledge_content(content: Any, *, max_length: int) -> str:
    if not isinstance(content, str):
        raise KnowledgeValidationError("content must be text")
    normalized = content.removeprefix("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip(" \t") for line in normalized.split("\n")]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    collapsed: list[str] = []
    blank_count = 0
    for line in lines:
        if line:
            blank_count = 0
            collapsed.append(line)
        else:
            blank_count += 1
            if blank_count <= 2:
                collapsed.append("")
    normalized = "\n".join(collapsed)
    if not normalized:
        raise KnowledgeValidationError("content is required")
    if len(normalized) > max_length:
        raise KnowledgeValidationError(f"content exceeds the {max_length} character limit")
    try:
        reject_secret_like_content(normalized, label="knowledge content")
    except MemorySecretError as exc:
        raise KnowledgeSecretError("knowledge content rejected: credential_or_secret_material") from exc
    return normalized


def knowledge_content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def deterministic_chunks(content: str) -> list[dict[str, Any]]:
    if not content:
        raise KnowledgeValidationError("content is required")
    chunks: list[dict[str, Any]] = []
    start = 0
    while start < len(content):
        end = _choose_chunk_end(content, start)
        if end <= start:
            raise KnowledgeValidationError("content could not be chunked safely")
        chunk_content = content[start:end]
        if chunk_content.strip():
            chunks.append({
                "chunkIndex": len(chunks), "content": chunk_content,
                "contentHash": knowledge_content_hash(chunk_content),
                "charStart": start, "charEnd": end,
            })
        if len(chunks) > MAX_CHUNKS:
            raise KnowledgeValidationError("content exceeds the 500 chunk limit")
        if end >= len(content):
            break
        next_start = _choose_overlap_start(content, start, end)
        start = next_start if next_start > start else end
    if not chunks:
        raise KnowledgeValidationError("content did not produce any non-empty chunks")
    return chunks


def _choose_chunk_end(content: str, start: int) -> int:
    if len(content) - start <= MAX_CHUNK_LENGTH:
        return len(content)
    minimum = min(len(content), start + max(400, TARGET_CHUNK_LENGTH // 2))
    maximum = min(len(content), start + MAX_CHUNK_LENGTH)
    target = min(len(content), start + TARGET_CHUNK_LENGTH)
    headings = [match.start() for match in _MARKDOWN_HEADING.finditer(content, minimum, maximum)]
    if headings:
        return min(headings, key=lambda position: (abs(position - target), position))
    paragraphs: list[int] = []
    cursor = content.find("\n\n", minimum, maximum)
    while cursor >= 0:
        paragraphs.append(cursor + 2)
        cursor = content.find("\n\n", cursor + 2, maximum)
    if paragraphs:
        return min(paragraphs, key=lambda position: (abs(position - target), position))
    sentences = [match.end() for match in _SENTENCE_BOUNDARY.finditer(content, minimum, maximum)]
    if sentences:
        return min(sentences, key=lambda position: (abs(position - target), position))
    return maximum


def _choose_overlap_start(content: str, prior_start: int, end: int) -> int:
    desired = max(prior_start + 1, end - CHUNK_OVERLAP)
    paragraph = content.find("\n\n", desired, min(end, desired + 80))
    if paragraph >= 0:
        return paragraph + 2
    sentence = _SENTENCE_BOUNDARY.search(content, desired, min(end, desired + 80))
    if sentence:
        return sentence.end()
    space = content.find(" ", desired, min(end, desired + 40))
    return space + 1 if space >= 0 else desired


class KnowledgeService:
    def __init__(
        self, conn: sqlite3.Connection, event_bus: EventBus | None = None, *,
        agent_exists: Callable[[str], bool] | None = None,
        project_exists: Callable[[str], bool] | None = None,
    ):
        self.conn = conn
        self.event_bus = event_bus
        self.agent_exists = agent_exists
        self.project_exists = project_exists

    def create_source(
        self, *, title: str, source_type: str, scope_type: str,
        scope_value: str | None, sensitivity: str, media_type: str,
        content: str, tags: list[str], project_name: str | None = None,
        relative_path: str | None = None, source_size_bytes: int | None = None,
        source_modified_at: str | None = None, actor: str = "local_user",
    ) -> dict[str, Any]:
        actor = _normalize_actor(actor)
        title = self.validate_title(title)
        source_type = _choice("source type", source_type, SOURCE_TYPES)
        sensitivity = _choice("sensitivity", sensitivity, SENSITIVITY_VALUES)
        media_type = _choice("media type", media_type, MEDIA_TYPES)
        tags = self.validate_tags(tags)
        scope_type, scope_value = self.validate_scope(scope_type, scope_value)
        if source_type == "registered_project_file":
            project_name = _required_text(project_name, MAX_TITLE_LENGTH, "project name")
            if not self._project_exists(project_name):
                raise KnowledgeNotFoundError("registered project not found")
            if scope_type != "project" or scope_value != project_name:
                raise KnowledgeValidationError("registered-project file scope must match its registered project")
            relative_path = _required_text(relative_path, 500, "relative path")
        else:
            project_name = scope_value if scope_type == "project" else None
            relative_path = None
            source_size_bytes = None
            source_modified_at = None
        content = normalize_knowledge_content(
            content, max_length=MAX_PASTED_CONTENT_LENGTH if source_type == "pasted_text" else 500_000
        )
        chunks = deterministic_chunks(content)
        content_hash = knowledge_content_hash(content)
        existing = self._find_duplicate(
            content_hash=content_hash, scope_type=scope_type,
            scope_value=scope_value, source_type=source_type,
        )
        if existing:
            raise KnowledgeConflictError("duplicate knowledge source", existing_source_id=existing)
        source_id = str(uuid4())
        now = utc_now()
        metadata = self._event_metadata(
            source_id=source_id, source_type=source_type, status="active",
            scope_type=scope_type, sensitivity=sensitivity, media_type=media_type,
            project_name=project_name, relative_path=relative_path,
            content_hash=content_hash, char_count=len(content), chunk_count=len(chunks),
            reason_code="explicit_import",
        )
        with self.conn:
            self.conn.execute(
                """
                insert into knowledge_sources (
                  source_id, title, source_type, status, scope_type, scope_value,
                  sensitivity, media_type, project_name, relative_path, content,
                  content_hash, tags, char_count, chunk_count, source_size_bytes,
                  source_modified_at, created_at, updated_at, imported_at, disabled_at
                ) values (?, ?, ?, 'active', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, null)
                """,
                (source_id, title, source_type, scope_type, scope_value, sensitivity,
                 media_type, project_name, relative_path, content, content_hash,
                 json.dumps(tags, ensure_ascii=False), len(content), len(chunks),
                 source_size_bytes, source_modified_at, now, now, now),
            )
            self._insert_chunks(source_id, chunks, now)
            self._insert_event("knowledge.imported", source_id, actor, metadata, now)
        self._emit("knowledge.imported", metadata)
        return self.get_source(source_id)

    def list_sources(
        self, *, status: str | None = None, source_type: str | None = None,
        scope_type: str | None = None, scope_value: str | None = None,
        sensitivity: str | None = None, project_name: str | None = None,
        query: str | None = None, limit: int = DEFAULT_LIST_LIMIT, offset: int = 0,
    ) -> list[dict[str, Any]]:
        limit, offset = _validate_pagination(limit, offset)
        clauses: list[str] = []
        params: list[Any] = []
        for column, label, value, allowed in (
            ("status", "status", status, SOURCE_STATUSES),
            ("source_type", "source type", source_type, SOURCE_TYPES),
            ("scope_type", "scope type", scope_type, SCOPE_TYPES),
            ("sensitivity", "sensitivity", sensitivity, SENSITIVITY_VALUES),
        ):
            if value is not None:
                clauses.append(f"{column} = ?")
                params.append(_choice(label, value, allowed))
        if scope_value is not None:
            clauses.append("scope_value = ?")
            params.append(_optional_filter(scope_value, MAX_TITLE_LENGTH, "scope value"))
        if project_name is not None:
            clauses.append("project_name = ?")
            params.append(_optional_filter(project_name, MAX_TITLE_LENGTH, "project name"))
        if query is not None:
            pattern = f"%{_escape_like(_optional_filter(query, MAX_QUERY_LENGTH, 'search query'))}%"
            clauses.append(
                "(title like ? escape '\\' collate nocase or tags like ? escape '\\' collate nocase "
                "or source_type like ? escape '\\' collate nocase or coalesce(project_name, '') like ? escape '\\' collate nocase "
                "or coalesce(relative_path, '') like ? escape '\\' collate nocase or media_type like ? escape '\\' collate nocase)"
            )
            params.extend([pattern] * 6)
        where = f" where {' and '.join(clauses)}" if clauses else ""
        rows = self.conn.execute(
            f"select {_SELECT_SOURCE} from knowledge_sources{where} order by updated_at desc, source_id limit ? offset ?",
            (*params, limit, offset),
        ).fetchall()
        return [self._serialize(row, include_content=False) for row in rows]

    def get_source(self, source_id: str) -> dict[str, Any]:
        return self._serialize(self._get_row(source_id), include_content=True)

    def list_chunks(self, source_id: str) -> list[dict[str, Any]]:
        self._get_row(source_id)
        rows = self.conn.execute(
            """
            select chunk_id, source_id, chunk_index, content, content_hash, char_start, char_end, created_at
            from knowledge_chunks where source_id = ? order by chunk_index
            """, (_normalized_id(source_id),),
        ).fetchall()
        return [
            {"chunkId": row[0], "sourceId": row[1], "chunkIndex": row[2],
             "content": row[3], "contentHash": row[4], "charStart": row[5],
             "charEnd": row[6], "createdAt": row[7]}
            for row in rows
        ]

    def list_events(self, source_id: str) -> list[dict[str, Any]]:
        normalized = _normalized_id(source_id)
        rows = self.conn.execute(
            """
            select event_id, source_id, event_type, actor, metadata, created_at
            from knowledge_events where source_id = ? order by created_at, event_id
            """, (normalized,),
        ).fetchall()
        if not rows:
            exists = self.conn.execute("select 1 from knowledge_sources where source_id = ?", (normalized,)).fetchone()
            if not exists:
                raise KnowledgeNotFoundError("knowledge source not found")
        return [
            {"eventId": row[0], "sourceId": row[1], "eventType": row[2],
             "actor": row[3], "metadata": json.loads(row[4]), "createdAt": row[5]}
            for row in rows
        ]

    def summary(self) -> dict[str, Any]:
        row = self.conn.execute(
            """
            select count(*),
              sum(case when status = 'active' then 1 else 0 end),
              sum(case when status = 'disabled' then 1 else 0 end),
              sum(case when source_type = 'pasted_text' then 1 else 0 end),
              sum(case when source_type = 'registered_project_file' then 1 else 0 end),
              sum(case when sensitivity = 'standard' then 1 else 0 end),
              sum(case when sensitivity = 'sensitive' then 1 else 0 end),
              coalesce(sum(char_count), 0), coalesce(sum(chunk_count), 0)
            from knowledge_sources
            """
        ).fetchone()
        available = knowledge_fts5_available(self.conn)
        embedding_row = self.conn.execute(
            "select enabled from knowledge_embedding_settings where settings_id = 'default'"
        ).fetchone()
        return {
            "totalSources": row[0], "activeSources": row[1] or 0,
            "disabledSources": row[2] or 0, "pastedSources": row[3] or 0,
            "registeredProjectFiles": row[4] or 0, "standardSources": row[5] or 0,
            "sensitiveSources": row[6] or 0, "totalCharacters": row[7] or 0,
            "totalChunks": row[8] or 0, "fts5Available": available,
            "indexMode": "fts5" if available else "deterministic_fallback_available",
            "automaticScanningEnabled": False, "agentRetrievalEnabled": True,
            "retrievalRequiresExplicitOptIn": True, "automaticInjectionEnabled": False,
            "embeddingsEnabled": bool(embedding_row and embedding_row[0]),
            "localModelEnabled": False,
            "retrievalAndGenerationSeparate": True,
            "knowledgeSuppliedOnlyWhenExplicitlyEnabled": True,
            "generationModifiesKnowledge": False,
            "generationCreatesEmbeddings": False,
            "generatedOutputBecomesSource": False,
            "embeddingAndGenerationModelsSeparatelyConfigured": True,
        }

    def edit_metadata(self, source_id: str, updates: dict[str, Any], *, actor: str = "local_user") -> dict[str, Any]:
        actor = _normalize_actor(actor)
        current = self.get_source(source_id)
        allowed = {"title", "tags", "sensitivity", "scope_type", "scope_value"}
        if set(updates) - allowed:
            raise KnowledgeValidationError("unsupported metadata fields")
        if not updates:
            return current
        if current["sourceType"] == "registered_project_file" and ({"scope_type", "scope_value"} & set(updates)):
            raise KnowledgeValidationError("registered-project file scope cannot be edited")
        title = self.validate_title(updates.get("title", current["title"]))
        tags = self.validate_tags(updates.get("tags", current["tags"]))
        sensitivity = _choice("sensitivity", updates.get("sensitivity", current["sensitivity"]), SENSITIVITY_VALUES)
        scope_type, scope_value = self.validate_scope(
            updates.get("scope_type", current["scopeType"]),
            updates.get("scope_value", current["scopeValue"]),
        )
        project_name = scope_value if scope_type == "project" else None
        proposed = {"title": title, "tags": tags, "sensitivity": sensitivity,
                    "scope_type": scope_type, "scope_value": scope_value, "project_name": project_name}
        old = {"title": current["title"], "tags": current["tags"], "sensitivity": current["sensitivity"],
               "scope_type": current["scopeType"], "scope_value": current["scopeValue"],
               "project_name": current["projectName"]}
        changed = sorted(key for key, value in proposed.items() if value != old[key])
        if not changed:
            return current
        if "scope_type" in changed or "scope_value" in changed:
            duplicate = self._find_duplicate(
                content_hash=current["contentHash"], scope_type=scope_type,
                scope_value=scope_value, source_type=current["sourceType"],
                exclude_source_id=current["sourceId"],
            )
            if duplicate:
                raise KnowledgeConflictError("duplicate knowledge source", existing_source_id=duplicate)
        now = utc_now()
        metadata = self._event_metadata_from_source(
            current, changed_fields=changed, sensitivity=sensitivity,
            scope_type=scope_type, project_name=project_name,
            reason_code="explicit_metadata_edit",
        )
        with self.conn:
            self.conn.execute(
                """
                update knowledge_sources set title = ?, tags = ?, sensitivity = ?, scope_type = ?,
                  scope_value = ?, project_name = ?, updated_at = ? where source_id = ?
                """,
                (title, json.dumps(tags, ensure_ascii=False), sensitivity, scope_type,
                 scope_value, project_name, now, current["sourceId"]),
            )
            self._sync_source_fts(current["sourceId"])
            self._insert_event("knowledge.updated", current["sourceId"], actor, metadata, now)
        self._emit("knowledge.updated", metadata)
        return self.get_source(current["sourceId"])

    def replace_pasted_content(self, source_id: str, content: str, *, actor: str = "local_user") -> dict[str, Any]:
        actor = _normalize_actor(actor)
        current = self.get_source(source_id)
        if current["sourceType"] != "pasted_text":
            raise KnowledgeValidationError("registered-project file content can only change through refresh")
        normalized = normalize_knowledge_content(content, max_length=MAX_PASTED_CONTENT_LENGTH)
        content_hash = knowledge_content_hash(normalized)
        if content_hash == current["contentHash"]:
            return {"changed": False, "source": current}
        duplicate = self._find_duplicate(
            content_hash=content_hash, scope_type=current["scopeType"],
            scope_value=current["scopeValue"], source_type=current["sourceType"],
            exclude_source_id=current["sourceId"],
        )
        if duplicate:
            raise KnowledgeConflictError("duplicate knowledge source", existing_source_id=duplicate)
        chunks = deterministic_chunks(normalized)
        now = utc_now()
        metadata = self._event_metadata_from_source(
            current, content_hash=content_hash, char_count=len(normalized), chunk_count=len(chunks),
            changed_fields=["content", "content_hash", "char_count", "chunk_count"],
            reason_code="explicit_pasted_content_replacement",
        )
        with self.conn:
            self.conn.execute(
                "update knowledge_sources set content = ?, content_hash = ?, char_count = ?, chunk_count = ?, updated_at = ? where source_id = ?",
                (normalized, content_hash, len(normalized), len(chunks), now, current["sourceId"]),
            )
            self.conn.execute("delete from knowledge_chunks where source_id = ?", (current["sourceId"],))
            self._insert_chunks(current["sourceId"], chunks, now)
            self._insert_event("knowledge.updated", current["sourceId"], actor, metadata, now)
        self._emit("knowledge.updated", metadata)
        return {"changed": True, "source": self.get_source(current["sourceId"])}

    def refresh_registered_source(
        self, source_id: str, *, content: str, source_size_bytes: int,
        source_modified_at: str, actor: str = "local_user",
    ) -> dict[str, Any]:
        actor = _normalize_actor(actor)
        current = self.get_source(source_id)
        if current["sourceType"] != "registered_project_file":
            raise KnowledgeValidationError("only registered-project files can be refreshed")
        normalized = normalize_knowledge_content(content, max_length=500_000)
        content_hash = knowledge_content_hash(normalized)
        if content_hash == current["contentHash"]:
            return {"changed": False, "source": current}
        duplicate = self._find_duplicate(
            content_hash=content_hash, scope_type=current["scopeType"],
            scope_value=current["scopeValue"], source_type=current["sourceType"],
            exclude_source_id=current["sourceId"],
        )
        if duplicate:
            raise KnowledgeConflictError("duplicate knowledge source", existing_source_id=duplicate)
        chunks = deterministic_chunks(normalized)
        now = utc_now()
        metadata = self._event_metadata_from_source(
            current, content_hash=content_hash, char_count=len(normalized), chunk_count=len(chunks),
            changed_fields=["content", "content_hash", "char_count", "chunk_count", "source_size_bytes", "source_modified_at"],
            reason_code="explicit_registered_file_refresh",
        )
        with self.conn:
            self.conn.execute(
                """
                update knowledge_sources set content = ?, content_hash = ?, char_count = ?, chunk_count = ?,
                  source_size_bytes = ?, source_modified_at = ?, updated_at = ? where source_id = ?
                """,
                (normalized, content_hash, len(normalized), len(chunks), source_size_bytes,
                 source_modified_at, now, current["sourceId"]),
            )
            self.conn.execute("delete from knowledge_chunks where source_id = ?", (current["sourceId"],))
            self._insert_chunks(current["sourceId"], chunks, now)
            self._insert_event("knowledge.refreshed", current["sourceId"], actor, metadata, now)
        self._emit("knowledge.refreshed", metadata)
        return {"changed": True, "source": self.get_source(current["sourceId"])}

    def disable(self, source_id: str, *, actor: str = "local_user") -> dict[str, Any]:
        return self._transition(source_id, required="active", target="disabled", actor=actor)

    def enable(self, source_id: str, *, actor: str = "local_user") -> dict[str, Any]:
        return self._transition(source_id, required="disabled", target="active", actor=actor)

    def delete(self, source_id: str, *, actor: str = "local_user") -> dict[str, Any]:
        actor = _normalize_actor(actor)
        current = self.get_source(source_id)
        metadata = self._event_metadata_from_source(current, reason_code="explicit_hard_delete")
        now = utc_now()
        with self.conn:
            if knowledge_fts5_available(self.conn):
                self.conn.execute("delete from knowledge_chunks_fts where source_id = ?", (current["sourceId"],))
            self.conn.execute("delete from knowledge_chunks where source_id = ?", (current["sourceId"],))
            self.conn.execute("delete from knowledge_sources where source_id = ?", (current["sourceId"],))
            self._insert_event("knowledge.deleted", current["sourceId"], actor, metadata, now)
        self._emit("knowledge.deleted", metadata)
        return {"sourceId": current["sourceId"], "deleted": True, "contentReturned": False,
                "originalProjectFileChanged": False, "auditMetadataPreserved": True}

    def validate_title(self, value: Any) -> str:
        title = _required_text(value, MAX_TITLE_LENGTH, "title")
        try:
            reject_secret_like_content(title, label="knowledge title")
        except MemorySecretError as exc:
            raise KnowledgeSecretError("knowledge title rejected: credential_or_secret_material") from exc
        return title

    def validate_tags(self, values: Any) -> list[str]:
        if not isinstance(values, list):
            raise KnowledgeValidationError("tags must be a list")
        if len(values) > MAX_TAGS:
            raise KnowledgeValidationError("no more than 12 tags are allowed")
        tags: list[str] = []
        seen: set[str] = set()
        for value in values:
            tag = _required_text(value, MAX_TAG_LENGTH, "tag")
            if _TAG_CREDENTIAL_ASSIGNMENT.search(tag):
                try:
                    reject_secret_like_content(tag, label="knowledge tag")
                except MemorySecretError as exc:
                    raise KnowledgeSecretError("knowledge tag rejected: credential_or_secret_material") from exc
            key = tag.casefold()
            if key not in seen:
                tags.append(tag)
                seen.add(key)
        return tags

    def validate_scope(self, scope_type: Any, scope_value: Any) -> tuple[str, str | None]:
        normalized_type = _choice("scope type", scope_type, SCOPE_TYPES)
        if normalized_type == "global":
            if scope_value not in (None, ""):
                raise KnowledgeValidationError("global scope does not accept a scope value")
            return normalized_type, None
        normalized_value = _required_text(scope_value, MAX_TITLE_LENGTH, "scope value")
        if normalized_type == "agent":
            if self.agent_exists is None or not self.agent_exists(normalized_value):
                raise KnowledgeValidationError("agent scope must reference an existing local response agent")
        elif not self._project_exists(normalized_value):
            raise KnowledgeNotFoundError("registered project not found")
        return normalized_type, normalized_value

    def _project_exists(self, project_name: str) -> bool:
        return self.project_exists is not None and self.project_exists(project_name)

    def _transition(self, source_id: str, *, required: str, target: str, actor: str) -> dict[str, Any]:
        actor = _normalize_actor(actor)
        current = self.get_source(source_id)
        if current["status"] != required:
            raise KnowledgeConflictError(f"cannot transition knowledge source from {current['status']} to {target}")
        now = utc_now()
        disabled_at = now if target == "disabled" else None
        event_type = "knowledge.disabled" if target == "disabled" else "knowledge.enabled"
        metadata = self._event_metadata_from_source(
            current, status=target, transition=f"{required}_to_{target}",
            reason_code="explicit_lifecycle_change",
        )
        with self.conn:
            self.conn.execute(
                "update knowledge_sources set status = ?, disabled_at = ?, updated_at = ? where source_id = ?",
                (target, disabled_at, now, current["sourceId"]),
            )
            self._insert_event(event_type, current["sourceId"], actor, metadata, now)
        self._emit(event_type, metadata)
        return self.get_source(current["sourceId"])

    def _find_duplicate(
        self, *, content_hash: str, scope_type: str, scope_value: str | None,
        source_type: str, exclude_source_id: str | None = None,
    ) -> str | None:
        clauses = ["content_hash = ?", "scope_type = ?", "coalesce(scope_value, '') = ?",
                   "source_type = ?", "status in ('active', 'disabled')"]
        params: list[Any] = [content_hash, scope_type, scope_value or "", source_type]
        if exclude_source_id:
            clauses.append("source_id <> ?")
            params.append(exclude_source_id)
        row = self.conn.execute(
            f"select source_id from knowledge_sources where {' and '.join(clauses)} limit 1", params
        ).fetchone()
        return row[0] if row else None

    def _get_row(self, source_id: str) -> tuple[Any, ...]:
        normalized = _normalized_id(source_id)
        row = self.conn.execute(
            f"select {_SELECT_SOURCE} from knowledge_sources where source_id = ?", (normalized,)
        ).fetchone()
        if not row:
            raise KnowledgeNotFoundError("knowledge source not found")
        return row

    def _serialize(self, row: tuple[Any, ...], *, include_content: bool) -> dict[str, Any]:
        values = dict(zip(_SOURCE_COLUMNS, row))
        result: dict[str, Any] = {
            "sourceId": values["source_id"], "title": values["title"],
            "sourceType": values["source_type"], "status": values["status"],
            "active": values["status"] == "active", "scopeType": values["scope_type"],
            "scopeValue": values["scope_value"], "sensitivity": values["sensitivity"],
            "mediaType": values["media_type"], "projectName": values["project_name"],
            "relativePath": values["relative_path"], "tags": json.loads(values["tags"]),
            "charCount": values["char_count"], "chunkCount": values["chunk_count"],
            "sourceSizeBytes": values["source_size_bytes"], "sourceModifiedAt": values["source_modified_at"],
            "contentHash": values["content_hash"], "createdAt": values["created_at"],
            "updatedAt": values["updated_at"], "importedAt": values["imported_at"],
            "disabledAt": values["disabled_at"],
        }
        if include_content:
            result["content"] = values["content"]
        return result

    def _insert_chunks(self, source_id: str, chunks: list[dict[str, Any]], created_at: str) -> None:
        self.conn.executemany(
            """
            insert into knowledge_chunks (
              chunk_id, source_id, chunk_index, content, content_hash, char_start, char_end, created_at
            ) values (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [(str(uuid4()), source_id, chunk["chunkIndex"], chunk["content"],
              chunk["contentHash"], chunk["charStart"], chunk["charEnd"], created_at)
             for chunk in chunks],
        )

    def _sync_source_fts(self, source_id: str) -> None:
        if not knowledge_fts5_available(self.conn):
            return
        self.conn.execute("delete from knowledge_chunks_fts where source_id = ?", (source_id,))
        self.conn.execute(
            """
            insert into knowledge_chunks_fts (
              chunk_id, source_id, content, source_title, tags, scope_type, scope_value
            )
            select chunk.chunk_id, chunk.source_id, chunk.content, source.title, source.tags,
              source.scope_type, coalesce(source.scope_value, '')
            from knowledge_chunks as chunk
            join knowledge_sources as source on source.source_id = chunk.source_id
            where chunk.source_id = ? order by chunk.chunk_index
            """, (source_id,),
        )

    def _insert_event(self, event_type: str, source_id: str, actor: str,
                      metadata: dict[str, Any], created_at: str) -> None:
        self.conn.execute(
            "insert into knowledge_events (event_id, source_id, event_type, actor, metadata, created_at) values (?, ?, ?, ?, ?, ?)",
            (str(uuid4()), source_id, event_type, actor, json.dumps(metadata, sort_keys=True), created_at),
        )

    def _emit(self, event_type: str, metadata: dict[str, Any]) -> None:
        if self.event_bus is not None:
            self.event_bus.emit(event_type, payload=metadata)

    def _event_metadata_from_source(self, source: dict[str, Any], **overrides: Any) -> dict[str, Any]:
        values = {
            "source_id": source["sourceId"], "source_type": source["sourceType"],
            "status": source["status"], "scope_type": source["scopeType"],
            "sensitivity": source["sensitivity"], "media_type": source["mediaType"],
            "project_name": source["projectName"], "relative_path": source["relativePath"],
            "content_hash": source["contentHash"], "char_count": source["charCount"],
            "chunk_count": source["chunkCount"],
        }
        values.update(overrides)
        return self._event_metadata(**values)

    def _event_metadata(
        self, *, source_id: str, source_type: str, status: str, scope_type: str,
        sensitivity: str, media_type: str, project_name: str | None,
        relative_path: str | None, content_hash: str, char_count: int, chunk_count: int,
        changed_fields: list[str] | None = None, transition: str | None = None,
        reason_code: str | None = None,
    ) -> dict[str, Any]:
        metadata: dict[str, Any] = {
            "sourceId": source_id, "sourceType": source_type, "status": status,
            "scopeType": scope_type, "sensitivity": sensitivity, "mediaType": media_type,
            "projectName": project_name, "contentHash": content_hash,
            "characterCount": char_count, "chunkCount": chunk_count,
        }
        if relative_path:
            metadata["filename"] = relative_path.rsplit("/", 1)[-1]
            metadata["pathHash"] = hashlib.sha256(relative_path.encode("utf-8")).hexdigest()
        if changed_fields:
            metadata["changedFields"] = sorted(changed_fields)
        if transition:
            metadata["transition"] = transition
        if reason_code:
            metadata["reasonCode"] = reason_code
        return metadata


def _choice(label: str, value: Any, allowed: frozenset[str]) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise KnowledgeValidationError(f"unsupported {label}")
    return value


def _required_text(value: Any, maximum: int, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise KnowledgeValidationError(f"{label} is required")
    normalized = value.strip()
    if len(normalized) > maximum:
        raise KnowledgeValidationError(f"{label} exceeds the {maximum} character limit")
    return normalized


def _optional_filter(value: Any, maximum: int, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise KnowledgeValidationError(f"{label} must not be blank")
    normalized = value.strip()
    if len(normalized) > maximum:
        raise KnowledgeValidationError(f"{label} exceeds the {maximum} character limit")
    return normalized


def _normalize_actor(actor: Any) -> str:
    if not isinstance(actor, str) or not _ACTOR_PATTERN.fullmatch(actor):
        raise KnowledgeValidationError("actor is invalid")
    return actor


def _normalized_id(source_id: Any) -> str:
    if not isinstance(source_id, str) or not source_id.strip():
        raise KnowledgeValidationError("source ID is required")
    return source_id.strip()


def _validate_pagination(limit: Any, offset: Any) -> tuple[int, int]:
    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1 or limit > MAX_LIST_LIMIT:
        raise KnowledgeValidationError("list limit must be between 1 and 200")
    if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
        raise KnowledgeValidationError("list offset must be non-negative")
    return limit, offset


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
