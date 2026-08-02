from __future__ import annotations

import json
import re
import socket
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


GENERATION_ENDPOINT = "http://127.0.0.1:11434/api/chat"
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


class _RejectRedirects(HTTPRedirectHandler):
    def redirect_request(
        self,
        req: Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        raise LocalGenerationProviderError("provider_redirect_blocked")


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

    def __init__(self) -> None:
        self._opener = build_opener(ProxyHandler({}), _RejectRedirects())

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
        response = self._post(payload, min(max(int(timeout_seconds), 1), GENERATION_TIMEOUT_SECONDS))
        return self._validated_generation_response(response)

    def probe(self, *, model: str, timeout_seconds: int = PROBE_TIMEOUT_SECONDS) -> dict[str, Any]:
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
        )
        if set(result["content"]) != {"status"} or str(result["content"]["status"]).strip().lower() != "ok":
            raise LocalGenerationProviderError("invalid_provider_response")
        return {"status": "ok", "thinkingDiscarded": result["thinkingDiscarded"]}

    def unload(self, *, model: str, timeout_seconds: int = PROBE_TIMEOUT_SECONDS) -> dict[str, Any]:
        model = validate_model_name(model)
        response = self._post(
            {"model": model, "messages": [], "stream": False, "keep_alive": 0},
            min(max(int(timeout_seconds), 1), PROBE_TIMEOUT_SECONDS),
        )
        if not isinstance(response, dict):
            raise LocalGenerationProviderError("invalid_provider_response")
        return {"unloaded": True, "provider": "ollama_local", "model": model}

    def _post(self, payload: dict[str, Any], timeout_seconds: int) -> dict[str, Any]:
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if len(encoded) > MAX_REQUEST_BYTES:
            raise LocalGenerationProviderError("generation_request_too_large")
        request = Request(
            GENERATION_ENDPOINT,
            data=encoded,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with self._opener.open(request, timeout=timeout_seconds) as response:
                if response.geturl() != GENERATION_ENDPOINT:
                    raise LocalGenerationProviderError("provider_redirect_blocked")
                body = response.read(MAX_RESPONSE_BYTES + 1)
        except LocalGenerationProviderError:
            raise
        except HTTPError as exc:
            if 300 <= exc.code < 400:
                raise LocalGenerationProviderError("provider_redirect_blocked") from None
            if exc.code == 404:
                raise LocalGenerationProviderError("model_unavailable") from None
            raise LocalGenerationProviderError("provider_unavailable") from None
        except (TimeoutError, socket.timeout):
            raise LocalGenerationProviderError("provider_timeout") from None
        except URLError as exc:
            if isinstance(exc.reason, (TimeoutError, socket.timeout)):
                raise LocalGenerationProviderError("provider_timeout") from None
            raise LocalGenerationProviderError("provider_unavailable") from None
        if len(body) > MAX_RESPONSE_BYTES:
            raise LocalGenerationProviderError("generation_response_too_large")
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
