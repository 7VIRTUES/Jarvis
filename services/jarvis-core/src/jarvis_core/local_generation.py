from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import threading
from typing import Any
from uuid import uuid4

from .events import EventBus
from .local_generation_provider import (
    GENERATION_ENDPOINT,
    GenerationCancelHandle,
    LocalGenerationProvider,
    LocalGenerationProviderError,
    validate_model_name,
)
from .prompt_assembly import GENERATED_RESPONSE_SCHEMA, PromptAssemblyError, assemble_generation_prompt
from .time_utils import utc_now


PROVIDER = "ollama_local"
STRUCTURED_OUTPUT_MODE = "json_schema"
MAX_CONCURRENCY = 1

_ERROR_MESSAGES = {
    "generation_disabled": "Local generation is disabled.",
    "provider_unavailable": "The fixed-loopback local generation provider is unavailable.",
    "model_unavailable": "The configured local generation model is unavailable.",
    "provider_timeout": "The local generation provider timed out.",
    "provider_redirect_blocked": "A provider redirect was blocked.",
    "generation_request_too_large": "The bounded generation request is too large.",
    "generation_response_too_large": "The provider response exceeded the safe limit.",
    "invalid_provider_response": "The provider returned an invalid response.",
    "invalid_model_name": "The local model name is invalid.",
    "invalid_structured_output": "The generated structured response is invalid.",
    "output_too_large": "The generated output exceeded the selected limit.",
    "unexpected_tool_call": "The provider attempted an unsupported tool call.",
    "unexpected_image_output": "The provider returned unsupported image output.",
    "generation_in_progress": "Another local generation call is already active.",
    "profile_not_found": "The requested local generation profile was not found.",
    "generation_state_changed": "Generation settings changed while the response was being produced.",
    "full_prompt_preview_blocked_private_session": "Full prompt preview is blocked in private sessions.",
    "generation_cancelled": "Local generation was cancelled by the user.",
    "no_active_generation": "No active local generation was found to cancel.",
    "cancellation_not_available": "The active generation cannot be cancelled.",
    "expected_runtime_id_mismatch": "The requested runtime ID does not match the active generation.",
}


class LocalGenerationError(RuntimeError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code

    def safe_detail(self) -> dict[str, str]:
        return {"error": self.code, "message": _ERROR_MESSAGES.get(self.code, "Local generation failed safely.")}


class ActiveGenerationRuntime:
    """Ephemeral process-memory representation of the single active generation."""

    def __init__(
        self,
        *,
        runtime_id: str,
        run_id: str | None = None,
        response_id: str | None = None,
        agent_id: str | None = None,
        profile_id: str | None = None,
        model_name: str,
        purpose: str,
        phase: str = "acquiring",
        started_at: str,
        private_session: bool = False,
        cancel_handle: GenerationCancelHandle | None = None,
    ) -> None:
        self.runtime_id = runtime_id
        self.run_id = run_id
        self.response_id = response_id
        self.agent_id = agent_id
        self.profile_id = profile_id
        self.model_name = model_name
        self.purpose = purpose
        self.phase = phase
        self.started_at = started_at
        self.cancellation_requested = False
        self.cancellable = True
        self.private_session = private_session
        self.cancel_handle = cancel_handle

    def to_dict(self) -> dict[str, Any]:
        return {
            "active": True,
            "runtimeId": self.runtime_id,
            "runId": self.run_id,
            "responseId": self.response_id,
            "agentId": self.agent_id,
            "profileId": self.profile_id,
            "modelName": self.model_name,
            "purpose": self.purpose,
            "phase": self.phase,
            "startedAt": self.started_at,
            "cancellationRequested": self.cancellation_requested,
            "cancellable": self.cancellable,
            "privateSession": self.private_session,
        }


class LocalGenerationService:
    def __init__(
        self,
        conn: sqlite3.Connection,
        event_bus: EventBus | None = None,
        provider: LocalGenerationProvider | None = None,
    ) -> None:
        self.conn = conn
        self.event_bus = event_bus
        self.provider = provider or LocalGenerationProvider()
        self._generation_lock = threading.Lock()
        self._active_count = 0
        self._active_count_lock = threading.Lock()
        self._active_runtime: ActiveGenerationRuntime | None = None
        self._runtime_lock = threading.Lock()

    def status(self) -> dict[str, Any]:
        settings = self._settings()
        recent = self.conn.execute(
            """
            select
              sum(case when status = 'completed' then 1 else 0 end),
              sum(case when status = 'failed' then 1 else 0 end)
            from local_generation_runs
            where datetime(replace(substr(created_at, 1, 19), 'T', ' ')) >= datetime('now', '-7 days')
            """
        ).fetchone()
        latest = self.conn.execute(
            f"select {_RUN_COLUMNS} from local_generation_runs order by created_at desc, run_id desc limit 1"
        ).fetchone()
        with self._active_count_lock:
            active_count = self._active_count
        return {
            "implemented": True,
            "enabled": settings["enabled"],
            "provider": settings["provider"],
            "fixedEndpoint": GENERATION_ENDPOINT,
            "modelName": settings["modelName"],
            "activeProfileId": settings["activeProfileId"],
            "contextCharacterLimit": settings["contextCharacterLimit"],
            "maximumOutputCharacters": settings["maximumOutputCharacters"],
            "temperature": settings["temperature"],
            "keepAliveSeconds": settings["keepAliveSeconds"],
            "configuredAt": settings["configuredAt"],
            "updatedAt": settings["updatedAt"],
            "activeGenerationCount": active_count,
            "maximumConcurrency": MAX_CONCURRENCY,
            "recentCompletedCount": int((recent or (0, 0))[0] or 0),
            "recentFailedCount": int((recent or (0, 0))[1] or 0),
            "latestRun": self._serialize_run(latest) if latest else None,
            "activeRuntime": self.active_runtime_status(),
            "automaticGeneration": False,
            "backgroundGeneration": False,
            "queue": False,
            "cancellation": True,
            "cancellationImplemented": True,
            "automaticRetry": False,
            "streaming": False,
            "toolCalling": False,
            "cloud": False,
            "apiKeys": False,
            "modelInstallOrPull": False,
            "training": False,
            "promptPersistence": False,
            "outputPersistence": False,
            "thinkingPersistence": False,
            "privateAudit": False,
        }

    def active_runtime_status(self) -> dict[str, Any]:
        with self._runtime_lock:
            if self._active_runtime is not None:
                return self._active_runtime.to_dict()
            return {"active": False, "status": "idle"}

    def cancel_active(
        self,
        *,
        confirmation: str,
        expected_runtime_id: str | None = None,
        actor: str = "local_user",
    ) -> dict[str, Any]:
        if confirmation != "CANCEL LOCAL GENERATION":
            raise LocalGenerationError("invalid_structured_output")
        with self._runtime_lock:
            if self._active_runtime is None or self._active_runtime.phase in ("completed", "failed", "cancelled"):
                return {
                    "cancelled": False,
                    "status": "no_active_generation",
                    "message": "No active local generation was found to cancel.",
                }
            if expected_runtime_id and expected_runtime_id.strip():
                if self._active_runtime.runtime_id != expected_runtime_id.strip():
                    return {
                        "cancelled": False,
                        "status": "runtime_id_mismatch",
                        "message": "The expected runtime ID does not match the active generation.",
                    }
            runtime = self._active_runtime
            runtime.cancellation_requested = True
            runtime.phase = "cancelling"
            if runtime.cancel_handle is not None:
                runtime.cancel_handle.cancel()
            if not runtime.private_session and runtime.run_id:
                self._emit(
                    "generation.cancellation_requested",
                    {
                        "runId": runtime.run_id,
                        "runtimeId": runtime.runtime_id,
                        "modelName": runtime.model_name,
                        "actor": self._actor(actor),
                    },
                )
            return {
                "cancelled": True,
                "status": "cancelling",
                "runtimeId": runtime.runtime_id,
                "modelName": runtime.model_name,
            }

    def probe(self, *, model_name: str, actor: str = "local_user") -> dict[str, Any]:
        model = self._model(model_name)
        self._acquire_generation()
        run_id = str(uuid4())
        runtime_id = str(uuid4())
        started = utc_now()
        cancel_handle = GenerationCancelHandle()
        self._set_active_runtime(
            ActiveGenerationRuntime(
                runtime_id=runtime_id,
                run_id=run_id,
                model_name=model,
                purpose="probe",
                phase="probing",
                started_at=started,
                private_session=False,
                cancel_handle=cancel_handle,
            )
        )
        try:
            self._insert_run(
                run_id=run_id,
                purpose="probe",
                provider=PROVIDER,
                model_name=model,
                requested_mode="probe",
                actual_mode="probe",
                output_style="fixed_probe",
                status="started",
                created_at=started,
            )
            result = self.provider.probe(model=model, cancel_handle=cancel_handle)
            completed = utc_now()
            self._complete_run(
                run_id,
                status="completed",
                output_char_count=len(result["status"]),
                thinking_discarded=bool(result["thinkingDiscarded"]),
                completed_at=completed,
            )
            self._emit(
                "generation.probed",
                {"runId": run_id, "provider": PROVIDER, "modelName": model, "status": "completed", "actor": self._actor(actor)},
            )
            return {
                "status": "ok",
                "provider": PROVIDER,
                "modelName": model,
                "runId": run_id,
                "thinkingDiscarded": bool(result["thinkingDiscarded"]),
                "enabled": self._settings()["enabled"],
                "persisted": True,
            }
        except (LocalGenerationProviderError, LocalGenerationError) as exc:
            error = self._as_error(exc)
            status = "cancelled" if error.code == "generation_cancelled" else "failed"
            self._complete_run(run_id, status=status, error_code=error.code, completed_at=utc_now())
            self._emit(
                "generation.failed",
                {"runId": run_id, "purpose": "probe", "provider": PROVIDER, "modelName": model, "errorCode": error.code},
            )
            raise error from None
        finally:
            self._clear_active_runtime()
            self._release_generation()

    def configure(
        self,
        *,
        model_name: str,
        context_char_limit: int,
        max_output_chars: int,
        temperature: float,
        keep_alive_seconds: int,
        confirmation: str,
        actor: str = "local_user",
    ) -> dict[str, Any]:
        if confirmation != "ENABLE LOCAL GENERATION":
            raise LocalGenerationError("generation_disabled")
        model = self._model(model_name)
        context_limit = self._bounded_int(context_char_limit, 8_000, 120_000, "generation_request_too_large")
        output_limit = self._bounded_int(max_output_chars, 500, 12_000, "output_too_large")
        selected_temperature = self._bounded_float(temperature, 0.0, 1.0)
        keep_alive = self._bounded_int(keep_alive_seconds, 0, 3_600, "invalid_structured_output")
        self._acquire_generation()
        probe_run_id = str(uuid4())
        runtime_id = str(uuid4())
        started = utc_now()
        cancel_handle = GenerationCancelHandle()
        self._set_active_runtime(
            ActiveGenerationRuntime(
                runtime_id=runtime_id,
                run_id=probe_run_id,
                model_name=model,
                purpose="configure_probe",
                phase="probing",
                started_at=started,
                private_session=False,
                cancel_handle=cancel_handle,
            )
        )
        try:
            self._insert_run(
                run_id=probe_run_id,
                purpose="configure_probe",
                provider=PROVIDER,
                model_name=model,
                requested_mode="probe",
                actual_mode="probe",
                output_style="fixed_probe",
                status="started",
                created_at=started,
            )
            probe = self.provider.probe(model=model, cancel_handle=cancel_handle)
            self._complete_run(
                probe_run_id,
                status="completed",
                output_char_count=len(probe["status"]),
                thinking_discarded=bool(probe["thinkingDiscarded"]),
                completed_at=utc_now(),
            )
            profile_id = self._profile_id(model, context_limit, output_limit, selected_temperature, keep_alive)
            now = utc_now()
            with self.conn:
                self.conn.execute(
                    """
                    insert or ignore into local_generation_profiles (
                      profile_id, provider, model_name, context_char_limit, max_output_chars,
                      default_temperature, keep_alive_seconds, structured_output_mode, created_at, last_used_at
                    ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, null)
                    """,
                    (
                        profile_id,
                        PROVIDER,
                        model,
                        context_limit,
                        output_limit,
                        selected_temperature,
                        keep_alive,
                        STRUCTURED_OUTPUT_MODE,
                        now,
                    ),
                )
                self.conn.execute(
                    """
                    update local_generation_settings set
                      enabled = 1, provider = ?, model_name = ?, active_profile_id = ?,
                      context_char_limit = ?, max_output_chars = ?, default_temperature = ?,
                      keep_alive_seconds = ?, configured_at = coalesce(configured_at, ?), updated_at = ?
                    where settings_id = 'default'
                    """,
                    (
                        PROVIDER,
                        model,
                        profile_id,
                        context_limit,
                        output_limit,
                        selected_temperature,
                        keep_alive,
                        now,
                        now,
                    ),
                )
            self._emit(
                "generation.probed",
                {"runId": probe_run_id, "purpose": "configure_probe", "provider": PROVIDER, "modelName": model, "status": "completed"},
            )
            self._emit(
                "generation.configured",
                {"provider": PROVIDER, "modelName": model, "profileId": profile_id, "actor": self._actor(actor)},
            )
            return self.status()
        except (LocalGenerationProviderError, LocalGenerationError) as exc:
            error = self._as_error(exc)
            status = "cancelled" if error.code == "generation_cancelled" else "failed"
            self._complete_run(probe_run_id, status=status, error_code=error.code, completed_at=utc_now())
            self._emit(
                "generation.failed",
                {"runId": probe_run_id, "purpose": "configure_probe", "provider": PROVIDER, "modelName": model, "errorCode": error.code},
            )
            raise error from None
        finally:
            self._clear_active_runtime()
            self._release_generation()

    def disable(self, *, confirmation: str, actor: str = "local_user") -> dict[str, Any]:
        if confirmation != "DISABLE LOCAL GENERATION":
            raise LocalGenerationError("generation_disabled")
        with self.conn:
            self.conn.execute(
                "update local_generation_settings set enabled = 0, updated_at = ? where settings_id = 'default'",
                (utc_now(),),
            )
        self._emit("generation.disabled", {"actor": self._actor(actor), "providerCalled": False})
        return self.status()

    def unload(
        self,
        *,
        confirmation: str,
        profile_id: str | None = None,
        actor: str = "local_user",
    ) -> dict[str, Any]:
        if confirmation != "UNLOAD LOCAL MODEL":
            raise LocalGenerationError("invalid_structured_output")
        settings = self._settings()
        profile = self._profile(profile_id or settings["activeProfileId"])
        self._acquire_generation()
        runtime_id = str(uuid4())
        cancel_handle = GenerationCancelHandle()
        self._set_active_runtime(
            ActiveGenerationRuntime(
                runtime_id=runtime_id,
                model_name=profile["modelName"],
                profile_id=profile["profileId"],
                purpose="unload",
                phase="unloading",
                started_at=utc_now(),
                cancel_handle=cancel_handle,
            )
        )
        try:
            result = self.provider.unload(model=profile["modelName"], cancel_handle=cancel_handle)
            self._emit(
                "generation.unloaded",
                {"provider": PROVIDER, "modelName": profile["modelName"], "profileId": profile["profileId"], "actor": self._actor(actor)},
            )
            return {**result, "profileId": profile["profileId"], "processKilled": False, "modelDeleted": False}
        except (LocalGenerationProviderError, LocalGenerationError) as exc:
            raise self._as_error(exc) from None
        finally:
            self._clear_active_runtime()
            self._release_generation()

    def list_profiles(self) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            select profile_id, provider, model_name, context_char_limit, max_output_chars,
              default_temperature, keep_alive_seconds, structured_output_mode, created_at, last_used_at
            from local_generation_profiles order by created_at desc, profile_id
            """
        ).fetchall()
        return [self._serialize_profile(row) for row in rows]

    def list_runs(self, *, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        bounded_limit = self._bounded_int(limit, 1, 200, "invalid_structured_output")
        bounded_offset = self._bounded_int(offset, 0, 100_000, "invalid_structured_output")
        rows = self.conn.execute(
            f"select {_RUN_COLUMNS} from local_generation_runs order by created_at desc, run_id limit ? offset ?",
            (bounded_limit, bounded_offset),
        ).fetchall()
        return [self._serialize_run(row) for row in rows]

    def get_run(self, run_id: str) -> dict[str, Any]:
        normalized = str(run_id or "").strip()
        if not normalized or len(normalized) > 200:
            raise LocalGenerationError("invalid_structured_output")
        row = self.conn.execute(
            f"select {_RUN_COLUMNS} from local_generation_runs where run_id = ?",
            (normalized,),
        ).fetchone()
        if not row:
            raise LocalGenerationError("profile_not_found")
        return self._serialize_run(row)

    def process_agent_response(
        self,
        *,
        deterministic_response: dict[str, Any],
        request_fields: dict[str, Any],
        agent_id: str,
        agent_name: str,
        category: str,
        web_context: list[dict[str, Any]],
        prior_agent_context: dict[str, Any] | None,
        memory_context: dict[str, Any],
        knowledge_context: dict[str, Any],
        local_context_summary: dict[str, Any],
        generation_options: dict[str, Any] | None,
        response_id: str,
        private_session: bool,
        high_stakes: bool,
    ) -> dict[str, Any]:
        options = generation_options or {}
        requested_mode = str(options.get("mode") or "deterministic")
        enabled = bool(options.get("enabled"))
        preview_only = bool(options.get("previewOnly"))
        base_context = self._base_generation_context(
            requested=enabled or preview_only or requested_mode != "deterministic",
            enabled=enabled,
            private_session=private_session,
            preview_only=preview_only,
            requested_mode=requested_mode,
        )
        base_context["highStakes"] = high_stakes
        base_context.update(
            {
                "requestedProfileId": options.get("modelProfileId"),
                "outputStyle": str(options.get("outputStyle") or "standard"),
                "maximumOutputCharacters": int(options.get("maxOutputCharacters") or 4_000),
                "temperature": float(options.get("temperature") if options.get("temperature") is not None else 0.2),
                "provider": None,
                "modelName": None,
                "profileId": None,
                "promptHash": None,
                "promptCharacterCount": 0,
                "sectionStats": {},
                "allowedCitationLabels": [],
                "truncationDisclosures": [],
                "outputCharacterCount": 0,
                "status": "deterministic",
                "error": None,
                "limitations": self._generation_limitations(private_session),
            }
        )
        if requested_mode == "deterministic" and not preview_only:
            return {"generationContext": base_context, "generatedResponse": None, "primaryResponseSource": "deterministic"}
        if requested_mode not in {"local_model", "local_model_with_fallback", "deterministic"}:
            return self._failed_agent_result(base_context, "invalid_structured_output", requested_mode)
        if not enabled:
            return self._failed_agent_result(base_context, "generation_disabled", requested_mode)
        if private_session and bool(options.get("includeFullPromptPreview")):
            return self._failed_agent_result(base_context, "full_prompt_preview_blocked_private_session", requested_mode)
        try:
            settings = self._settings()
            profile = self._profile(options.get("modelProfileId") or settings["activeProfileId"])
            requested_output_limit = self._bounded_int(
                options.get("maxOutputCharacters", profile["maximumOutputCharacters"]),
                500,
                12_000,
                "output_too_large",
            )
            output_limit = min(requested_output_limit, int(profile["maximumOutputCharacters"]))
            temperature = self._bounded_float(options.get("temperature", profile["temperature"]), 0.0, 1.0)
            output_style = str(options.get("outputStyle") or "standard")
            if output_style not in {"concise", "standard", "detailed"}:
                raise LocalGenerationError("invalid_structured_output")
            assembly = assemble_generation_prompt(
                agent_id=agent_id,
                agent_name=agent_name,
                category=category,
                deterministic_response=deterministic_response,
                request_fields=request_fields,
                web_context=web_context,
                prior_agent_context=prior_agent_context,
                memory_context=memory_context,
                knowledge_context=knowledge_context,
                local_context_summary=local_context_summary,
                context_char_limit=profile["contextCharacterLimit"],
                output_style=output_style,
                max_output_characters=output_limit,
                high_stakes=high_stakes,
            )
            prompt_metadata = assembly.metadata(
                include_full_prompt=preview_only and bool(options.get("includeFullPromptPreview"))
            )
            if preview_only:
                context = {
                    **base_context,
                    **self._safe_profile_context(profile, output_limit, temperature, output_style),
                    **prompt_metadata,
                    "actualMode": "prompt_preview",
                    "primarySource": "prompt_preview",
                    "status": "preview",
                    "limitations": self._generation_limitations(private_session),
                }
                return {"generationContext": context, "generatedResponse": None, "primaryResponseSource": "prompt_preview"}
            if not settings["enabled"]:
                raise LocalGenerationError("generation_disabled")
            return self._call_provider_for_agent(
                assembly=assembly,
                base_context=base_context,
                profile=profile,
                settings_snapshot=settings,
                output_limit=output_limit,
                temperature=temperature,
                output_style=output_style,
                requested_mode=requested_mode,
                response_id=response_id,
                agent_id=agent_id,
                private_session=private_session,
                high_stakes=high_stakes,
            )
        except (LocalGenerationError, LocalGenerationProviderError, PromptAssemblyError) as exc:
            return self._failed_agent_result(base_context, self._as_error(exc).code, requested_mode)

    def _call_provider_for_agent(
        self,
        *,
        assembly: Any,
        base_context: dict[str, Any],
        profile: dict[str, Any],
        settings_snapshot: dict[str, Any],
        output_limit: int,
        temperature: float,
        output_style: str,
        requested_mode: str,
        response_id: str,
        agent_id: str,
        private_session: bool,
        high_stakes: bool,
    ) -> dict[str, Any]:
        run_id: str | None = None
        runtime_id = str(uuid4())
        acquired = False
        cancel_handle = GenerationCancelHandle()
        try:
            self._acquire_generation()
            acquired = True
            started_at = utc_now()
            self._set_active_runtime(
                ActiveGenerationRuntime(
                    runtime_id=runtime_id,
                    run_id=None,
                    response_id=response_id,
                    agent_id=agent_id,
                    profile_id=profile["profileId"],
                    model_name=profile["modelName"],
                    purpose="agent_response",
                    phase="assembling_prompt",
                    started_at=started_at,
                    private_session=private_session,
                    cancel_handle=cancel_handle,
                )
            )
            if not private_session:
                run_id = str(uuid4())
                self._update_runtime_run_id(run_id)
                request_count = int(assembly.section_stats.get("currentRequest", {}).get("includedCharacters") or 0)
                deterministic_count = int(assembly.section_stats.get("deterministicResponse", {}).get("includedCharacters") or 0)
                self._insert_run(
                    run_id=run_id,
                    response_id=response_id,
                    agent_id=agent_id,
                    purpose="agent_response",
                    profile_id=profile["profileId"],
                    provider=PROVIDER,
                    model_name=profile["modelName"],
                    requested_mode=requested_mode,
                    actual_mode="local_model",
                    output_style=output_style,
                    status="started",
                    prompt_hash=assembly.prompt_hash,
                    prompt_char_count=assembly.prompt_character_count,
                    current_request_char_count=request_count,
                    deterministic_response_char_count=deterministic_count,
                    memory_item_count=int(assembly.section_stats.get("memory", {}).get("includedItemCount") or 0),
                    knowledge_chunk_count=int(assembly.section_stats.get("knowledge", {}).get("includedItemCount") or 0),
                    web_source_count=int(assembly.section_stats.get("web", {}).get("includedItemCount") or 0),
                    prior_context_present=bool(assembly.section_stats.get("priorContext", {}).get("includedCharacters")),
                    section_stats=assembly.section_stats,
                    created_at=started_at,
                )

            self._update_runtime_phase("connecting")
            self._update_runtime_phase("generating")

            provider_result = self.provider.generate(
                model=profile["modelName"],
                system_message=assembly.system_message,
                user_message=assembly.user_message,
                output_schema=GENERATED_RESPONSE_SCHEMA,
                keep_alive_seconds=profile["keepAliveSeconds"],
                temperature=temperature,
                cancel_handle=cancel_handle,
            )

            self._update_runtime_phase("validating")

            generated = self.validate_structured_output(
                provider_result["content"],
                allowed_citation_labels=set(assembly.allowed_citation_labels),
                max_response_characters=output_limit,
                high_stakes=high_stakes,
            )

            self._update_runtime_phase("finalizing")

            if not private_session and not self._settings_unchanged(settings_snapshot, profile):
                raise LocalGenerationError("generation_state_changed")

            output_count = len(json.dumps(generated, ensure_ascii=False, separators=(",", ":")))
            if run_id:
                self._complete_run(
                    run_id,
                    status="completed",
                    actual_mode="local_model",
                    output_char_count=output_count,
                    thinking_discarded=bool(provider_result["thinkingDiscarded"]),
                    completed_at=utc_now(),
                )
                with self.conn:
                    self.conn.execute(
                        "update local_generation_profiles set last_used_at = ? where profile_id = ?",
                        (utc_now(), profile["profileId"]),
                    )
                self._emit(
                    "generation.completed",
                    {"runId": run_id, "responseId": response_id, "agentId": agent_id, "profileId": profile["profileId"], "outputCharacterCount": output_count},
                )
            context = {
                **base_context,
                **self._safe_profile_context(profile, output_limit, temperature, output_style),
                **assembly.metadata(),
                "actualMode": "local_model",
                "primarySource": "local_model",
                "providerCalled": True,
                "runId": run_id,
                "runtimeId": runtime_id,
                "outputCharacterCount": output_count,
                "thinkingDiscarded": bool(provider_result["thinkingDiscarded"]),
                "status": "completed",
                "persisted": bool(run_id),
                "limitations": self._generation_limitations(private_session),
            }
            return {"generationContext": context, "generatedResponse": generated, "primaryResponseSource": "local_model"}
        except (LocalGenerationError, LocalGenerationProviderError, PromptAssemblyError) as exc:
            error = self._as_error(exc)
            if error.code == "generation_cancelled":
                self._update_runtime_phase("cancelled")
                if run_id:
                    self._complete_run(
                        run_id,
                        status="cancelled",
                        actual_mode="cancelled",
                        fallback_used=(requested_mode == "local_model_with_fallback"),
                        error_code="generation_cancelled",
                        completed_at=utc_now(),
                    )
                    self._emit(
                        "generation.cancelled",
                        {"runId": run_id, "responseId": response_id, "agentId": agent_id, "runtimeId": runtime_id},
                    )
                return self._cancelled_agent_result(
                    {
                        **base_context,
                        **self._safe_profile_context(profile, output_limit, temperature, output_style),
                        **assembly.metadata(),
                        "providerCalled": True,
                        "runId": run_id,
                        "runtimeId": runtime_id,
                        "persisted": bool(run_id),
                    },
                    requested_mode,
                )

            self._update_runtime_phase("failed")
            if run_id:
                fallback_used = requested_mode == "local_model_with_fallback"
                self._complete_run(
                    run_id,
                    status="failed",
                    actual_mode="deterministic_fallback" if fallback_used else "generation_failed",
                    fallback_used=fallback_used,
                    error_code=error.code,
                    completed_at=utc_now(),
                )
                self._emit(
                    "generation.failed",
                    {"runId": run_id, "responseId": response_id, "agentId": agent_id, "profileId": profile["profileId"], "errorCode": error.code},
                )
            return self._failed_agent_result(
                {
                    **base_context,
                    **self._safe_profile_context(profile, output_limit, temperature, output_style),
                    **assembly.metadata(),
                    "providerCalled": True,
                    "runId": run_id,
                    "runtimeId": runtime_id,
                    "persisted": bool(run_id),
                },
                error.code,
                requested_mode,
            )
        finally:
            self._clear_active_runtime()
            if acquired:
                self._release_generation()

    @staticmethod
    def validate_structured_output(
        value: dict[str, Any],
        *,
        allowed_citation_labels: set[str],
        max_response_characters: int,
        high_stakes: bool,
    ) -> dict[str, Any]:
        required = {"response", "keyPoints", "citations", "limitations", "safetyNotes"}
        if not isinstance(value, dict) or set(value) != required:
            raise LocalGenerationError("invalid_structured_output")
        response = _required_string(value["response"], max_response_characters)
        key_points = _string_list(value["keyPoints"], 12, 1_000)
        limitations = _string_list(value["limitations"], 12, 1_000)
        safety_notes = _string_list(value["safetyNotes"], 12, 1_000)
        citations_raw = value["citations"]
        if not isinstance(citations_raw, list) or len(citations_raw) > 20:
            raise LocalGenerationError("invalid_structured_output")
        citations: list[dict[str, str]] = []
        for item in citations_raw:
            if not isinstance(item, dict) or set(item) != {"label", "supports"}:
                raise LocalGenerationError("invalid_structured_output")
            label = _required_string(item["label"], 100)
            if label not in allowed_citation_labels:
                raise LocalGenerationError("invalid_structured_output")
            citations.append({"label": label, "supports": _required_string(item["supports"], 1_000)})
        if high_stakes:
            blocked_claims = (
                r"\b(?:i|jarvis)\s+(?:have\s+)?diagnos(?:e|ed)\b",
                r"\b(?:i|jarvis)\s+guarantee(?:s|d)?\s+(?:a\s+)?(?:financial|investment|return|profit)",
                r"\b(?:i am|jarvis is)\s+(?:acting as\s+)?your\s+(?:lawyer|attorney)\b",
                r"\battorney-client\s+(?:representation|relationship)\s+(?:is|has been)\s+(?:created|established)\b",
                r"\b(?:i|jarvis)\s+(?:have\s+)?(?:completed|performed|executed|fixed|patched|secured|remediated)\s+(?:the\s+|your\s+)?security",
                r"\b(?:i|jarvis)\s+(?:have\s+)?(?:contacted|called)\s+(?:911|emergency services)\b",
            )
            if any(re.search(pattern, response, re.IGNORECASE) for pattern in blocked_claims):
                raise LocalGenerationError("invalid_structured_output")
            warning = "High-stakes response: material uncertainty remains; verify important details and seek qualified professional review where relevant."
            limitation = "Jarvis did not diagnose, guarantee an outcome, establish professional representation, complete a security action, or contact emergency services."
            safety_notes = _append_bounded(safety_notes, warning, 12)
            limitations = _append_bounded(limitations, limitation, 12)
        structured = {
            "response": response,
            "keyPoints": key_points,
            "citations": citations,
            "limitations": limitations,
            "safetyNotes": safety_notes,
        }
        if len(json.dumps(structured, ensure_ascii=False, separators=(",", ":"))) > 20_000:
            raise LocalGenerationError("output_too_large")
        return structured

    def _cancelled_agent_result(self, context: dict[str, Any], requested_mode: str) -> dict[str, Any]:
        fallback = requested_mode == "local_model_with_fallback"
        primary = "deterministic_fallback" if fallback else "generation_cancelled"
        return {
            "generationContext": {
                **context,
                "actualMode": "deterministic" if fallback else "generation_cancelled",
                "primarySource": primary,
                "fallbackUsed": fallback,
                "status": "cancelled",
                "error": "generation_cancelled",
                "errorMessage": (
                    "Local generation was cancelled by the user. The deterministic response remains available."
                    if fallback
                    else "Local generation was cancelled by the user."
                ),
                "cancellationRequested": True,
                "automaticGeneration": False,
                "toolCalling": False,
                "limitations": self._generation_limitations(bool(context.get("privateSession"))),
            },
            "generatedResponse": None,
            "primaryResponseSource": primary,
        }

    def _failed_agent_result(self, context: dict[str, Any], code: str, requested_mode: str) -> dict[str, Any]:
        fallback = requested_mode == "local_model_with_fallback"
        primary = "deterministic_fallback" if fallback else "generation_failed"
        return {
            "generationContext": {
                **context,
                "actualMode": "deterministic" if fallback else "generation_failed",
                "primarySource": primary,
                "fallbackUsed": fallback,
                "status": "failed",
                "error": code,
                "errorMessage": _ERROR_MESSAGES.get(code, "Local generation failed safely."),
                "automaticGeneration": False,
                "toolCalling": False,
                "limitations": self._generation_limitations(bool(context.get("privateSession"))),
            },
            "generatedResponse": None,
            "primaryResponseSource": primary,
        }

    def _set_active_runtime(self, runtime: ActiveGenerationRuntime) -> None:
        with self._runtime_lock:
            self._active_runtime = runtime

    def _update_runtime_phase(self, phase: str) -> None:
        with self._runtime_lock:
            if self._active_runtime is not None:
                self._active_runtime.phase = phase
                if phase in ("completed", "failed", "cancelled"):
                    self._active_runtime.cancellable = False

    def _update_runtime_run_id(self, run_id: str) -> None:
        with self._runtime_lock:
            if self._active_runtime is not None:
                self._active_runtime.run_id = run_id

    def _clear_active_runtime(self) -> None:
        with self._runtime_lock:
            self._active_runtime = None

    @staticmethod
    def _base_generation_context(
        *, requested: bool, enabled: bool, private_session: bool, preview_only: bool, requested_mode: str
    ) -> dict[str, Any]:
        return {
            "requested": requested,
            "enabled": enabled,
            "privateSession": private_session,
            "previewOnly": preview_only,
            "requestedMode": requested_mode,
            "actualMode": "deterministic",
            "primarySource": "deterministic",
            "providerCalled": False,
            "runId": None,
            "runtimeId": None,
            "fallbackUsed": False,
            "thinkingDiscarded": False,
            "persisted": False,
            "automaticGeneration": False,
            "toolCalling": False,
        }

    @staticmethod
    def _safe_profile_context(
        profile: dict[str, Any], output_limit: int, temperature: float, output_style: str
    ) -> dict[str, Any]:
        return {
            "provider": PROVIDER,
            "modelName": profile["modelName"],
            "profileId": profile["profileId"],
            "contextCharacterLimit": profile["contextCharacterLimit"],
            "maximumOutputCharacters": output_limit,
            "temperature": temperature,
            "keepAliveSeconds": profile["keepAliveSeconds"],
            "outputStyle": output_style,
        }

    @staticmethod
    def _generation_limitations(private_session: bool) -> list[str]:
        limitations = [
            "Generation is explicit per request and never automatic or background.",
            "The model has no tools or action authority.",
            "Prompts, generated output, thinking, and provider bodies are not persisted.",
            "The deterministic response remains available for manual review.",
            "Active local generation can be cancelled explicitly at any time.",
        ]
        if private_session:
            limitations.append("Private generation is ephemeral and creates no run row or generation event.")
        return limitations

    def _settings(self) -> dict[str, Any]:
        row = self.conn.execute(
            """
            select settings_id, enabled, provider, model_name, active_profile_id,
              context_char_limit, max_output_chars, default_temperature,
              keep_alive_seconds, configured_at, updated_at
            from local_generation_settings where settings_id = 'default'
            """
        ).fetchone()
        if not row:
            raise LocalGenerationError("generation_disabled")
        return {
            "settingsId": row[0],
            "enabled": bool(row[1]),
            "provider": row[2],
            "modelName": row[3],
            "activeProfileId": row[4],
            "contextCharacterLimit": row[5],
            "maximumOutputCharacters": row[6],
            "temperature": row[7],
            "keepAliveSeconds": row[8],
            "configuredAt": row[9],
            "updatedAt": row[10],
        }

    def _profile(self, profile_id: object) -> dict[str, Any]:
        normalized = str(profile_id or "").strip()
        if not normalized or len(normalized) > 200:
            raise LocalGenerationError("profile_not_found")
        row = self.conn.execute(
            """
            select profile_id, provider, model_name, context_char_limit, max_output_chars,
              default_temperature, keep_alive_seconds, structured_output_mode, created_at, last_used_at
            from local_generation_profiles where profile_id = ?
            """,
            (normalized,),
        ).fetchone()
        if not row:
            raise LocalGenerationError("profile_not_found")
        return self._serialize_profile(row)

    @staticmethod
    def _serialize_profile(row: tuple[Any, ...]) -> dict[str, Any]:
        return {
            "profileId": row[0],
            "provider": row[1],
            "modelName": row[2],
            "contextCharacterLimit": row[3],
            "maximumOutputCharacters": row[4],
            "temperature": row[5],
            "keepAliveSeconds": row[6],
            "structuredOutputMode": row[7],
            "createdAt": row[8],
            "lastUsedAt": row[9],
        }

    def _settings_unchanged(self, prior: dict[str, Any], profile: dict[str, Any]) -> bool:
        current = self._settings()
        return (
            current["enabled"]
            and current["updatedAt"] == prior["updatedAt"]
            and current["activeProfileId"] == prior["activeProfileId"]
            and current["provider"] == prior["provider"]
            and profile["provider"] == PROVIDER
        )

    def _acquire_generation(self) -> None:
        if not self._generation_lock.acquire(blocking=False):
            raise LocalGenerationError("generation_in_progress")
        with self._active_count_lock:
            self._active_count = 1

    def _release_generation(self) -> None:
        if self._generation_lock.locked():
            with self._active_count_lock:
                self._active_count = 0
            self._generation_lock.release()

    def _insert_run(self, *, run_id: str, created_at: str, **values: Any) -> None:
        section_stats = values.get("section_stats") or {}
        with self.conn:
            self.conn.execute(
                """
                insert into local_generation_runs (
                  run_id, response_id, agent_id, purpose, profile_id, provider, model_name,
                  requested_mode, actual_mode, output_style, status, prompt_hash, prompt_char_count,
                  current_request_char_count, deterministic_response_char_count, memory_item_count,
                  knowledge_chunk_count, web_source_count, prior_context_present, section_stats,
                  output_char_count, fallback_used, thinking_discarded, error_code, created_at, completed_at
                ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, null, ?, null)
                """,
                (
                    run_id,
                    values.get("response_id"),
                    values.get("agent_id"),
                    values.get("purpose", "agent_response"),
                    values.get("profile_id"),
                    values.get("provider", PROVIDER),
                    values.get("model_name"),
                    values.get("requested_mode", "local_model"),
                    values.get("actual_mode", "local_model"),
                    values.get("output_style", "standard"),
                    values.get("status", "started"),
                    values.get("prompt_hash"),
                    int(values.get("prompt_char_count") or 0),
                    int(values.get("current_request_char_count") or 0),
                    int(values.get("deterministic_response_char_count") or 0),
                    int(values.get("memory_item_count") or 0),
                    int(values.get("knowledge_chunk_count") or 0),
                    int(values.get("web_source_count") or 0),
                    int(bool(values.get("prior_context_present"))),
                    json.dumps(section_stats, sort_keys=True, separators=(",", ":")),
                    created_at,
                ),
            )

    def _complete_run(
        self,
        run_id: str,
        *,
        status: str,
        actual_mode: str | None = None,
        output_char_count: int = 0,
        fallback_used: bool = False,
        thinking_discarded: bool = False,
        error_code: str | None = None,
        completed_at: str,
    ) -> None:
        with self.conn:
            self.conn.execute(
                """
                update local_generation_runs set status = ?, actual_mode = coalesce(?, actual_mode), output_char_count = ?, fallback_used = ?,
                  thinking_discarded = ?, error_code = ?, completed_at = ? where run_id = ?
                """,
                (
                    status,
                    actual_mode,
                    int(output_char_count),
                    int(fallback_used),
                    int(thinking_discarded),
                    error_code,
                    completed_at,
                    run_id,
                ),
            )

    @staticmethod
    def _serialize_run(row: tuple[Any, ...]) -> dict[str, Any]:
        values = dict(zip(_RUN_COLUMN_NAMES, row))
        return {
            "runId": values["run_id"],
            "responseId": values["response_id"],
            "agentId": values["agent_id"],
            "purpose": values["purpose"],
            "profileId": values["profile_id"],
            "provider": values["provider"],
            "modelName": values["model_name"],
            "requestedMode": values["requested_mode"],
            "actualMode": values["actual_mode"],
            "outputStyle": values["output_style"],
            "status": values["status"],
            "promptHash": values["prompt_hash"],
            "promptCharacterCount": values["prompt_char_count"],
            "currentRequestCharacterCount": values["current_request_char_count"],
            "deterministicResponseCharacterCount": values["deterministic_response_char_count"],
            "memoryItemCount": values["memory_item_count"],
            "knowledgeChunkCount": values["knowledge_chunk_count"],
            "webSourceCount": values["web_source_count"],
            "priorContextPresent": bool(values["prior_context_present"]),
            "sectionStats": json.loads(values["section_stats"] or "{}"),
            "outputCharacterCount": values["output_char_count"],
            "fallbackUsed": bool(values["fallback_used"]),
            "thinkingDiscarded": bool(values["thinking_discarded"]),
            "errorCode": values["error_code"],
            "createdAt": values["created_at"],
            "completedAt": values["completed_at"],
            "contentPersisted": False,
        }

    def _emit(self, event_type: str, metadata: dict[str, Any]) -> None:
        if self.event_bus is not None:
            self.event_bus.emit(event_type, payload=metadata)

    @staticmethod
    def _model(value: object) -> str:
        try:
            return validate_model_name(value)
        except LocalGenerationProviderError as exc:
            raise LocalGenerationError(exc.code) from None

    @staticmethod
    def _actor(value: object) -> str:
        actor = str(value or "").strip()
        return actor[:200] if actor else "local_user"

    @staticmethod
    def _bounded_int(value: object, minimum: int, maximum: int, code: str) -> int:
        if isinstance(value, bool):
            raise LocalGenerationError(code)
        try:
            number = int(value)
        except (TypeError, ValueError):
            raise LocalGenerationError(code) from None
        if number < minimum or number > maximum:
            raise LocalGenerationError(code)
        return number

    @staticmethod
    def _bounded_float(value: object, minimum: float, maximum: float) -> float:
        if isinstance(value, bool):
            raise LocalGenerationError("invalid_structured_output")
        try:
            number = float(value)
        except (TypeError, ValueError):
            raise LocalGenerationError("invalid_structured_output") from None
        if number < minimum or number > maximum:
            raise LocalGenerationError("invalid_structured_output")
        return number

    @staticmethod
    def _profile_id(model: str, context_limit: int, output_limit: int, temperature: float, keep_alive: int) -> str:
        digest = hashlib.sha256(
            f"{PROVIDER}\0{model}\0{context_limit}\0{output_limit}\0{temperature:.6f}\0{keep_alive}\0{STRUCTURED_OUTPUT_MODE}".encode("utf-8")
        ).hexdigest()[:24]
        return f"generation-{digest}"

    @staticmethod
    def _as_error(exc: BaseException) -> LocalGenerationError:
        code = getattr(exc, "code", "invalid_provider_response")
        return LocalGenerationError(str(code))


def _required_string(value: Any, maximum: int) -> str:
    if not isinstance(value, str):
        raise LocalGenerationError("invalid_structured_output")
    text = value.strip()
    if not text or len(text) > maximum or any(ord(character) < 9 for character in text):
        raise LocalGenerationError("invalid_structured_output")
    return text


def _string_list(value: Any, maximum_items: int, maximum_characters: int) -> list[str]:
    if not isinstance(value, list) or len(value) > maximum_items:
        raise LocalGenerationError("invalid_structured_output")
    return [_required_string(item, maximum_characters) for item in value]


def _append_bounded(items: list[str], value: str, maximum_items: int) -> list[str]:
    result = list(items)
    if value in result:
        return result
    if len(result) >= maximum_items:
        result[-1] = value
    else:
        result.append(value)
    return result


_RUN_COLUMN_NAMES = [
    "run_id", "response_id", "agent_id", "purpose", "profile_id", "provider", "model_name",
    "requested_mode", "actual_mode", "output_style", "status", "prompt_hash", "prompt_char_count",
    "current_request_char_count", "deterministic_response_char_count", "memory_item_count",
    "knowledge_chunk_count", "web_source_count", "prior_context_present", "section_stats",
    "output_char_count", "fallback_used", "thinking_discarded", "error_code", "created_at", "completed_at",
]
_RUN_COLUMNS = ", ".join(_RUN_COLUMN_NAMES)
