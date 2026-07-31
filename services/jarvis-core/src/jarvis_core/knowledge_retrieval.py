from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
from dataclasses import dataclass
from typing import Any, Callable
from uuid import uuid4

from .db import knowledge_fts5_available
from .events import EventBus
from .knowledge import KnowledgeValidationError
from .knowledge_embeddings import (
    KnowledgeEmbeddingError,
    KnowledgeEmbeddingService,
    SEMANTIC_CANDIDATE_LIMIT,
)
from .time_utils import utc_now


PURPOSES = frozenset({"manual_preview", "agent_response"})
RETRIEVAL_MODES = frozenset({"fts5", "deterministic_fallback", "semantic", "hybrid", "lexical_fallback"})
REQUESTED_MODES = frozenset({"lexical", "semantic", "hybrid"})
MAX_QUERY_LENGTH = 1_000
MAX_QUERY_TERMS = 24
MAX_TERM_LENGTH = 64
MAX_ITEMS = 10
MAX_HISTORY_LIMIT = 100
FALLBACK_CANDIDATE_LIMIT = 5_000
MAX_CHUNKS_PER_SOURCE = 3
HYBRID_POOL_LIMIT = 100
RRF_K = 60
LEXICAL_WEIGHT = 0.55
SEMANTIC_WEIGHT = 0.45
_TOKEN_PATTERN = re.compile(r"[^\W_]+", re.UNICODE)
_ROW_COLUMNS = (
    "chunk_id",
    "source_id",
    "chunk_index",
    "content",
    "char_start",
    "char_end",
    "title",
    "source_type",
    "scope_type",
    "scope_value",
    "sensitivity",
    "media_type",
    "project_name",
    "relative_path",
    "tags",
    "updated_at",
)
_SELECT_COLUMNS = """
  chunk.chunk_id, chunk.source_id, chunk.chunk_index, chunk.content,
  chunk.char_start, chunk.char_end, source.title, source.source_type,
  source.scope_type, source.scope_value, source.sensitivity, source.media_type,
  source.project_name, source.relative_path, source.tags, source.updated_at
"""


class KnowledgeRetrievalNotFoundError(KeyError):
    pass


class KnowledgeSemanticUnavailableError(RuntimeError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class KnowledgeRetrievalRequest:
    query: str
    agent_id: str | None = None
    project_name: str | None = None
    private_session: bool = False
    include_sensitive: bool = False
    max_items: int = 5
    purpose: str = "manual_preview"
    server_known_agent: bool = False
    mode: str = "lexical"


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
    mode: str


class KnowledgeRetrievalService:
    """Rank stored knowledge chunks deterministically and retain redacted audits."""

    def __init__(
        self,
        conn: sqlite3.Connection,
        event_bus: EventBus | None = None,
        *,
        agent_exists: Callable[[str], bool] | None = None,
        fts5_available: bool | None = None,
        embedding_service: KnowledgeEmbeddingService | None = None,
    ):
        self.conn = conn
        self.event_bus = event_bus
        self.agent_exists = agent_exists
        self._fts5_override = fts5_available
        self.embedding_service = embedding_service

    @property
    def fts5_available(self) -> bool:
        if self._fts5_override is not None:
            return self._fts5_override
        return knowledge_fts5_available(self.conn)

    @property
    def retrieval_mode(self) -> str:
        return "fts5" if self.fts5_available else "deterministic_fallback"

    def status(self) -> dict[str, Any]:
        retrieval_count = int(
            self.conn.execute("select count(*) from knowledge_retrievals").fetchone()[0]
        )
        return {
            "fts5Available": self.fts5_available,
            "retrievalMode": self.retrieval_mode,
            "recentRetrievalCount": retrieval_count,
            "knowledgeRetrievalStatus": "lexical_semantic_hybrid",
            "knowledgeRetrievalMode": "lexical_semantic_hybrid",
            "knowledgeLexicalRetrievalEnabled": True,
            "knowledgeSemanticRetrievalImplemented": True,
            "knowledgeSemanticRetrievalEnabledByDefault": False,
            "knowledgeHybridRetrievalImplemented": True,
            "knowledgeHybridRetrievalEnabledByDefault": False,
            "knowledgeRetrievalAuditImplemented": True,
            "knowledgeAgentRetrievalEnabled": True,
            "knowledgeAgentRetrievalAgentCount": 37,
            "knowledgeAgentRetrievalAllAgents": True,
            "knowledgeRetrievalRequiresExplicitOptIn": True,
            "knowledgeRetrievalRequiresExplicitQuery": True,
            "knowledgeSensitiveRetrievalDefaultEnabled": False,
            "knowledgeOriginalFileReadsDuringRetrieval": False,
        }

    def retrieve(self, request: KnowledgeRetrievalRequest) -> dict[str, Any]:
        normalized = self._normalize_request(request)
        retrieved_at = utc_now()
        if normalized.private_session:
            return self._result(
                normalized, blocked=True, block_reason="private_session", retrieval_id=None,
                retrieved_at=retrieved_at, mode=self.retrieval_mode, candidates=[], items=[],
                candidate_limit_reached=False,
            )
        if normalized.mode == "semantic":
            return self._retrieve_semantic(normalized, retrieved_at)
        if normalized.mode == "hybrid":
            return self._retrieve_hybrid(normalized, retrieved_at)
        return self._retrieve_lexical(normalized, retrieved_at)

    def _retrieve_lexical(self, request: _NormalizedRequest, retrieved_at: str,
                          *, actual_mode: str | None = None,
                          limitations: list[str] | None = None) -> dict[str, Any]:
        lexical_mode, ranked, candidate_limit_reached = self._lexical_ranked(request)
        for rank, candidate in enumerate(ranked, 1):
            candidate["lexical_rank"] = rank
        selected = self._select_diverse(ranked, request.max_items)
        items = self._serialize_items(selected)
        retrieval_id = str(uuid4())
        mode = actual_mode or lexical_mode
        self._audit(request, retrieval_id, retrieved_at, mode, ranked, items)
        return self._result(
            request, blocked=False, block_reason=None, retrieval_id=retrieval_id,
            retrieved_at=retrieved_at, mode=mode, candidates=ranked, items=items,
            candidate_limit_reached=candidate_limit_reached,
            additional_limitations=limitations or [], lexical_candidate_count=len(ranked),
        )

    def _retrieve_semantic(self, request: _NormalizedRequest,
                           retrieved_at: str) -> dict[str, Any]:
        try:
            ranked, metadata = self._semantic_ranked(request)
        except KnowledgeEmbeddingError as exc:
            raise KnowledgeSemanticUnavailableError(exc.code) from None
        selected = self._select_diverse(ranked, request.max_items)
        items = self._serialize_items(selected)
        retrieval_id = str(uuid4())
        self._audit(request, retrieval_id, retrieved_at, "semantic", ranked, items,
                    profile_id=metadata["profileId"])
        return self._result(
            request, blocked=False, block_reason=None, retrieval_id=retrieval_id,
            retrieved_at=retrieved_at, mode="semantic", candidates=ranked, items=items,
            candidate_limit_reached=False, semantic_metadata=metadata,
            semantic_candidate_count=len(ranked),
            semantic_candidate_limit_reached=metadata["candidateLimitReached"],
        )

    def _retrieve_hybrid(self, request: _NormalizedRequest,
                         retrieved_at: str) -> dict[str, Any]:
        lexical_mode, lexical_ranked, candidate_limit_reached = self._lexical_ranked(request)
        for rank, candidate in enumerate(lexical_ranked, 1):
            candidate["lexical_rank"] = rank
        lexical_pool = lexical_ranked[:HYBRID_POOL_LIMIT]
        try:
            semantic_ranked, metadata = self._semantic_ranked(request)
        except KnowledgeEmbeddingError as exc:
            limitation = ("Hybrid semantic capability was unavailable (" + exc.code +
                          "); actual retrieval used lexical ranking only.")
            return self._retrieve_lexical(
                request, retrieved_at, actual_mode="lexical_fallback",
                limitations=[limitation],
            )
        semantic_pool = semantic_ranked[:HYBRID_POOL_LIMIT]
        union: dict[str, dict[str, Any]] = {}
        for candidate in lexical_pool:
            union[candidate["chunk_id"]] = dict(candidate)
        for candidate in semantic_pool:
            existing = union.get(candidate["chunk_id"])
            if existing is None:
                union[candidate["chunk_id"]] = dict(candidate)
            else:
                for key in ("semantic_rank", "semantic_score", "ranking_signals"):
                    existing[key] = candidate.get(key)
        for candidate in union.values():
            lexical_rank = candidate.get("lexical_rank")
            semantic_rank = candidate.get("semantic_rank")
            candidate["hybrid_score"] = (
                (LEXICAL_WEIGHT / (RRF_K + lexical_rank) if lexical_rank else 0.0)
                + (SEMANTIC_WEIGHT / (RRF_K + semantic_rank) if semantic_rank else 0.0)
            )
            signals = list(candidate.get("ranking_signals") or [])
            if lexical_rank:
                signals.append(f"lexical reciprocal rank {lexical_rank}")
            if semantic_rank:
                signals.append(f"semantic reciprocal rank {semantic_rank}")
            candidate["ranking_signals"] = signals
        ranked = sorted(
            union.values(),
            key=lambda item: (
                -item["hybrid_score"], -item["scope_priority"],
                -(item.get("semantic_score") if item.get("semantic_score") is not None else -2.0),
                item.get("lexical_rank") or 10**9, _DescendingText(item["updated_at"]),
                item["chunk_index"], item["source_id"], item["chunk_id"],
            ),
        )
        selected = self._select_diverse(ranked, request.max_items)
        items = self._serialize_items(selected)
        retrieval_id = str(uuid4())
        self._audit(request, retrieval_id, retrieved_at, "hybrid", ranked, items,
                    profile_id=metadata["profileId"])
        return self._result(
            request, blocked=False, block_reason=None, retrieval_id=retrieval_id,
            retrieved_at=retrieved_at, mode="hybrid", candidates=ranked, items=items,
            candidate_limit_reached=candidate_limit_reached,
            semantic_metadata=metadata, lexical_candidate_count=len(lexical_ranked),
            semantic_candidate_count=len(semantic_ranked),
            semantic_candidate_limit_reached=metadata["candidateLimitReached"],
        )

    def _lexical_ranked(self, request: _NormalizedRequest) -> tuple[str, list[dict[str, Any]], bool]:
        mode = self.retrieval_mode
        if mode == "fts5":
            candidates, limit_reached = self._fts_candidates(request), False
        else:
            candidates, limit_reached = self._fallback_candidates(request)
        return mode, self._rank(candidates), limit_reached

    def _semantic_ranked(self, request: _NormalizedRequest) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        if self.embedding_service is None:
            raise KnowledgeEmbeddingError("provider_disabled")
        query = self.embedding_service.embed_query(request.query, private_session=False)
        query_vector = query["vector"]
        try:
            records = self.embedding_service.current_semantic_candidates(
                agent_id=request.agent_id, project_name=request.project_name,
                include_sensitive=request.include_sensitive,
                limit=SEMANTIC_CANDIDATE_LIMIT + 1,
            )
            limit_reached = len(records) > SEMANTIC_CANDIDATE_LIMIT
            candidates: list[dict[str, Any]] = []
            for record in records[:SEMANTIC_CANDIDATE_LIMIT]:
                vector = record.pop("vector")
                score = sum(left * right for left, right in zip(query_vector, vector, strict=True))
                for index in range(len(vector)):
                    vector[index] = 0.0
                if not math.isfinite(score) or score < -1.000001 or score > 1.000001:
                    continue
                score = max(-1.0, min(1.0, score))
                candidate = self._semantic_candidate(record, score, request)
                candidates.append(candidate)
            ranked = sorted(
                candidates,
                key=lambda item: (
                    -item["semantic_score"], -item["scope_priority"],
                    _DescendingText(item["updated_at"]), item["chunk_index"],
                    item["source_id"], item["chunk_id"],
                ),
            )
            for rank, candidate in enumerate(ranked, 1):
                candidate["semantic_rank"] = rank
            return ranked, {
                "available": True, "used": True, "provider": query["provider"],
                "model": query["model"], "profileId": query["profileId"],
                "dimensions": query["dimensions"], "candidateLimitReached": limit_reached,
            }
        finally:
            for index in range(len(query_vector)):
                query_vector[index] = 0.0

    def _semantic_candidate(self, record: dict[str, Any], score: float,
                            request: _NormalizedRequest) -> dict[str, Any]:
        candidate = dict(record)
        candidate["scope_priority"] = self._scope_priority(candidate, request)
        candidate["semantic_score"] = round(score, 8)
        candidate["text_score"] = 0.0
        candidate["matched_term_count"] = 0
        candidate["match_reasons"] = [
            "local semantic similarity rank",
            "exact agent scope" if candidate["scope_priority"] == 3 else
            "exact project scope" if candidate["scope_priority"] == 2 else "global scope",
            "sensitive source explicitly included" if candidate["sensitivity"] == "sensitive"
            else "standard source",
        ]
        candidate["ranking_signals"] = list(candidate["match_reasons"])
        try:
            candidate["tags_list"] = json.loads(candidate["tags"])
        except (TypeError, json.JSONDecodeError):
            candidate["tags_list"] = []
        return candidate
    def list_retrievals(
        self,
        *,
        limit: int = 25,
        offset: int = 0,
        agent_id: str | None = None,
        project_name: str | None = None,
        purpose: str | None = None,
        retrieval_mode: str | None = None,
    ) -> list[dict[str, Any]]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= MAX_HISTORY_LIMIT:
            raise KnowledgeValidationError("retrieval history limit must be between 1 and 100")
        if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
            raise KnowledgeValidationError("retrieval history offset must be non-negative")
        agent_id = self._normalize_optional(agent_id, 200, "agent ID")
        if agent_id:
            self._validate_agent(agent_id)
        project_name = self._normalize_optional(project_name, 200, "project name")
        if purpose is not None and purpose not in PURPOSES:
            raise KnowledgeValidationError("unsupported retrieval purpose")
        if retrieval_mode is not None and retrieval_mode not in RETRIEVAL_MODES:
            raise KnowledgeValidationError("unsupported retrieval mode")
        conditions: list[str] = []
        parameters: list[Any] = []
        for column, value in (
            ("agent_id", agent_id),
            ("project_name", project_name),
            ("purpose", purpose),
            ("retrieval_mode", retrieval_mode),
        ):
            if value:
                conditions.append(f"{column} = ?")
                parameters.append(value)
        where = f" where {' and '.join(conditions)}" if conditions else ""
        rows = self.conn.execute(
            "select retrieval_id, purpose, agent_id, project_name, query_hash, "
            "query_term_count, include_sensitive, retrieval_mode, candidate_chunk_count, "
            "candidate_source_count, selected_chunk_count, selected_source_count, created_at "
            f"from knowledge_retrievals{where} "
            "order by created_at desc, retrieval_id desc limit ? offset ?",
            (*parameters, limit, offset),
        ).fetchall()
        return [self._serialize_history_row(row) for row in rows]

    def get_retrieval(self, retrieval_id: str) -> dict[str, Any]:
        retrieval_id = self._normalize_optional(retrieval_id, 200, "retrieval ID")
        if not retrieval_id:
            raise KnowledgeValidationError("retrieval ID is required")
        row = self.conn.execute(
            "select retrieval_id, purpose, agent_id, project_name, query_hash, "
            "query_term_count, include_sensitive, retrieval_mode, candidate_chunk_count, "
            "candidate_source_count, selected_chunk_count, selected_source_count, created_at "
            "from knowledge_retrievals where retrieval_id = ?",
            (retrieval_id,),
        ).fetchone()
        if row is None:
            raise KnowledgeRetrievalNotFoundError("knowledge retrieval not found")
        result = self._serialize_history_row(row)
        item_rows = self.conn.execute(
            """
            select item.chunk_id, item.source_id, item.rank, item.text_score,
              item.scope_priority, item.source_rank, item.chunk_index, item.created_at,
              source.title, source.status, source.scope_type, source.scope_value,
              source.sensitivity, chunk.chunk_id, score.profile_id, score.lexical_rank,
              score.semantic_rank, score.semantic_score, score.hybrid_score
            from knowledge_retrieval_items as item
            left join knowledge_sources as source on source.source_id = item.source_id
            left join knowledge_chunks as chunk on chunk.chunk_id = item.chunk_id
            left join knowledge_retrieval_scores as score on score.retrieval_id = item.retrieval_id
              and score.chunk_id = item.chunk_id
            where item.retrieval_id = ?
            order by item.rank, item.source_id, item.chunk_id
            """,
            (retrieval_id,),
        ).fetchall()
        result["items"] = [
            {
                "chunkId": item[0],
                "sourceId": item[1],
                "rank": int(item[2]),
                "textScore": float(item[3]),
                "scopePriority": int(item[4]),
                "sourceRank": int(item[5]),
                "chunkIndex": int(item[6]),
                "createdAt": item[7],
                "sourceAvailable": item[8] is not None,
                "chunkAvailable": item[13] is not None,
                "currentTitle": item[8],
                "currentStatus": item[9],
                "currentScopeType": item[10],
                "currentScopeValue": item[11],
                "currentSensitivity": item[12],
                "profileId": item[14],
                "lexicalRank": item[15],
                "semanticRank": item[16],
                "semanticScore": item[17],
                "hybridScore": item[18],
            }
            for item in item_rows
        ]
        return result

    def _normalize_request(self, request: KnowledgeRetrievalRequest) -> _NormalizedRequest:
        if request.purpose not in PURPOSES:
            raise KnowledgeValidationError("unsupported retrieval purpose")
        if request.purpose == "agent_response" and not request.server_known_agent:
            raise KnowledgeValidationError("agent response retrieval requires a server-known agent ID")
        if request.mode not in REQUESTED_MODES:
            raise KnowledgeValidationError("unsupported requested retrieval mode")
        if not isinstance(request.query, str):
            raise KnowledgeValidationError("retrieval query must be text")
        query = " ".join(request.query.split())
        if not query:
            raise KnowledgeValidationError("retrieval query is required")
        if len(query) > MAX_QUERY_LENGTH:
            raise KnowledgeValidationError("retrieval query exceeds 1000 characters")
        terms = self._query_terms(query)
        if not terms:
            raise KnowledgeValidationError("retrieval query must include a word or number")
        if len(terms) > MAX_QUERY_TERMS:
            raise KnowledgeValidationError("retrieval query exceeds 24 distinct terms")
        if any(len(term) > MAX_TERM_LENGTH for term in terms):
            raise KnowledgeValidationError("retrieval query term exceeds 64 characters")
        if not isinstance(request.max_items, int) or isinstance(request.max_items, bool) or not 1 <= request.max_items <= MAX_ITEMS:
            raise KnowledgeValidationError("maximum retrieval items must be between 1 and 10")
        agent_id = self._normalize_optional(request.agent_id, 200, "agent ID")
        if request.purpose == "agent_response" and not agent_id:
            raise KnowledgeValidationError("agent response retrieval requires an agent ID")
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
            mode=request.mode,
        )

    def _query_terms(self, value: str) -> tuple[str, ...]:
        terms: list[str] = []
        seen: set[str] = set()
        for raw in _TOKEN_PATTERN.findall(value):
            term = raw.casefold()
            if term not in seen:
                seen.add(term)
                terms.append(term)
        return tuple(terms)

    @staticmethod
    def _fts_query(terms: tuple[str, ...]) -> str:
        return " OR ".join(f'"{term.replace(chr(34), chr(34) * 2)}"' for term in terms)

    def _scope_sql(self, request: _NormalizedRequest) -> tuple[str, list[Any]]:
        clauses = ["source.scope_type = 'global'"]
        parameters: list[Any] = []
        if request.project_name:
            clauses.append("(source.scope_type = 'project' and source.scope_value = ?)")
            parameters.append(request.project_name)
        if request.agent_id:
            clauses.append("(source.scope_type = 'agent' and source.scope_value = ?)")
            parameters.append(request.agent_id)
        return f"({' or '.join(clauses)})", parameters

    def _fts_candidates(self, request: _NormalizedRequest) -> list[dict[str, Any]]:
        scope_sql, scope_parameters = self._scope_sql(request)
        sensitivity_sql = "" if request.include_sensitive else " and source.sensitivity = 'standard'"
        rows = self.conn.execute(
            f"select {_SELECT_COLUMNS}, "
            "bm25(knowledge_chunks_fts, 0.0, 0.0, 10.0, 3.0, 2.0, 0.25, 0.25) "
            "from knowledge_chunks_fts "
            "join knowledge_chunks as chunk on chunk.chunk_id = knowledge_chunks_fts.chunk_id "
            "join knowledge_sources as source on source.source_id = chunk.source_id "
            "where knowledge_chunks_fts match ? and source.status = 'active' "
            f"and {scope_sql}{sensitivity_sql}",
            (self._fts_query(request.terms), *scope_parameters),
        ).fetchall()
        candidates: list[dict[str, Any]] = []
        for row in rows:
            record = dict(zip(_ROW_COLUMNS, row[: len(_ROW_COLUMNS)], strict=True))
            candidates.append(self._candidate(record, -float(row[-1]), request))
        return candidates

    def _fallback_candidates(
        self, request: _NormalizedRequest
    ) -> tuple[list[dict[str, Any]], bool]:
        scope_sql, scope_parameters = self._scope_sql(request)
        sensitivity_sql = "" if request.include_sensitive else " and source.sensitivity = 'standard'"
        rows = self.conn.execute(
            f"select {_SELECT_COLUMNS} from knowledge_chunks as chunk "
            "join knowledge_sources as source on source.source_id = chunk.source_id "
            "where source.status = 'active' "
            f"and {scope_sql}{sensitivity_sql} "
            "order by source.updated_at desc, source.source_id, chunk.chunk_index, chunk.chunk_id "
            f"limit {FALLBACK_CANDIDATE_LIMIT + 1}",
            tuple(scope_parameters),
        ).fetchall()
        candidate_limit_reached = len(rows) > FALLBACK_CANDIDATE_LIMIT
        candidates: list[dict[str, Any]] = []
        for row in rows[:FALLBACK_CANDIDATE_LIMIT]:
            record = dict(zip(_ROW_COLUMNS, row, strict=True))
            score = self._fallback_score(record, request.terms)
            if score > 0:
                candidates.append(self._candidate(record, score, request))
        return candidates, candidate_limit_reached

    def _fallback_score(self, record: dict[str, Any], terms: tuple[str, ...]) -> float:
        content_terms = set(self._query_terms(str(record.get("content") or "")))
        title_terms = set(self._query_terms(str(record.get("title") or "")))
        tag_terms = set(self._query_terms(str(record.get("tags") or "")))
        return float(
            sum(10 for term in terms if term in content_terms)
            + sum(3 for term in terms if term in title_terms)
            + sum(2 for term in terms if term in tag_terms)
        )

    def _candidate(
        self, record: dict[str, Any], text_score: float, request: _NormalizedRequest
    ) -> dict[str, Any]:
        candidate = dict(record)
        candidate["text_score"] = round(float(text_score), 8)
        candidate["scope_priority"] = self._scope_priority(candidate, request)
        content_terms = set(self._query_terms(str(candidate["content"])))
        title_terms = set(self._query_terms(str(candidate["title"])))
        tag_terms = set(self._query_terms(str(candidate["tags"])))
        candidate["content_matches"] = sum(1 for term in request.terms if term in content_terms)
        candidate["title_matches"] = sum(1 for term in request.terms if term in title_terms)
        candidate["tag_matches"] = sum(1 for term in request.terms if term in tag_terms)
        candidate["matched_term_count"] = sum(
            1
            for term in request.terms
            if term in content_terms or term in title_terms or term in tag_terms
        )
        candidate["match_reasons"] = self._match_reasons(candidate)
        try:
            candidate["tags_list"] = json.loads(candidate["tags"])
        except (TypeError, json.JSONDecodeError):
            candidate["tags_list"] = []
        return candidate

    @staticmethod
    def _scope_priority(record: dict[str, Any], request: _NormalizedRequest) -> int:
        if record["scope_type"] == "agent" and record["scope_value"] == request.agent_id:
            return 3
        if record["scope_type"] == "project" and record["scope_value"] == request.project_name:
            return 2
        return 1

    @staticmethod
    def _match_reasons(record: dict[str, Any]) -> list[str]:
        reasons: list[str] = []
        if record["content_matches"]:
            reasons.append(f"chunk content matched {record['content_matches']} query terms")
        if record["title_matches"]:
            reasons.append(f"source title matched {record['title_matches']} query terms")
        if record["tag_matches"]:
            reasons.append(f"source tags matched {record['tag_matches']} query terms")
        if record["scope_priority"] == 3:
            reasons.append("exact agent scope")
        elif record["scope_priority"] == 2:
            reasons.append("exact project scope")
        else:
            reasons.append("global scope")
        reasons.append(
            "sensitive source explicitly included"
            if record["sensitivity"] == "sensitive"
            else "standard source"
        )
        return reasons

    @staticmethod
    def _rank(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(
            candidates,
            key=lambda item: (
                -item["text_score"],
                -item["scope_priority"],
                -item["matched_term_count"],
                _DescendingText(item["updated_at"]),
                item["chunk_index"],
                item["source_id"],
                item["chunk_id"],
            ),
        )

    @staticmethod
    def _select_diverse(
        ranked: list[dict[str, Any]], max_items: int
    ) -> list[dict[str, Any]]:
        counts: dict[str, int] = {}
        selected: list[dict[str, Any]] = []
        for candidate in ranked:
            source_id = candidate["source_id"]
            if counts.get(source_id, 0) >= MAX_CHUNKS_PER_SOURCE:
                continue
            selected.append(candidate)
            counts[source_id] = counts.get(source_id, 0) + 1
            if len(selected) >= max_items:
                break
        return selected

    def _serialize_items(self, selected: list[dict[str, Any]]) -> list[dict[str, Any]]:
        source_ranks: dict[str, int] = {}
        source_counts: dict[str, int] = {}
        for record in selected:
            source_counts[record["source_id"]] = source_counts.get(record["source_id"], 0) + 1
        items: list[dict[str, Any]] = []
        for rank, record in enumerate(selected, 1):
            source_id = record["source_id"]
            if source_id not in source_ranks:
                source_ranks[source_id] = len(source_ranks) + 1
            items.append(
                {
                    "chunkId": record["chunk_id"],
                    "sourceId": source_id,
                    "sourceTitle": record["title"],
                    "sourceType": record["source_type"],
                    "scopeType": record["scope_type"],
                    "scopeValue": record["scope_value"],
                    "sensitivity": record["sensitivity"],
                    "mediaType": record["media_type"],
                    "projectName": record["project_name"],
                    "relativePath": record["relative_path"],
                    "tags": record["tags_list"],
                    "chunkIndex": int(record["chunk_index"]),
                    "charStart": int(record["char_start"]),
                    "charEnd": int(record["char_end"]),
                    "content": record["content"],
                    "rank": rank,
                    "textScore": record["text_score"],
                    "scopePriority": record["scope_priority"],
                    "matchedTermCount": record["matched_term_count"],
                    "matchReasons": list(record["match_reasons"]),
                    "lexicalRank": record.get("lexical_rank"),
                    "semanticRank": record.get("semantic_rank"),
                    "semanticScore": record.get("semantic_score"),
                    "hybridScore": record.get("hybrid_score"),
                    "rankingSignals": list(record.get("ranking_signals") or record["match_reasons"]),
                    "sourceUpdatedAt": record["updated_at"],
                    "citationLabel": f"[K{rank}]",
                    "sourceRank": source_ranks[source_id],
                    "sourceSelectedCount": source_counts[source_id],
                }
            )
        return items

    def _result(
        self,
        request: _NormalizedRequest,
        *,
        blocked: bool,
        block_reason: str | None,
        retrieval_id: str | None,
        retrieved_at: str,
        mode: str,
        candidates: list[dict[str, Any]],
        items: list[dict[str, Any]],
        candidate_limit_reached: bool,
        semantic_metadata: dict[str, Any] | None = None,
        lexical_candidate_count: int = 0,
        semantic_candidate_count: int = 0,
        semantic_candidate_limit_reached: bool = False,
        additional_limitations: list[str] | None = None,
    ) -> dict[str, Any]:
        source_ids = {item["sourceId"] for item in items}
        diversity: list[dict[str, Any]] = []
        for source_id in sorted(
            source_ids,
            key=lambda value: min(item["rank"] for item in items if item["sourceId"] == value),
        ):
            source_items = [item for item in items if item["sourceId"] == source_id]
            diversity.append({"sourceId": source_id, "selectedChunkCount": len(source_items),
                              "bestRank": min(item["rank"] for item in source_items)})
        limitations = [
            "Retrieval searched active stored SQLite chunks only.",
            "No knowledge source was modified.",
            "No original project file was opened during retrieval.",
            "No model training occurred.",
            "No local generative model was used.",
        ]
        if request.mode == "lexical":
            limitations.append("Lexical retrieval did not contact an embedding provider.")
        if mode in {"semantic", "hybrid"}:
            limitations.extend([
                "Semantic similarity does not prove correctness.",
                "Embeddings were produced by a user-enabled local model.",
                "No cloud model was contacted.",
            ])
        if mode == "hybrid":
            limitations.append("Hybrid retrieval combined lexical and semantic rank signals.")
        if request.purpose == "manual_preview":
            limitations.append("No response agent was invoked.")
        if mode == "deterministic_fallback":
            limitations.append("SQLite FTS5 is unavailable; deterministic lexical ranking was used.")
        if candidate_limit_reached:
            limitations.append("Deterministic fallback candidates were bounded at 5000 chunks; ranking is not exhaustive.")
        if semantic_candidate_limit_reached:
            limitations.append("Semantic candidates were bounded at 10000 current vectors; ranking is not exhaustive.")
        if blocked:
            limitations.append("Private session blocked retrieval and auditing; stored sources were not deleted.")
        limitations.extend(additional_limitations or [])
        semantic = semantic_metadata or {}
        capability = (self.embedding_service.capability()
                      if self.embedding_service is not None and not blocked else {"available": False})
        semantic_used = mode in {"semantic", "hybrid"} and bool(semantic.get("used"))
        return {
            "requested": True, "used": bool(items) and not blocked,
            "blocked": blocked, "blockReason": block_reason,
            "retrievalId": retrieval_id, "retrievedAt": retrieved_at,
            "purpose": request.purpose, "agentId": request.agent_id,
            "projectName": request.project_name, "privateSession": request.private_session,
            "includeSensitive": request.include_sensitive,
            "requestedMode": request.mode, "fts5Available": self.fts5_available,
            "retrievalMode": mode, "semanticAvailable": bool(semantic.get("available", capability.get("available"))),
            "semanticUsed": semantic_used,
            "embeddingProvider": semantic.get("provider") if semantic_used else None,
            "embeddingModel": semantic.get("model") if semantic_used else None,
            "embeddingProfileId": semantic.get("profileId") if semantic_used else None,
            "embeddingDimensions": semantic.get("dimensions") if semantic_used else None,
            "querySource": "explicit", "query": request.query,
            "queryTermCount": len(request.terms),
            "candidateChunkCount": 0 if blocked else len(candidates),
            "candidateSourceCount": 0 if blocked else len({item["source_id"] for item in candidates}),
            "candidateLimitReached": candidate_limit_reached,
            "lexicalCandidateCount": 0 if blocked else lexical_candidate_count,
            "semanticCandidateCount": 0 if blocked else semantic_candidate_count,
            "semanticCandidateLimitReached": semantic_candidate_limit_reached,
            "selectedChunkCount": len(items), "selectedSourceCount": len(source_ids),
            "sourceDiversity": diversity, "items": items, "limitations": limitations,
        }

    def _audit(
        self,
        request: _NormalizedRequest,
        retrieval_id: str,
        created_at: str,
        mode: str,
        candidates: list[dict[str, Any]],
        items: list[dict[str, Any]],
        *,
        profile_id: str | None = None,
    ) -> None:
        query_hash = hashlib.sha256(request.query.encode("utf-8")).hexdigest()
        candidate_source_count = len({candidate["source_id"] for candidate in candidates})
        selected_source_count = len({item["sourceId"] for item in items})
        with self.conn:
            self.conn.execute(
                "insert into knowledge_retrievals (retrieval_id, purpose, agent_id, project_name, "
                "query_hash, query_term_count, include_sensitive, retrieval_mode, "
                "candidate_chunk_count, candidate_source_count, selected_chunk_count, "
                "selected_source_count, created_at) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
                    candidate_source_count,
                    len(items),
                    selected_source_count,
                    created_at,
                ),
            )
            for item in items:
                self.conn.execute(
                    "insert into knowledge_retrieval_items (retrieval_id, chunk_id, source_id, "
                    "rank, text_score, scope_priority, source_rank, chunk_index, created_at) "
                    "values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        retrieval_id,
                        item["chunkId"],
                        item["sourceId"],
                        item["rank"],
                        item["textScore"],
                        item["scopePriority"],
                        item["sourceRank"],
                        item["chunkIndex"],
                        created_at,
                    ),
                )
                if (item.get("lexicalRank") is not None or item.get("semanticRank") is not None
                        or item.get("hybridScore") is not None):
                    self.conn.execute(
                        "insert into knowledge_retrieval_scores "
                        "(retrieval_id, chunk_id, profile_id, lexical_rank, semantic_rank, "
                        "semantic_score, hybrid_score, created_at) values (?, ?, ?, ?, ?, ?, ?, ?)",
                        (retrieval_id, item["chunkId"], profile_id, item.get("lexicalRank"),
                         item.get("semanticRank"), item.get("semanticScore"),
                         item.get("hybridScore"), created_at),
                    )
            for source_id in dict.fromkeys(item["sourceId"] for item in items):
                source_items = [item for item in items if item["sourceId"] == source_id]
                metadata = {
                    "retrievalId": retrieval_id,
                    "purpose": request.purpose,
                    "agentId": request.agent_id,
                    "projectPresent": request.project_name is not None,
                    "queryHash": query_hash,
                    "queryTermCount": len(request.terms),
                    "requestedMode": request.mode,
                    "retrievalMode": mode,
                    "profileId": profile_id,
                    "candidateChunkCount": len(candidates),
                    "candidateSourceCount": candidate_source_count,
                    "selectedChunkCount": len(items),
                    "selectedSourceCount": selected_source_count,
                    "includeSensitive": request.include_sensitive,
                    "sourceId": source_id,
                    "selectedChunkIds": [item["chunkId"] for item in source_items],
                    "selectedChunkCountForSource": len(source_items),
                    "bestRank": min(item["rank"] for item in source_items),
                    "scopeType": source_items[0]["scopeType"],
                    "sensitivity": source_items[0]["sensitivity"],
                }
                self.conn.execute(
                    "insert into knowledge_events (event_id, source_id, event_type, actor, "
                    "metadata, created_at) values (?, ?, 'knowledge.retrieved', "
                    "'knowledge_retrieval_service', ?, ?)",
                    (str(uuid4()), source_id, json.dumps(metadata, sort_keys=True), created_at),
                )
        if self.event_bus is not None:
            self.event_bus.emit(
                "knowledge.retrieved",
                payload={
                    "retrievalId": retrieval_id,
                    "purpose": request.purpose,
                    "agentId": request.agent_id,
                    "projectPresent": request.project_name is not None,
                    "queryHash": query_hash,
                    "queryTermCount": len(request.terms),
                    "requestedMode": request.mode,
                    "retrievalMode": mode,
                    "profileId": profile_id,
                    "candidateChunkCount": len(candidates),
                    "candidateSourceCount": candidate_source_count,
                    "selectedChunkCount": len(items),
                    "selectedSourceCount": selected_source_count,
                    "includeSensitive": request.include_sensitive,
                    "selectedSourceIds": list(dict.fromkeys(item["sourceId"] for item in items)),
                    "selectedChunkIds": [item["chunkId"] for item in items],
                },
            )

    @staticmethod
    def _serialize_history_row(row: tuple[Any, ...]) -> dict[str, Any]:
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
            "candidateChunkCount": int(row[8]),
            "candidateSourceCount": int(row[9]),
            "selectedChunkCount": int(row[10]),
            "selectedSourceCount": int(row[11]),
            "createdAt": row[12],
        }

    def _validate_agent(self, agent_id: str) -> None:
        if self.agent_exists is None or not self.agent_exists(agent_id):
            raise KnowledgeValidationError(
                "agent ID must reference an existing local response agent"
            )

    @staticmethod
    def _normalize_optional(value: Any, maximum: int, label: str) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise KnowledgeValidationError(f"{label} must be text")
        normalized = " ".join(value.split())
        if not normalized:
            return None
        if len(normalized) > maximum:
            raise KnowledgeValidationError(f"{label} exceeds the maximum length")
        return normalized


class _DescendingText:
    def __init__(self, value: Any):
        self.value = str(value or "")

    def __lt__(self, other: "_DescendingText") -> bool:
        return self.value > other.value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _DescendingText) and self.value == other.value
