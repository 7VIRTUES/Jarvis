from __future__ import annotations

import http.client
import json
import re
import socket
import threading
from typing import Any


GENERATION_HOST = "127.0.0.1"
GENERATION_PORT = 11434
GENERATION_PATH = "/api/chat"
GENERATION_ENDPOINT = f"http://{GENERATION_HOST}:{GENERATION_PORT}{GENERATION_PATH}"

PROBE_TIMEOUT_SECONDS = 120
GENERATION_TIMEOUT_SECONDS = 300
MAX_REQUEST_BYTES = 2 * 1024 * 1024
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
MAX_PROMPT_CHARACTERS = 120_000
MAX_STRUCTURED_OUTPUT_CHARACTERS = 20_000
MAX_PRIMARY_RESPONSE_CHARACTERS = 12_000

_MODEL_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,119}$")
_DISALLOWED_MODEL_TEXT = re.compile(
    r"(?:cloud|https?[:/]|\?|#|[\\{}\[\]\"'`$|<>;&]|\$\(|\r|\n|\t)", re.IGNORECASE
)


class LocalGenerationProviderError(RuntimeError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


class GenerationCancelHandle:
    """Thread-safe cancellation handle for a single in-flight local generation request."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._cancelled = False
        self._conn: http.client.HTTPConnection | None = None

    @property
    def is_cancelled(self) -> bool:
        with self._lock:
            return self._cancelled

    def register_connection(self, conn: http.client.HTTPConnection) -> None:
        with self._lock:
            self._conn = conn
            if self._cancelled:
                try:
                    conn.close()
                except Exception:
                    pass

    def unregister_connection(self) -> None:
        with self._lock:
            self._conn = None

    def cancel(self) -> bool:
        with self._lock:
            self._cancelled = True
            if self._conn is not None:
                try:
                    self._conn.close()
                except Exception:
                    pass
            return True


def validate_model_name(value: object) -> str:
    model = str(value or "")
    if (
        not _MODEL_NAME.fullmatch(model)
        or _DISALLOWED_MODEL_TEXT.search(model)
        or "://" in model
        or any(character.isspace() or ord(character) < 32 for character in model)
    ):
        raise LocalGenerationProviderError("invalid_model_name")
    return model


class LocalGenerationProvider:
    endpoint = GENERATION_ENDPOINT

    def generate(
        self,
        *,
        model: str,
        system_message: str,
        user_message: str,
        output_schema: dict[str, Any],
        timeout_seconds: int = GENERATION_TIMEOUT_SECONDS,
        keep_alive_seconds: int = 300,
        temperature: float = 0.2,
        cancel_handle: GenerationCancelHandle | None = None,
    ) -> dict[str, Any]:
        model = validate_model_name(model)
        if len(system_message) + len(user_message) > MAX_PROMPT_CHARACTERS:
            raise LocalGenerationProviderError("generation_request_too_large")
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            "stream": False,
            "think": False,
            "format": output_schema,
            "keep_alive": int(keep_alive_seconds),
            "options": {"temperature": float(temperature)},
        }
        response = self._post(
            payload,
            min(max(int(timeout_seconds), 1), GENERATION_TIMEOUT_SECONDS),
            cancel_handle=cancel_handle,
        )
        return self._validated_generation_response(response)

    def probe(
        self,
        *,
        model: str,
        timeout_seconds: int = PROBE_TIMEOUT_SECONDS,
        cancel_handle: GenerationCancelHandle | None = None,
    ) -> dict[str, Any]:
        result = self.generate(
            model=model,
            system_message=(
                "Return only the required JSON object. Do not use tools, images, external data, "
                "or any user content."
            ),
            user_message='Return exactly {"status":"ok"}.',
            output_schema={
                "type": "object",
                "properties": {"status": {"type": "string"}},
                "required": ["status"],
                "additionalProperties": False,
            },
            timeout_seconds=min(max(int(timeout_seconds), 1), PROBE_TIMEOUT_SECONDS),
            keep_alive_seconds=0,
            temperature=0.0,
            cancel_handle=cancel_handle,
        )
        if set(result["content"]) != {"status"} or str(result["content"]["status"]).strip().lower() != "ok":
            raise LocalGenerationProviderError("invalid_provider_response")
        return {"status": "ok", "thinkingDiscarded": result["thinkingDiscarded"]}

    def unload(
        self,
        *,
        model: str,
        timeout_seconds: int = PROBE_TIMEOUT_SECONDS,
        cancel_handle: GenerationCancelHandle | None = None,
    ) -> dict[str, Any]:
        model = validate_model_name(model)
        response = self._post(
            {"model": model, "messages": [], "stream": False, "keep_alive": 0},
            min(max(int(timeout_seconds), 1), PROBE_TIMEOUT_SECONDS),
            cancel_handle=cancel_handle,
        )
        if not isinstance(response, dict):
            raise LocalGenerationProviderError("invalid_provider_response")
        return {"unloaded": True, "provider": "ollama_local", "model": model}

    def _post(
        self,
        payload: dict[str, Any],
        timeout_seconds: int,
        cancel_handle: GenerationCancelHandle | None = None,
    ) -> dict[str, Any]:
        if cancel_handle and cancel_handle.is_cancelled:
            raise LocalGenerationProviderError("generation_cancelled")

        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if len(encoded) > MAX_REQUEST_BYTES:
            raise LocalGenerationProviderError("generation_request_too_large")

        conn = http.client.HTTPConnection(GENERATION_HOST, GENERATION_PORT, timeout=timeout_seconds)
        if cancel_handle:
            cancel_handle.register_connection(conn)

        try:
            if cancel_handle and cancel_handle.is_cancelled:
                raise LocalGenerationProviderError("generation_cancelled")

            conn.request(
                "POST",
                GENERATION_PATH,
                body=encoded,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Host": f"{GENERATION_HOST}:{GENERATION_PORT}",
                },
            )

            if cancel_handle and cancel_handle.is_cancelled:
                raise LocalGenerationProviderError("generation_cancelled")

            response = conn.getresponse()

            if 300 <= response.status < 400:
                raise LocalGenerationProviderError("provider_redirect_blocked")
            if response.status == 404:
                raise LocalGenerationProviderError("model_unavailable")
            if response.status != 200:
                raise LocalGenerationProviderError("provider_unavailable")

            chunks: list[bytes] = []
            total_bytes = 0
            while True:
                if cancel_handle and cancel_handle.is_cancelled:
                    raise LocalGenerationProviderError("generation_cancelled")
                chunk = response.read(65536)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if total_bytes > MAX_RESPONSE_BYTES:
                    raise LocalGenerationProviderError("generation_response_too_large")
                chunks.append(chunk)

            body = b"".join(chunks)

        except LocalGenerationProviderError:
            raise
        except (TimeoutError, socket.timeout):
            if cancel_handle and cancel_handle.is_cancelled:
                raise LocalGenerationProviderError("generation_cancelled") from None
            raise LocalGenerationProviderError("provider_timeout") from None
        except (http.client.HTTPException, ConnectionError, OSError, socket.error):
            if cancel_handle and cancel_handle.is_cancelled:
                raise LocalGenerationProviderError("generation_cancelled") from None
            raise LocalGenerationProviderError("provider_unavailable") from None
        finally:
            if cancel_handle:
                cancel_handle.unregister_connection()
            try:
                conn.close()
            except Exception:
                pass

        try:
            decoded = body.decode("utf-8")
            parsed = json.loads(decoded)
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise LocalGenerationProviderError("invalid_provider_response") from None

        if not isinstance(parsed, dict):
            raise LocalGenerationProviderError("invalid_provider_response")
        return parsed

    @staticmethod
    def _validated_generation_response(response: dict[str, Any]) -> dict[str, Any]:
        if response.get("done") is not True:
            raise LocalGenerationProviderError("invalid_provider_response")
        message = response.get("message")
        if not isinstance(message, dict) or message.get("role") != "assistant":
            raise LocalGenerationProviderError("invalid_provider_response")
        if message.get("tool_calls"):
            raise LocalGenerationProviderError("unexpected_tool_call")
        if message.get("images") or response.get("images"):
            raise LocalGenerationProviderError("unexpected_image_output")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise LocalGenerationProviderError("invalid_provider_response")
        if len(content) > MAX_STRUCTURED_OUTPUT_CHARACTERS:
            raise LocalGenerationProviderError("output_too_large")
        try:
            structured = json.loads(content)
        except json.JSONDecodeError:
            raise LocalGenerationProviderError("invalid_structured_output") from None
        if not isinstance(structured, dict):
            raise LocalGenerationProviderError("invalid_structured_output")
        thinking = message.get("thinking")
        return {
            "content": structured,
            "contentCharacterCount": len(content),
            "thinkingDiscarded": bool(thinking.strip()) if isinstance(thinking, str) else bool(thinking),
        }
