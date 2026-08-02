from __future__ import annotations

import base64
import json
import math
import sqlite3
import struct
import threading
from contextlib import contextmanager
from typing import Any
from uuid import uuid4

from .events import EventBus
from .local_embedding_provider import LocalEmbeddingProviderError, LocalOllamaEmbeddingProvider
from .time_utils import utc_now


PROVIDER = "ollama_local"
PROFILE_NORMALIZATION = "l2_unit"
MAX_BATCH_SIZE = 64
SEMANTIC_CANDIDATE_LIMIT = 10_000
_PROBE_TEXT = "Jarvis local embedding capability probe."
# Float32 L2 accumulation can drift slightly at 4,096 dimensions. Five parts in
# 100,000 accepts normal round-off while rejecting materially non-unit vectors.
FLOAT32_UNIT_TOLERANCE = 5e-5


class KnowledgeEmbeddingError(RuntimeError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


class KnowledgeEmbeddingService:
    """Own optional local embedding configuration, vectors, audits, and provider calls."""

    def __init__(self, conn: sqlite3.Connection, event_bus: EventBus | None = None,
                 provider: LocalOllamaEmbeddingProvider | None = None) -> None:
        self.conn = conn
        self.event_bus = event_bus
        self.provider = provider or LocalOllamaEmbeddingProvider()
        self._mutation_lock = threading.Lock()

    def status(self) -> dict[str, Any]:
        settings = self._settings()
        counts = self._counts(settings)
        latest_row = self.conn.execute(
            "select run_id, operation, profile_id, provider, model_name, requested_chunk_count, "
            "embedded_chunk_count, skipped_chunk_count, failed_chunk_count, include_sensitive, "
            "source_id, status, error_code, created_at, completed_at from knowledge_embedding_runs "
            "order by created_at desc, run_id desc limit 1"
        ).fetchone()
        profile = self._active_profile(settings)
        configured = bool(
            settings["provider"] == PROVIDER and settings["modelName"]
            and settings["activeProfileId"] and settings["dimensions"]
            and profile is not None and profile["provider"] == PROVIDER
            and profile["modelName"] == settings["modelName"]
            and profile["dimensions"] == settings["dimensions"]
            and profile["normalization"] == PROFILE_NORMALIZATION
        )
        return {
            "provider": PROVIDER, "fixedEndpoint": self.provider.endpoint_label,
            "enabled": settings["enabled"], "embeddingsEnabled": settings["enabled"],
            "model": settings["modelName"], "dimensions": settings["dimensions"],
            "activeProfileId": settings["activeProfileId"],
            "providerConfigured": configured, **counts,
            "latestRun": self._run_dict(latest_row) if latest_row else None,
            "recentRuns": self._recent_runs(),
            "automaticEmbeddingEnabled": False, "backgroundEmbeddingEnabled": False,
            "schedulingEnabled": False,
            "modelInstallationSupported": False, "modelPullingSupported": False,
            "cloudProviderSupported": False, "apiKeySupported": False,
            "hybridRetrievalAvailable": bool(settings["enabled"] and configured),
            "phase": "v0.1E Batch 3",
            "currentSlice": "local semantic embeddings and hybrid knowledge retrieval",
            "knowledgeLibraryStatus": "implemented_with_optional_local_embeddings",
            "knowledgeRetrievalStatus": "lexical_semantic_hybrid",
            "knowledgeLexicalRetrievalEnabled": True,
            "knowledgeSemanticRetrievalImplemented": True,
            "knowledgeSemanticRetrievalEnabledByDefault": False,
            "knowledgeHybridRetrievalImplemented": True,
            "knowledgeHybridRetrievalEnabledByDefault": False,
            "knowledgeEmbeddingProvider": "ollama_local",
            "knowledgeEmbeddingEndpointPolicy": "fixed_loopback_only",
            "knowledgeEmbeddingConfigurationExplicit": True,
            "knowledgeEmbeddingAutomaticBuildEnabled": False,
            "knowledgeEmbeddingBackgroundJobsEnabled": False,
            "knowledgeEmbeddingModelPullingImplemented": False,
            "knowledgeEmbeddingModelInstallationImplemented": False,
            "knowledgeEmbeddingApiKeysSupported": False,
            "knowledgeEmbeddingCloudProvidersSupported": False,
            "knowledgeVectorStorage": "sqlite_float32_blob",
            "knowledgeVectorDatabaseEnabled": False,
            "knowledgeOriginalFileReadsDuringEmbedding": False,
            "knowledgeOriginalFileReadsDuringRetrieval": False,
            "knowledgeAutomaticScanningEnabled": False,
            "knowledgeAutomaticInjectionEnabled": False,
            "knowledgeLocalGenerativeModelEnabled": False,
            "knowledgeModelTrainingEnabled": False,
        }

    def capability(self) -> dict[str, Any]:
        settings = self._settings()
        profile = self._active_profile(settings)
        available = bool(
            settings["enabled"]
            and settings["provider"] == PROVIDER
            and settings["modelName"]
            and settings["dimensions"]
            and profile is not None
            and profile["provider"] == PROVIDER
            and profile["modelName"] == settings["modelName"]
            and profile["dimensions"] == settings["dimensions"]
            and profile["normalization"] == PROFILE_NORMALIZATION
        )
        return {
            "available": available, "enabled": settings["enabled"], "provider": PROVIDER,
            "model": settings["modelName"], "profileId": settings["activeProfileId"],
            "dimensions": settings["dimensions"],
            "errorCode": None if available else "provider_disabled",
        }

    def probe(self, model_name: str, *, private_session: bool = False) -> dict[str, Any]:
        model = self._model(model_name)
        created = utc_now()
        try:
            response = self.provider.embed(model, [_PROBE_TEXT], timeout=30)
        except LocalEmbeddingProviderError as exc:
            self._record_run("probe", model_name=model, status="failed",
                             error_code=exc.code, created_at=created)
            raise KnowledgeEmbeddingError(exc.code) from None
        self._record_run("probe", model_name=model, status="completed", created_at=created)
        return {
            "reachable": True, "validResponse": True, "model": model,
            "dimensions": response.dimensions, "provider": PROVIDER,
            "fixedEndpoint": self.provider.endpoint_label,
            "persistedVector": False, "enabled": False,
        }

    def configure(self, model_name: str, confirmation: str, actor: str) -> dict[str, Any]:
        with self._exclusive_mutation():
            return self._configure(model_name, confirmation, actor)

    def _configure(self, model_name: str, confirmation: str, actor: str) -> dict[str, Any]:
        if confirmation != "ENABLE EMBEDDINGS":
            raise KnowledgeEmbeddingError("confirmation_required")
        model = self._model(model_name)
        actor = self._actor(actor)
        created = utc_now()
        try:
            response = self.provider.embed(model, [_PROBE_TEXT], timeout=30)
        except LocalEmbeddingProviderError as exc:
            self._record_run("configure", model_name=model, status="failed",
                             error_code=exc.code, created_at=created)
            raise KnowledgeEmbeddingError(exc.code) from None
        row = self.conn.execute(
            "select profile_id from knowledge_embedding_profiles "
            "where provider = ? and model_name = ? and dimensions = ?",
            (PROVIDER, model, response.dimensions),
        ).fetchone()
        profile_id = row[0] if row else str(uuid4())
        run_id, now = str(uuid4()), utc_now()
        with self.conn:
            if row is None:
                self.conn.execute(
                    "insert into knowledge_embedding_profiles "
                    "(profile_id, provider, model_name, dimensions, normalization, created_at, last_used_at) "
                    "values (?, ?, ?, ?, ?, ?, ?)",
                    (profile_id, PROVIDER, model, response.dimensions, PROFILE_NORMALIZATION, now, now),
                )
            else:
                self.conn.execute(
                    "update knowledge_embedding_profiles set normalization = ?, last_used_at = ? "
                    "where profile_id = ?",
                    (PROFILE_NORMALIZATION, now, profile_id),
                )
            self.conn.execute(
                "update knowledge_embedding_settings set enabled = 1, provider = ?, model_name = ?, "
                "active_profile_id = ?, dimensions = ?, configured_at = ?, updated_at = ? "
                "where settings_id = 'default'",
                (PROVIDER, model, profile_id, response.dimensions, now, now),
            )
            self._insert_run(run_id, "configure", profile_id, model, 0, 0, 0, 0,
                             False, None, "completed", None, created, now)
        metadata = {"runId": run_id, "provider": PROVIDER, "modelName": model,
                    "profileId": profile_id, "dimensions": response.dimensions,
                    "actor": actor, "timestamp": now, "transition": "configured_enabled"}
        self._emit("knowledge.embeddings.configured", metadata)
        return self.status()

    def disable(self, confirmation: str, actor: str) -> dict[str, Any]:
        with self._exclusive_mutation():
            return self._disable(confirmation, actor)

    def _disable(self, confirmation: str, actor: str) -> dict[str, Any]:
        if confirmation != "DISABLE EMBEDDINGS":
            raise KnowledgeEmbeddingError("confirmation_required")
        actor, settings, now = self._actor(actor), self._settings(), utc_now()
        status, run_id = ("completed" if settings["enabled"] else "no_change"), str(uuid4())
        with self.conn:
            self.conn.execute("update knowledge_embedding_settings set enabled = 0, updated_at = ? "
                              "where settings_id = 'default'", (now,))
            self._insert_run(run_id, "disable", settings["activeProfileId"], settings["modelName"],
                             0, 0, 0, 0, False, None, status, None, now, now)
        self._emit("knowledge.embeddings.disabled",
                   {"runId": run_id, "provider": PROVIDER, "modelName": settings["modelName"],
                    "profileId": settings["activeProfileId"], "dimensions": settings["dimensions"],
                    "actor": actor, "timestamp": now, "transition": "enabled_to_disabled"})
        return self.status()

    def clear(self, scope: str, source_id: str | None, confirmation: str, actor: str) -> dict[str, Any]:
        with self._exclusive_mutation():
            return self._clear(scope, source_id, confirmation, actor)

    def _clear(self, scope: str, source_id: str | None, confirmation: str, actor: str) -> dict[str, Any]:
        if confirmation != "DELETE EMBEDDINGS":
            raise KnowledgeEmbeddingError("confirmation_required")
        if scope not in {"active_profile", "source", "all_profiles"}:
            raise KnowledgeEmbeddingError("invalid_scope")
        actor, settings = self._actor(actor), self._settings()
        if scope == "source":
            source_id = self._source_id(source_id)
            if not self.conn.execute("select 1 from knowledge_sources where source_id = ?",
                                     (source_id,)).fetchone():
                raise KnowledgeEmbeddingError("source_not_found")
            where, parameters = "source_id = ?", (source_id,)
        elif scope == "active_profile":
            where, parameters = ("profile_id = ?", (settings["activeProfileId"],)) \
                if settings["activeProfileId"] else ("0 = 1", ())
        else:
            where, parameters = "1 = 1", ()
        rows = self.conn.execute(
            f"select distinct source_id from knowledge_chunk_embeddings where {where} order by source_id",
            parameters).fetchall()
        deleted = int(self.conn.execute(
            f"select count(*) from knowledge_chunk_embeddings where {where}", parameters).fetchone()[0])
        now, run_id = utc_now(), str(uuid4())
        with self.conn:
            self.conn.execute(f"delete from knowledge_chunk_embeddings where {where}", parameters)
            self._insert_run(run_id, "clear_embeddings", settings["activeProfileId"],
                             settings["modelName"], deleted, 0, deleted, 0, False, source_id,
                             "completed" if deleted else "no_change", None, now, now)
            for row in rows:
                self._insert_source_event(
                    row[0], "knowledge.embeddings_cleared", actor,
                    {"runId": run_id, "provider": PROVIDER,
                     "profileId": settings["activeProfileId"], "sourceId": row[0],
                     "actor": actor, "timestamp": now}, now)
        self._emit("knowledge.embeddings.cleared",
                   {"runId": run_id, "provider": PROVIDER,
                    "profileId": settings["activeProfileId"], "sourceId": source_id,
                    "requestedCount": deleted, "actor": actor, "timestamp": now})
        return {"scope": scope, "sourceId": source_id,
                "deletedVectorCount": deleted, "runId": run_id}

    def rebuild_preview(self, *, source_id: str | None = None,
                        include_sensitive: bool = False, only_missing: bool = True,
                        limit: int = 32, cursor: str | None = None,
                        private_session: bool = False) -> dict[str, Any]:
        if private_session:
            raise KnowledgeEmbeddingError("private_session_blocked")
        settings = self._settings()
        self._batch_limit(limit)
        source_id = self._optional_source_id(source_id)
        if source_id and not self.conn.execute(
                "select 1 from knowledge_sources where source_id = ?", (source_id,)).fetchone():
            raise KnowledgeEmbeddingError("source_not_found")
        counts, selected, next_cursor = self._selection(
            settings, source_id, bool(include_sensitive), bool(only_missing), limit, cursor)
        return {"activeProfileId": settings["activeProfileId"], "model": settings["modelName"],
                "dimensions": settings["dimensions"], **counts,
                "selectedBatchCount": len(selected),
                "selectedSourceCount": len({row["sourceId"] for row in selected}),
                "nextCursor": next_cursor, "persisted": False, "providerCalled": False}

    def rebuild(self, *, source_id: str | None = None,
                include_sensitive: bool = False, only_missing: bool = True,
                limit: int = 32, cursor: str | None = None,
                confirmation: str, actor: str,
                private_session: bool = False) -> dict[str, Any]:
        if confirmation != "EMBED":
            raise KnowledgeEmbeddingError("confirmation_required")
        if private_session:
            raise KnowledgeEmbeddingError("private_session_blocked")
        with self._exclusive_mutation():
            return self._rebuild(
                source_id=source_id, include_sensitive=include_sensitive,
                only_missing=only_missing, limit=limit, cursor=cursor,
                confirmation=confirmation, actor=actor,
            )

    def _rebuild(self, *, source_id: str | None = None,
                 include_sensitive: bool = False, only_missing: bool = True,
                 limit: int = 32, cursor: str | None = None,
                 confirmation: str, actor: str) -> dict[str, Any]:
        if confirmation != "EMBED":
            raise KnowledgeEmbeddingError("confirmation_required")
        actor, settings = self._actor(actor), self._settings()
        if not settings["enabled"] or settings["provider"] != PROVIDER \
                or not settings["activeProfileId"] \
                or not settings["modelName"] or not settings["dimensions"]:
            raise KnowledgeEmbeddingError("provider_disabled")
        profile = self._active_profile(settings)
        if (profile is None or profile["provider"] != PROVIDER
                or profile["modelName"] != settings["modelName"]
                or profile["normalization"] != PROFILE_NORMALIZATION):
            raise KnowledgeEmbeddingError("provider_disabled")
        if profile["dimensions"] != settings["dimensions"]:
            raise KnowledgeEmbeddingError("embedding_dimension_mismatch")
        self._batch_limit(limit)
        source_id = self._optional_source_id(source_id)
        if source_id and not self.conn.execute(
                "select 1 from knowledge_sources where source_id = ?", (source_id,)).fetchone():
            raise KnowledgeEmbeddingError("source_not_found")
        counts, selected, next_cursor = self._selection(
            settings, source_id, bool(include_sensitive), bool(only_missing), limit, cursor)
        created = utc_now()
        if not selected:
            run_id = self._record_run(
                "embed_batch", profile_id=settings["activeProfileId"],
                model_name=settings["modelName"], include_sensitive=include_sensitive,
                source_id=source_id, status="no_change", created_at=created)
            return {**counts, "runId": run_id, "status": "no_change",
                    "requestedChunkCount": 0, "embeddedChunkCount": 0,
                    "skippedChunkCount": 0, "failedChunkCount": 0,
                    "nextCursor": next_cursor}
        try:
            response = self.provider.embed(
                settings["modelName"], [row["content"] for row in selected], timeout=180,
                expected_dimensions=settings["dimensions"])
        except LocalEmbeddingProviderError as exc:
            self._record_run(
                "embed_batch", profile_id=settings["activeProfileId"],
                model_name=settings["modelName"], requested=len(selected), failed=len(selected),
                include_sensitive=include_sensitive, source_id=source_id, status="failed",
                error_code=exc.code, created_at=created)
            raise KnowledgeEmbeddingError(exc.code) from None
        try:
            blobs = [
                self.serialize_vector(vector, settings["dimensions"])
                for vector in response.vectors
            ]
        except KnowledgeEmbeddingError as exc:
            self._record_run(
                "embed_batch", profile_id=settings["activeProfileId"],
                model_name=settings["modelName"], requested=len(selected), failed=len(selected),
                include_sensitive=include_sensitive, source_id=source_id, status="failed",
                error_code=exc.code, created_at=created)
            raise
        now, run_id = utc_now(), str(uuid4())
        try:
            self.conn.execute("begin immediate")
            current_settings = self._settings()
            if not self._same_configuration(settings, current_settings):
                raise KnowledgeEmbeddingError("embedding_state_changed")
            current_profile = self._active_profile(current_settings)
            if (current_profile is None or current_profile["provider"] != PROVIDER
                    or current_profile["modelName"] != settings["modelName"]
                    or current_profile["dimensions"] != settings["dimensions"]
                    or current_profile["normalization"] != PROFILE_NORMALIZATION):
                raise KnowledgeEmbeddingError("embedding_state_changed")
            for row in selected:
                current = self.conn.execute(
                    "select chunk.source_id, chunk.content_hash, source.status, source.sensitivity "
                    "from knowledge_chunks as chunk join knowledge_sources as source "
                    "on source.source_id = chunk.source_id where chunk.chunk_id = ?",
                    (row["chunkId"],),
                ).fetchone()
                if (current is None or current[0] != row["sourceId"]
                        or current[1] != row["contentHash"] or current[2] != "active"
                        or (not include_sensitive and current[3] != "standard")):
                    raise KnowledgeEmbeddingError("embedding_state_changed")
            for row, blob in zip(selected, blobs, strict=True):
                self.conn.execute(
                    "insert into knowledge_chunk_embeddings "
                    "(profile_id, chunk_id, source_id, content_hash, dimensions, vector, created_at, updated_at) "
                    "values (?, ?, ?, ?, ?, ?, ?, ?) "
                    "on conflict(profile_id, chunk_id) do update set source_id = excluded.source_id, "
                    "content_hash = excluded.content_hash, dimensions = excluded.dimensions, "
                    "vector = excluded.vector, updated_at = excluded.updated_at",
                    (settings["activeProfileId"], row["chunkId"], row["sourceId"],
                     row["contentHash"], settings["dimensions"], blob, now, now))
            self.conn.execute("update knowledge_embedding_profiles set last_used_at = ? where profile_id = ?",
                              (now, settings["activeProfileId"]))
            self._insert_run(run_id, "embed_batch", settings["activeProfileId"],
                             settings["modelName"], len(selected), len(selected), 0, 0,
                             include_sensitive, source_id, "completed", None, created, now)
            for affected_source in sorted({row["sourceId"] for row in selected}):
                source_count = sum(1 for row in selected if row["sourceId"] == affected_source)
                self._insert_source_event(
                    affected_source, "knowledge.embedded", actor,
                    {"runId": run_id, "provider": PROVIDER,
                     "modelName": settings["modelName"], "profileId": settings["activeProfileId"],
                     "dimensions": settings["dimensions"], "sourceId": affected_source,
                     "embeddedCount": source_count, "includeSensitive": bool(include_sensitive),
                      "actor": actor, "timestamp": now}, now)
            self.conn.commit()
        except KnowledgeEmbeddingError:
            self.conn.rollback()
            raise
        except sqlite3.Error:
            self.conn.rollback()
            raise KnowledgeEmbeddingError("embedding_write_failed") from None
        self._emit("knowledge.embeddings.built",
                   {"runId": run_id, "provider": PROVIDER,
                    "modelName": settings["modelName"], "profileId": settings["activeProfileId"],
                    "dimensions": settings["dimensions"], "sourceId": source_id,
                    "requestedCount": len(selected), "embeddedCount": len(selected),
                    "skippedCount": 0, "failedCount": 0,
                    "includeSensitive": bool(include_sensitive), "actor": actor, "timestamp": now})
        return {**counts, "runId": run_id, "status": "completed",
                "requestedChunkCount": len(selected), "embeddedChunkCount": len(selected),
                "skippedChunkCount": 0, "failedChunkCount": 0, "nextCursor": next_cursor}

    def embed_query(self, query: str, *, private_session: bool = False) -> dict[str, Any]:
        if private_session:
            raise KnowledgeEmbeddingError("private_session_blocked")
        settings = self._settings()
        profile = self._active_profile(settings)
        if (not settings["enabled"] or settings["provider"] != PROVIDER
                or not settings["activeProfileId"] or not settings["modelName"]
                or not settings["dimensions"] or profile is None
                or profile["provider"] != PROVIDER
                or profile["modelName"] != settings["modelName"]
                or profile["normalization"] != PROFILE_NORMALIZATION):
            raise KnowledgeEmbeddingError("provider_disabled")
        if profile["dimensions"] != settings["dimensions"]:
            raise KnowledgeEmbeddingError("embedding_dimension_mismatch")
        if not isinstance(query, str) or not query:
            raise KnowledgeEmbeddingError("embedding_input_too_large")
        try:
            response = self.provider.embed(settings["modelName"], [query], timeout=60,
                                           expected_dimensions=settings["dimensions"])
        except LocalEmbeddingProviderError as exc:
            raise KnowledgeEmbeddingError(exc.code) from None
        return {"vector": list(response.vectors[0]), "provider": PROVIDER,
                "model": settings["modelName"], "profileId": settings["activeProfileId"],
                "dimensions": settings["dimensions"]}

    def current_semantic_candidates(self, *, agent_id: str | None,
                                    project_name: str | None, include_sensitive: bool,
                                    limit: int = SEMANTIC_CANDIDATE_LIMIT + 1) -> list[dict[str, Any]]:
        settings = self._settings()
        profile = self._active_profile(settings)
        if (not settings["enabled"] or settings["provider"] != PROVIDER
                or not settings["activeProfileId"] or not settings["modelName"]
                or not settings["dimensions"] or profile is None
                or profile["provider"] != PROVIDER
                or profile["modelName"] != settings["modelName"]
                or profile["normalization"] != PROFILE_NORMALIZATION):
            raise KnowledgeEmbeddingError("provider_disabled")
        if profile["dimensions"] != settings["dimensions"]:
            raise KnowledgeEmbeddingError("embedding_dimension_mismatch")
        clauses = ["source.scope_type = 'global'"]
        parameters: list[Any] = [settings["activeProfileId"]]
        if project_name:
            clauses.append("(source.scope_type = 'project' and source.scope_value = ?)")
            parameters.append(project_name)
        if agent_id:
            clauses.append("(source.scope_type = 'agent' and source.scope_value = ?)")
            parameters.append(agent_id)
        sensitivity = "" if include_sensitive else " and source.sensitivity = 'standard'"
        rows = self.conn.execute(
            "select chunk.chunk_id, chunk.source_id, chunk.chunk_index, chunk.content, "
            "chunk.content_hash, chunk.char_start, chunk.char_end, source.title, source.source_type, "
            "source.scope_type, source.scope_value, source.sensitivity, source.media_type, "
            "source.project_name, source.relative_path, source.tags, source.updated_at, "
            "embedding.source_id, embedding.content_hash, embedding.dimensions, embedding.vector "
            "from knowledge_chunk_embeddings as embedding "
            "join knowledge_chunks as chunk on chunk.chunk_id = embedding.chunk_id "
            "join knowledge_sources as source on source.source_id = chunk.source_id "
            "where embedding.profile_id = ? and source.status = 'active' and (" +
            " or ".join(clauses) + ")" + sensitivity +
            " order by source.source_id, chunk.chunk_index, chunk.chunk_id",
            tuple(parameters))
        result: list[dict[str, Any]] = []
        for row in rows:
            if row[17] != row[1] or row[4] != row[18] or row[19] != settings["dimensions"]:
                continue
            try:
                vector = self.deserialize_vector(row[20], row[19])
            except KnowledgeEmbeddingError:
                continue
            result.append({
                "chunk_id": row[0], "source_id": row[1], "chunk_index": int(row[2]),
                "content": row[3], "content_hash": row[4], "char_start": int(row[5]),
                "char_end": int(row[6]), "title": row[7], "source_type": row[8],
                "scope_type": row[9], "scope_value": row[10], "sensitivity": row[11],
                "media_type": row[12], "project_name": row[13], "relative_path": row[14],
                "tags": row[15], "updated_at": row[16], "vector": vector})
            if len(result) >= limit:
                break
        return result

    @staticmethod
    def serialize_vector(vector: tuple[float, ...] | list[float], dimensions: int) -> bytes:
        if (not isinstance(dimensions, int) or isinstance(dimensions, bool)
                or not 8 <= dimensions <= 4096):
            raise KnowledgeEmbeddingError("embedding_dimension_mismatch")
        if not isinstance(vector, (list, tuple)) or len(vector) != dimensions:
            raise KnowledgeEmbeddingError("embedding_dimension_mismatch")
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in vector):
            raise KnowledgeEmbeddingError("invalid_provider_response")
        values = [float(value) for value in vector]
        if any(not math.isfinite(value) for value in values):
            raise KnowledgeEmbeddingError("invalid_provider_response")
        magnitude = math.sqrt(sum(value * value for value in values))
        if not math.isfinite(magnitude) or magnitude == 0.0:
            raise KnowledgeEmbeddingError("invalid_provider_response")
        normalized = [value / magnitude for value in values]
        try:
            blob = struct.pack(f"<{dimensions}f", *normalized)
            float32_values = struct.unpack(f"<{dimensions}f", blob)
        except (OverflowError, struct.error):
            raise KnowledgeEmbeddingError("invalid_provider_response") from None
        if any(not math.isfinite(value) for value in float32_values):
            raise KnowledgeEmbeddingError("invalid_provider_response")
        float32_magnitude = math.sqrt(sum(value * value for value in float32_values))
        if (not math.isfinite(float32_magnitude) or float32_magnitude == 0.0
                or abs(float32_magnitude - 1.0) > FLOAT32_UNIT_TOLERANCE):
            raise KnowledgeEmbeddingError("invalid_provider_response")
        return blob

    @staticmethod
    def deserialize_vector(value: Any, dimensions: int) -> list[float]:
        if (not isinstance(dimensions, int) or isinstance(dimensions, bool)
                or not 8 <= dimensions <= 4096):
            raise KnowledgeEmbeddingError("wrong_dimension")
        if not isinstance(value, (bytes, bytearray, memoryview)):
            raise KnowledgeEmbeddingError("invalid_vector_blob_length")
        raw = bytes(value)
        if len(raw) != dimensions * 4:
            raise KnowledgeEmbeddingError("invalid_vector_blob_length")
        try:
            vector = list(struct.unpack(f"<{dimensions}f", raw))
        except struct.error:
            raise KnowledgeEmbeddingError("invalid_vector_blob_length") from None
        if len(vector) != dimensions:
            raise KnowledgeEmbeddingError("invalid_vector_blob_length")
        if any(not math.isfinite(item) for item in vector):
            raise KnowledgeEmbeddingError("non_finite_vector")
        magnitude = math.sqrt(sum(item * item for item in vector))
        if not math.isfinite(magnitude):
            raise KnowledgeEmbeddingError("non_finite_vector")
        if magnitude == 0.0:
            raise KnowledgeEmbeddingError("zero_vector")
        if abs(magnitude - 1.0) > FLOAT32_UNIT_TOLERANCE:
            raise KnowledgeEmbeddingError("non_unit_vector")
        return [item / magnitude for item in vector]

    def _settings(self) -> dict[str, Any]:
        row = self.conn.execute(
            "select enabled, provider, model_name, active_profile_id, dimensions, configured_at, updated_at "
            "from knowledge_embedding_settings where settings_id = 'default'").fetchone()
        if row is None:
            raise KnowledgeEmbeddingError("provider_disabled")
        return {"enabled": bool(row[0]), "provider": row[1], "modelName": row[2],
                "activeProfileId": row[3], "dimensions": row[4],
                "configuredAt": row[5], "updatedAt": row[6]}

    def _active_profile(self, settings: dict[str, Any]) -> dict[str, Any] | None:
        profile_id = settings.get("activeProfileId")
        if not profile_id:
            return None
        row = self.conn.execute(
            "select profile_id, provider, model_name, dimensions, normalization "
            "from knowledge_embedding_profiles where profile_id = ?",
            (profile_id,),
        ).fetchone()
        if row is None:
            return None
        return {"profileId": row[0], "provider": row[1], "modelName": row[2],
                "dimensions": row[3], "normalization": row[4]}

    @staticmethod
    def _same_configuration(before: dict[str, Any], after: dict[str, Any]) -> bool:
        keys = ("enabled", "provider", "modelName", "activeProfileId", "dimensions", "updatedAt")
        return all(before.get(key) == after.get(key) for key in keys)

    def _recent_runs(self, limit: int = 25) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "select run_id, operation, profile_id, provider, model_name, requested_chunk_count, "
            "embedded_chunk_count, skipped_chunk_count, failed_chunk_count, include_sensitive, "
            "source_id, status, error_code, created_at, completed_at "
            "from knowledge_embedding_runs order by created_at desc, run_id desc limit ?",
            (limit,),
        ).fetchall()
        return [self._run_dict(row) for row in rows]

    def _counts(self, settings: dict[str, Any]) -> dict[str, int]:
        total = int(self.conn.execute("select count(*) from knowledge_chunks").fetchone()[0])
        active = int(self.conn.execute(
            "select count(*) from knowledge_chunks as chunk join knowledge_sources as source "
            "on source.source_id = chunk.source_id where source.status = 'active'").fetchone()[0])
        sensitive = int(self.conn.execute(
            "select count(*) from knowledge_chunks as chunk join knowledge_sources as source "
            "on source.source_id = chunk.source_id where source.status = 'active' "
            "and source.sensitivity = 'sensitive'").fetchone()[0])
        active_profile_id = settings["activeProfileId"]
        profile = self._active_profile(settings)
        profile_current = bool(
            profile is not None and settings["provider"] == PROVIDER
            and profile["provider"] == PROVIDER
            and profile["modelName"] == settings["modelName"]
            and profile["dimensions"] == settings["dimensions"]
            and profile["normalization"] == PROFILE_NORMALIZATION
        )
        rows = self.conn.execute(
            "select chunk.source_id, chunk.content_hash, embedding.source_id, "
            "embedding.content_hash, embedding.dimensions, embedding.vector "
            "from knowledge_chunks as chunk join knowledge_sources as source "
            "on source.source_id = chunk.source_id left join knowledge_chunk_embeddings as embedding "
            "on embedding.chunk_id = chunk.chunk_id and embedding.profile_id = ? "
            "where source.status = 'active' order by chunk.chunk_id",
            (active_profile_id,),
        ).fetchall()
        current = missing = stale_content = invalid = wrong_dimension = 0
        invalid_blob_length = non_finite = zero = non_unit = wrong_source = 0
        for row in rows:
            if row[2] is None:
                missing += 1
                continue
            if row[2] != row[0]:
                wrong_source += 1
                invalid += 1
                continue
            if row[3] != row[1]:
                stale_content += 1
                continue
            if not profile_current or row[4] != settings["dimensions"]:
                wrong_dimension += 1
                invalid += 1
                continue
            try:
                self.deserialize_vector(row[5], row[4])
            except KnowledgeEmbeddingError as exc:
                invalid += 1
                if exc.code == "invalid_vector_blob_length":
                    invalid_blob_length += 1
                elif exc.code == "non_finite_vector":
                    non_finite += 1
                elif exc.code == "zero_vector":
                    zero += 1
                elif exc.code == "non_unit_vector":
                    non_unit += 1
                else:
                    wrong_dimension += 1
                continue
            current += 1
        total_stored = int(self.conn.execute(
            "select count(*) from knowledge_chunk_embeddings").fetchone()[0])
        if active_profile_id:
            wrong_profile = int(self.conn.execute(
                "select count(*) from knowledge_chunk_embeddings where profile_id <> ?",
                (active_profile_id,),
            ).fetchone()[0])
        else:
            wrong_profile = total_stored
        disabled_vectors = int(self.conn.execute(
            "select count(*) from knowledge_chunk_embeddings as embedding "
            "join knowledge_chunks as chunk on chunk.chunk_id = embedding.chunk_id "
            "join knowledge_sources as source on source.source_id = chunk.source_id "
            "where source.status <> 'active'").fetchone()[0])
        return {"totalChunks": total, "activeSourceChunks": active,
                "embeddedCurrentChunks": current, "missingChunks": missing,
                "staleChunks": stale_content, "staleContentChunks": stale_content,
                "invalidVectorChunks": invalid, "wrongProfileVectorCount": wrong_profile,
                "disabledSourceVectorCount": disabled_vectors,
                "wrongDimensionVectorCount": wrong_dimension,
                "invalidBlobLengthVectorCount": invalid_blob_length,
                "nonFiniteVectorCount": non_finite, "zeroVectorCount": zero,
                "nonUnitVectorCount": non_unit, "wrongSourceVectorCount": wrong_source,
                "totalStoredVectors": total_stored,
                "sensitiveActiveChunks": sensitive,
                "sensitiveChunksExcluded": sensitive}

    def _selection(self, settings: dict[str, Any], source_id: str | None,
                   include_sensitive: bool, only_missing: bool, limit: int,
                   cursor: str | None) -> tuple[dict[str, int], list[dict[str, Any]], str | None]:
        if not settings["activeProfileId"]:
            return ({"eligibleChunkCount": 0, "currentEmbeddedCount": 0,
                      "missingCount": 0, "staleCount": 0,
                      "invalidVectorCount": 0,
                      "sensitiveChunksExcludedCount": 0}, [], None)
        after = self._decode_cursor(cursor)
        parameters: list[Any] = [settings["activeProfileId"]]
        where = ["source.status = 'active'"]
        if source_id:
            where.append("chunk.source_id = ?")
            parameters.append(source_id)
        sensitive_excluded = 0
        if not include_sensitive:
            sensitive_parameters: list[Any] = []
            sensitive_where = ["source.status = 'active'", "source.sensitivity = 'sensitive'"]
            if source_id:
                sensitive_where.append("chunk.source_id = ?")
                sensitive_parameters.append(source_id)
            sensitive_excluded = int(self.conn.execute(
                "select count(*) from knowledge_chunks as chunk join knowledge_sources as source "
                "on source.source_id = chunk.source_id where " + " and ".join(sensitive_where),
                tuple(sensitive_parameters)).fetchone()[0])
            where.append("source.sensitivity = 'standard'")
        rows = self.conn.execute(
            "select chunk.chunk_id, chunk.source_id, chunk.chunk_index, chunk.content, "
            "chunk.content_hash, embedding.source_id, embedding.content_hash, "
            "embedding.dimensions, embedding.vector "
            "from knowledge_chunks as chunk join knowledge_sources as source "
            "on source.source_id = chunk.source_id left join knowledge_chunk_embeddings as embedding "
            "on embedding.chunk_id = chunk.chunk_id and embedding.profile_id = ? where " +
            " and ".join(where) + " order by chunk.source_id, chunk.chunk_index, chunk.chunk_id",
            tuple(parameters)).fetchall()
        profile = self._active_profile(settings)
        profile_current = bool(
            profile is not None and settings["provider"] == PROVIDER
            and profile["provider"] == PROVIDER
            and profile["modelName"] == settings["modelName"]
            and profile["dimensions"] == settings["dimensions"]
            and profile["normalization"] == PROFILE_NORMALIZATION
        )
        eligible = current = missing = stale = invalid = 0
        selectable: list[dict[str, Any]] = []
        for row in rows:
            eligible += 1
            state = "missing"
            if row[5] is not None:
                if row[5] != row[1] or not profile_current or row[7] != settings["dimensions"]:
                    state = "invalid"
                elif row[4] != row[6]:
                    state = "stale"
                else:
                    try:
                        self.deserialize_vector(row[8], row[7])
                    except KnowledgeEmbeddingError:
                        state = "invalid"
                    else:
                        state = "current"
            if state == "current":
                current += 1
            elif state == "missing":
                missing += 1
            elif state == "stale":
                stale += 1
            else:
                invalid += 1
            key = (row[1], int(row[2]), row[0])
            if after is not None and key <= after:
                continue
            if only_missing and state == "current":
                continue
            selectable.append({"chunkId": row[0], "sourceId": row[1],
                               "chunkIndex": int(row[2]), "content": row[3],
                               "contentHash": row[4]})
        has_more, selected = len(selectable) > limit, selectable[:limit]
        next_cursor = self._encode_cursor(selected[-1]) if has_more and selected else None
        counts = {"eligibleChunkCount": eligible, "currentEmbeddedCount": current,
                   "missingCount": missing, "staleCount": stale,
                   "invalidVectorCount": invalid,
                   "sensitiveChunksExcludedCount": sensitive_excluded}
        return counts, selected, next_cursor

    @staticmethod
    def _encode_cursor(row: dict[str, Any]) -> str:
        raw = json.dumps([row["sourceId"], row["chunkIndex"], row["chunkId"]],
                         separators=(",", ":"))
        return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii").rstrip("=")

    @staticmethod
    def _decode_cursor(cursor: str | None) -> tuple[str, int, str] | None:
        if cursor is None:
            return None
        if not isinstance(cursor, str) or not cursor or len(cursor) > 1000:
            raise KnowledgeEmbeddingError("invalid_cursor")
        try:
            padded = cursor + "=" * (-len(cursor) % 4)
            value = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8"))
        except (ValueError, UnicodeError, json.JSONDecodeError):
            raise KnowledgeEmbeddingError("invalid_cursor") from None
        if (not isinstance(value, list) or len(value) != 3
                or not isinstance(value[0], str) or not isinstance(value[1], int)
                or isinstance(value[1], bool) or not isinstance(value[2], str)):
            raise KnowledgeEmbeddingError("invalid_cursor")
        return value[0], value[1], value[2]

    def _record_run(self, operation: str, *, profile_id: str | None = None,
                    model_name: str | None = None, requested: int = 0,
                    embedded: int = 0, skipped: int = 0, failed: int = 0,
                    include_sensitive: bool = False, source_id: str | None = None,
                    status: str, error_code: str | None = None,
                    created_at: str | None = None) -> str:
        run_id, created, completed = str(uuid4()), created_at or utc_now(), utc_now()
        with self.conn:
            self._insert_run(run_id, operation, profile_id, model_name, requested, embedded,
                             skipped, failed, include_sensitive, source_id, status,
                             error_code, created, completed)
        return run_id

    def _insert_run(self, run_id: str, operation: str, profile_id: str | None,
                    model_name: str | None, requested: int, embedded: int,
                    skipped: int, failed: int, include_sensitive: bool,
                    source_id: str | None, status: str, error_code: str | None,
                    created_at: str, completed_at: str) -> None:
        self.conn.execute(
            "insert into knowledge_embedding_runs "
            "(run_id, operation, profile_id, provider, model_name, requested_chunk_count, "
            "embedded_chunk_count, skipped_chunk_count, failed_chunk_count, include_sensitive, "
            "source_id, status, error_code, created_at, completed_at) "
            "values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (run_id, operation, profile_id, PROVIDER, model_name, requested, embedded,
             skipped, failed, int(include_sensitive), source_id, status, error_code,
             created_at, completed_at))

    @staticmethod
    def _run_dict(row: tuple[Any, ...]) -> dict[str, Any]:
        return {"runId": row[0], "operation": row[1], "profileId": row[2],
                "provider": row[3], "model": row[4], "requestedChunkCount": int(row[5]),
                "embeddedChunkCount": int(row[6]), "skippedChunkCount": int(row[7]),
                "failedChunkCount": int(row[8]), "includeSensitive": bool(row[9]),
                "sourceId": row[10], "status": row[11], "errorCode": row[12],
                "createdAt": row[13], "completedAt": row[14]}

    def _insert_source_event(self, source_id: str, event_type: str, actor: str,
                             metadata: dict[str, Any], created_at: str) -> None:
        self.conn.execute(
            "insert into knowledge_events (event_id, source_id, event_type, actor, metadata, created_at) "
            "values (?, ?, ?, ?, ?, ?)",
            (str(uuid4()), source_id, event_type, actor,
             json.dumps(metadata, sort_keys=True), created_at))

    def _emit(self, event_type: str, metadata: dict[str, Any]) -> None:
        if self.event_bus is not None:
            self.event_bus.emit(event_type, payload=metadata)

    @contextmanager
    def _exclusive_mutation(self):
        if not self._mutation_lock.acquire(blocking=False):
            raise KnowledgeEmbeddingError("embedding_rebuild_in_progress")
        try:
            yield
        finally:
            self._mutation_lock.release()

    def _model(self, value: Any) -> str:
        try:
            return self.provider.validate_model_name(value)
        except LocalEmbeddingProviderError as exc:
            raise KnowledgeEmbeddingError(exc.code) from None

    @staticmethod
    def _actor(value: Any) -> str:
        if not isinstance(value, str):
            raise KnowledgeEmbeddingError("invalid_actor")
        normalized = " ".join(value.split())
        if not normalized or len(normalized) > 200:
            raise KnowledgeEmbeddingError("invalid_actor")
        return normalized

    @staticmethod
    def _source_id(value: Any) -> str:
        if not isinstance(value, str) or not value or len(value) > 200:
            raise KnowledgeEmbeddingError("source_not_found")
        return value

    def _optional_source_id(self, value: Any) -> str | None:
        return None if value is None else self._source_id(value)

    @staticmethod
    def _batch_limit(value: Any) -> int:
        if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= MAX_BATCH_SIZE:
            raise KnowledgeEmbeddingError("invalid_batch_limit")
        return value
