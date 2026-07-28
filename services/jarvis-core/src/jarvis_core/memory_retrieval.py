from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from dataclasses import dataclass
from typing import Any, Callable
from uuid import uuid4

from .db import memory_fts5_available
from .events import EventBus
from .memory import MemoryValidationError
from .time_utils import utc_now


PURPOSES = frozenset({"manual_preview", "agent_response"})
MAX_QUERY_LENGTH = 1000
MAX_QUERY_TERMS = 24
MAX_TERM_LENGTH = 64
MAX_ITEMS = 10
MAX_HISTORY_LIMIT = 100

MEMORY_TYPE_PRIORITY = {
    "agent_instruction": 3,
    "constraint": 3,
    "preference": 3,
    "goal": 2,
    "decision": 2,
    "project_fact": 2,
    "personal_fact": 1,
    "routine": 1,
    "terminology": 1,
}
CONFIDENCE_PRIORITY = {"high": 3, "medium": 2, "low": 1}
_TOKEN_PATTERN = re.compile(r"[^\W_]+", re.UNICODE)
_ROW_COLUMNS = (
    "memory_id",
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
    "updated_at",
)


class MemoryRetrievalNotFoundError(KeyError):
    pass


@dataclass(frozen=True)
class MemoryRetrievalRequest:
    query: str
    agent_id: str | None = None
    project_name: str | None = None
    private_session: bool = False
    include_sensitive: bool = False
    max_items: int = 5
    purpose: str = "manual_preview"
    server_known_agent: bool = False


@dataclass(frozen=True)
class _NormalizedRequest:
    query: str
    terms: tuple[str, ...]
    agent_id: str | None
    project_name: str | None
    private_session: bool
    include_sensitive: bool
    max_items: int
    purpose: str


class MemoryRetrievalService:
    """Deterministic, scoped retrieval with redacted local audit evidence."""

    def __init__(
        self,
        conn: sqlite3.Connection,
        event_bus: EventBus | None = None,
        *,
        agent_exists: Callable[[str], bool] | None = None,
        fts5_available: bool | None = None,
    ):
        self.conn = conn
        self.event_bus = event_bus
        self.agent_exists = agent_exists
        self._fts5_override = fts5_available

    @property
    def fts5_available(self) -> bool:
        if self._fts5_override is not None:
            return self._fts5_override
        return memory_fts5_available(self.conn)

    @property
    def retrieval_mode(self) -> str:
        return "fts5" if self.fts5_available else "deterministic_fallback"

    def status(self) -> dict[str, Any]:
        recent_count = int(
            self.conn.execute("select count(*) from memory_retrievals").fetchone()[0]
        )
        return {
            "fts5Available": self.fts5_available,
            "retrievalMode": self.retrieval_mode,
            "memoryRetrievalStatus": "implemented_all_response_agents",
            "memoryAgentRetrievalAgentCount": 37,
            "memoryAgentRetrievalAllAgents": True,
            "recentRetrievalCount": recent_count,
        }

    def retrieve(self, request: MemoryRetrievalRequest) -> dict[str, Any]:
        normalized = self._normalize_request(request)
        retrieved_at = utc_now()
        mode = self.retrieval_mode
        if normalized.private_session:
            return self._result(
                normalized,
                requested=True,
                blocked=True,
                block_reason="private_session",
                retrieval_id=None,
                retrieved_at=retrieved_at,
                mode=mode,
                candidates=[],
                items=[],
            )

        if self.fts5_available:
            candidates = self._fts_candidates(normalized)
        else:
            candidates = self._fallback_candidates(normalized)
        ranked = self._rank(candidates, normalized)[: normalized.max_items]
        retrieval_id = str(uuid4())
        items = [self._serialize_item(record, index + 1) for index, record in enumerate(ranked)]
        self._audit(normalized, retrieval_id, retrieved_at, mode, candidates, items)
        return self._result(
            normalized,
            requested=True,
            blocked=False,
            block_reason=None,
            retrieval_id=retrieval_id,
            retrieved_at=retrieved_at,
            mode=mode,
            candidates=candidates,
            items=items,
        )

    def list_retrievals(
        self,
        *,
        limit: int = 25,
        offset: int = 0,
        agent_id: str | None = None,
        project_name: str | None = None,
        purpose: str | None = None,
    ) -> list[dict[str, Any]]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= MAX_HISTORY_LIMIT:
            raise MemoryValidationError("retrieval history limit must be between 1 and 100")
        if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
            raise MemoryValidationError("retrieval history offset must be non-negative")
        agent_id = self._normalize_optional(agent_id, 200, "agent ID")
        if agent_id:
            self._validate_agent(agent_id)
        project_name = self._normalize_optional(project_name, 200, "project name")
        if purpose is not None and purpose not in PURPOSES:
            raise MemoryValidationError("unsupported retrieval purpose")
        conditions: list[str] = []
        parameters: list[Any] = []
        if agent_id:
            conditions.append("agent_id = ?")
            parameters.append(agent_id)
        if project_name:
            conditions.append("project_name = ?")
            parameters.append(project_name)
        if purpose:
            conditions.append("purpose = ?")
            parameters.append(purpose)
        where = f" where {' and '.join(conditions)}" if conditions else ""
        rows = self.conn.execute(
            "select retrieval_id, purpose, agent_id, project_name, query_hash, "
            "query_term_count, include_sensitive, retrieval_mode, candidate_count, "
            f"selected_count, created_at from memory_retrievals{where} "
            "order by created_at desc, retrieval_id desc limit ? offset ?",
            (*parameters, limit, offset),
        ).fetchall()
        return [self._serialize_history_row(row) for row in rows]

    def get_retrieval(self, retrieval_id: str) -> dict[str, Any]:
        retrieval_id = self._normalize_optional(retrieval_id, 200, "retrieval ID")
        row = self.conn.execute(
            "select retrieval_id, purpose, agent_id, project_name, query_hash, "
            "query_term_count, include_sensitive, retrieval_mode, candidate_count, "
            "selected_count, created_at from memory_retrievals where retrieval_id = ?",
            (retrieval_id,),
        ).fetchone()
        if row is None:
            raise MemoryRetrievalNotFoundError("memory retrieval not found")
        result = self._serialize_history_row(row)
        item_rows = self.conn.execute(
            "select memory_id, memory_type, scope_type, rank, text_score, scope_priority, "
            "confidence_priority, created_at from memory_retrieval_items "
            "where retrieval_id = ? order by rank, memory_id",
            (retrieval_id,),
        ).fetchall()
        result["items"] = [
            {
                "memoryId": item[0],
                "memoryType": item[1],
                "scopeType": item[2],
                "rank": int(item[3]),
                "textScore": float(item[4]),
                "scopePriority": int(item[5]),
                "confidencePriority": int(item[6]),
                "createdAt": item[7],
            }
            for item in item_rows
        ]
        return result

    def _normalize_request(self, request: MemoryRetrievalRequest) -> _NormalizedRequest:
        if request.purpose not in PURPOSES:
            raise MemoryValidationError("unsupported retrieval purpose")
        if request.purpose == "agent_response" and request.agent_id and not request.server_known_agent:
            raise MemoryValidationError("agent response retrieval requires a server-known agent ID")
        if not isinstance(request.query, str):
            raise MemoryValidationError("retrieval query must be text")
        query = " ".join(request.query.split())
        if not query:
            raise MemoryValidationError("retrieval query is required")
        if len(query) > MAX_QUERY_LENGTH:
            raise MemoryValidationError("retrieval query exceeds 1000 characters")
        terms = self._query_terms(query)
        if not terms:
            raise MemoryValidationError("retrieval query must include a word or number")
        if len(terms) > MAX_QUERY_TERMS:
            raise MemoryValidationError("retrieval query exceeds 24 distinct terms")
        if any(len(term) > MAX_TERM_LENGTH for term in terms):
            raise MemoryValidationError("retrieval query term exceeds 64 characters")
        if not isinstance(request.max_items, int) or isinstance(request.max_items, bool) or not 1 <= request.max_items <= MAX_ITEMS:
            raise MemoryValidationError("maximum retrieval items must be between 1 and 10")
        agent_id = self._normalize_optional(request.agent_id, 200, "agent ID")
        if agent_id:
            self._validate_agent(agent_id)
        project_name = self._normalize_optional(request.project_name, 200, "project name")
        return _NormalizedRequest(
            query=query,
            terms=terms,
            agent_id=agent_id,
            project_name=project_name,
            private_session=bool(request.private_session),
            include_sensitive=bool(request.include_sensitive),
            max_items=request.max_items,
            purpose=request.purpose,
        )

    def _query_terms(self, query: str) -> tuple[str, ...]:
        terms: list[str] = []
        seen: set[str] = set()
        for raw in _TOKEN_PATTERN.findall(query):
            term = raw.casefold()
            if term not in seen:
                seen.add(term)
                terms.append(term)
        return tuple(terms)

    def _fts_query(self, terms: tuple[str, ...]) -> str:
        return " OR ".join(f'"{term.replace(chr(34), chr(34) * 2)}"' for term in terms)

    def _scope_sql(self, request: _NormalizedRequest) -> tuple[str, list[Any]]:
        clauses = ["m.scope_type = 'global'"]
        parameters: list[Any] = []
        if request.project_name:
            clauses.append("(m.scope_type = 'project' and m.scope_value = ?)")
            parameters.append(request.project_name)
        if request.agent_id:
            clauses.append("(m.scope_type = 'agent' and m.scope_value = ?)")
            parameters.append(request.agent_id)
        return f"({' or '.join(clauses)})", parameters

    def _fts_candidates(self, request: _NormalizedRequest) -> list[dict[str, Any]]:
        scope_sql, scope_parameters = self._scope_sql(request)
        sensitivity_sql = "" if request.include_sensitive else " and m.sensitivity = 'standard'"
        columns = ", ".join(f"m.{column}" for column in _ROW_COLUMNS)
        rows = self.conn.execute(
            f"select {columns}, -bm25(memory_fts, 0.0, 10.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0) "
            "from memory_fts join memories m on m.rowid = memory_fts.rowid "
            "where memory_fts match ? and m.status = 'approved' "
            "and (m.expires_at is null or m.expires_at > ?) "
            f"and {scope_sql}{sensitivity_sql}",
            (self._fts_query(request.terms), utc_now(), *scope_parameters),
        ).fetchall()
        candidates: list[dict[str, Any]] = []
        for row in rows:
            record = dict(zip(_ROW_COLUMNS, row[: len(_ROW_COLUMNS)], strict=True))
            lexical_score = self._fallback_score(record, request.terms)
            bm25_score = round(float(row[-1]), 4)
            candidates.append(
                self._candidate_from_record(record, lexical_score + bm25_score, request)
            )
        return candidates

    def _fallback_candidates(self, request: _NormalizedRequest) -> list[dict[str, Any]]:
        scope_sql, scope_parameters = self._scope_sql(request)
        sensitivity_sql = "" if request.include_sensitive else " and m.sensitivity = 'standard'"
        columns = ", ".join(f"m.{column}" for column in _ROW_COLUMNS)
        rows = self.conn.execute(
            f"select {columns} from memories m where m.status = 'approved' "
            "and (m.expires_at is null or m.expires_at > ?) "
            f"and {scope_sql}{sensitivity_sql}",
            (utc_now(), *scope_parameters),
        ).fetchall()
        candidates: list[dict[str, Any]] = []
        for row in rows:
            record = dict(zip(_ROW_COLUMNS, row, strict=True))
            score = self._fallback_score(record, request.terms)
            if score > 0:
                candidates.append(self._candidate_from_record(record, score, request))
        return candidates

    def _fallback_score(self, record: dict[str, Any], terms: tuple[str, ...]) -> float:
        weighted_fields = {
            "content": 10,
            "memory_type": 3,
            "scope_type": 2,
            "scope_value": 2,
            "source_type": 1,
            "source_agent_id": 1,
            "source_reference": 1,
            "proposal_reason": 1,
        }
        score = 0
        for field, weight in weighted_fields.items():
            field_terms = self._query_terms(str(record.get(field) or ""))
            for term in terms:
                score += field_terms.count(term) * weight
        return float(score)

    def _candidate_from_row(self, row: tuple[Any, ...], score: float, request: _NormalizedRequest) -> dict[str, Any]:
        return self._candidate_from_record(
            dict(zip(_ROW_COLUMNS, row[: len(_ROW_COLUMNS)], strict=True)), score, request
        )

    def _candidate_from_record(self, record: dict[str, Any], score: float, request: _NormalizedRequest) -> dict[str, Any]:
        record = dict(record)
        record["text_score"] = round(float(score), 8)
        record["scope_priority"] = self._scope_priority(record, request)
        record["memory_type_priority"] = MEMORY_TYPE_PRIORITY.get(record["memory_type"], 0)
        record["confidence_priority"] = CONFIDENCE_PRIORITY.get(record["confidence"], 0)
        record["match_reasons"] = self._match_reasons(record, request)
        return record

    def _scope_priority(self, record: dict[str, Any], request: _NormalizedRequest) -> int:
        if record["scope_type"] == "agent" and record["scope_value"] == request.agent_id:
            return 3
        if record["scope_type"] == "project" and record["scope_value"] == request.project_name:
            return 2
        return 1

    def _rank(self, candidates: list[dict[str, Any]], request: _NormalizedRequest) -> list[dict[str, Any]]:
        return sorted(
            candidates,
            key=lambda item: (
                -item["text_score"],
                -item["scope_priority"],
                -item["memory_type_priority"],
                -item["confidence_priority"],
                _DescendingText(item["updated_at"]),
                item["memory_id"],
            ),
        )

    def _match_reasons(self, record: dict[str, Any], request: _NormalizedRequest) -> list[str]:
        content_terms = set(self._query_terms(record["content"]))
        matched = sum(1 for term in request.terms if term in content_terms)
        reasons = [f"content matched {matched} query terms"] if matched else ["metadata matched query terms"]
        if record["scope_priority"] == 3:
            reasons.append("exact agent scope")
        elif record["scope_priority"] == 2:
            reasons.append("exact project scope")
        else:
            reasons.append("global scope")
        reasons.append(f"{record['confidence']} confidence")
        if record["memory_type"] in {"constraint", "preference", "agent_instruction"}:
            reasons.append(f"{record['memory_type'].replace('_', ' ')} memory")
        return reasons

    def _serialize_item(self, record: dict[str, Any], rank: int) -> dict[str, Any]:
        return {
            "memoryId": record["memory_id"],
            "memoryType": record["memory_type"],
            "content": record["content"],
            "scopeType": record["scope_type"],
            "scopeValue": record["scope_value"],
            "sourceType": record["source_type"],
            "sourceAgentId": record["source_agent_id"],
            "sourceReference": record["source_reference"],
            "confidence": record["confidence"],
            "sensitivity": record["sensitivity"],
            "expiresAt": record["expires_at"],
            "updatedAt": record["updated_at"],
            "rank": rank,
            "textScore": record["text_score"],
            "scopePriority": record["scope_priority"],
            "memoryTypePriority": record["memory_type_priority"],
            "confidencePriority": record["confidence_priority"],
            "matchReasons": record["match_reasons"],
        }

    def _result(
        self,
        request: _NormalizedRequest,
        *,
        requested: bool,
        blocked: bool,
        block_reason: str | None,
        retrieval_id: str | None,
        retrieved_at: str,
        mode: str,
        candidates: list[dict[str, Any]],
        items: list[dict[str, Any]],
    ) -> dict[str, Any]:
        limitations = [
            "Deterministic retrieval uses approved local memories only.",
            "No model training occurred and no memory was automatically created or changed.",
        ]
        if mode == "deterministic_fallback":
            limitations.append("SQLite FTS5 is unavailable; deterministic token matching was used.")
        if blocked:
            limitations.append("Private session blocked retrieval and all retrieval auditing.")
        return {
            "requested": requested,
            "blocked": blocked,
            "blockReason": block_reason,
            "retrievalId": retrieval_id,
            "retrievedAt": retrieved_at,
            "purpose": request.purpose,
            "agentId": request.agent_id,
            "projectName": request.project_name,
            "privateSession": request.private_session,
            "includeSensitive": request.include_sensitive,
            "fts5Available": mode == "fts5",
            "retrievalMode": mode,
            "querySource": "explicit",
            "query": request.query,
            "queryTermCount": len(request.terms),
            "candidateCount": len(candidates),
            "selectedCount": len(items),
            "items": items,
            "limitations": limitations,
        }

    def _audit(
        self,
        request: _NormalizedRequest,
        retrieval_id: str,
        created_at: str,
        mode: str,
        candidates: list[dict[str, Any]],
        items: list[dict[str, Any]],
    ) -> None:
        query_hash = hashlib.sha256(request.query.encode("utf-8")).hexdigest()
        self.conn.execute(
            "insert into memory_retrievals (retrieval_id, purpose, agent_id, project_name, "
            "query_hash, query_term_count, include_sensitive, retrieval_mode, candidate_count, "
            "selected_count, created_at) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                retrieval_id,
                request.purpose,
                request.agent_id,
                request.project_name,
                query_hash,
                len(request.terms),
                int(request.include_sensitive),
                mode,
                len(candidates),
                len(items),
                created_at,
            ),
        )
        for item in items:
            self.conn.execute(
                "insert into memory_retrieval_items (retrieval_id, memory_id, memory_type, "
                "scope_type, rank, text_score, scope_priority, confidence_priority, created_at) "
                "values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    retrieval_id,
                    item["memoryId"],
                    item["memoryType"],
                    item["scopeType"],
                    item["rank"],
                    item["textScore"],
                    item["scopePriority"],
                    item["confidencePriority"],
                    created_at,
                ),
            )
            metadata = {
                "retrievalId": retrieval_id,
                "purpose": request.purpose,
                "agentId": request.agent_id,
                "projectPresent": request.project_name is not None,
                "queryHash": query_hash,
                "queryTermCount": len(request.terms),
                "retrievalMode": mode,
                "includeSensitive": request.include_sensitive,
                "memoryId": item["memoryId"],
                "memoryType": item["memoryType"],
                "scopeType": item["scopeType"],
                "rank": item["rank"],
            }
            self.conn.execute(
                "insert into memory_events (event_id, memory_id, event_type, actor, metadata, created_at) "
                "values (?, ?, 'memory.retrieved', 'memory_retrieval_service', ?, ?)",
                (str(uuid4()), item["memoryId"], json.dumps(metadata, sort_keys=True), created_at),
            )
        self.conn.commit()
        if self.event_bus is not None:
            self.event_bus.emit(
                "memory.retrieved",
                payload={
                    "retrievalId": retrieval_id,
                    "purpose": request.purpose,
                    "agentId": request.agent_id,
                    "projectPresent": request.project_name is not None,
                    "queryHash": query_hash,
                    "queryTermCount": len(request.terms),
                    "retrievalMode": mode,
                    "candidateCount": len(candidates),
                    "selectedCount": len(items),
                    "includeSensitive": request.include_sensitive,
                    "selectedMemoryIds": [item["memoryId"] for item in items],
                    "selectedMemoryTypes": [item["memoryType"] for item in items],
                    "selectedScopeTypes": [item["scopeType"] for item in items],
                },
            )

    def _serialize_history_row(self, row: tuple[Any, ...]) -> dict[str, Any]:
        return {
            "retrievalId": row[0],
            "purpose": row[1],
            "agentId": row[2],
            "projectName": row[3],
            "projectPresent": row[3] is not None,
            "queryHash": row[4],
            "queryTermCount": int(row[5]),
            "includeSensitive": bool(row[6]),
            "retrievalMode": row[7],
            "candidateCount": int(row[8]),
            "selectedCount": int(row[9]),
            "createdAt": row[10],
        }

    def _validate_agent(self, agent_id: str) -> None:
        if self.agent_exists is None or not self.agent_exists(agent_id):
            raise MemoryValidationError("agent ID must reference an existing local response agent")

    @staticmethod
    def _normalize_optional(value: Any, maximum: int, label: str) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise MemoryValidationError(f"{label} must be text")
        normalized = " ".join(value.split())
        if not normalized:
            return None
        if len(normalized) > maximum:
            raise MemoryValidationError(f"{label} exceeds the maximum length")
        return normalized


class _DescendingText:
    def __init__(self, value: Any):
        self.value = str(value or "")

    def __lt__(self, other: "_DescendingText") -> bool:
        return self.value > other.value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _DescendingText) and self.value == other.value
