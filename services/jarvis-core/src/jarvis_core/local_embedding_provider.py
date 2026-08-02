from __future__ import annotations

import json
import math
import re
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


OLLAMA_EMBEDDING_URL = "http://127.0.0.1:11434/api/embed"
OLLAMA_ENDPOINT_LABEL = "127.0.0.1:11434 /api/embed (fixed loopback)"
MAX_RESPONSE_BYTES = 32 * 1024 * 1024
MAX_REQUEST_BYTES = 32 * 1024 * 1024
_MODEL_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:/-]{0,119}\Z")


class LocalEmbeddingProviderError(RuntimeError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class EmbeddingResponse:
    vectors: tuple[tuple[float, ...], ...]
    dimensions: int


class _RejectRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        raise LocalEmbeddingProviderError("provider_redirect_blocked")


class LocalOllamaEmbeddingProvider:
    """One fixed loopback Ollama embedding transport with no proxy or redirect path."""

    provider_id = "ollama_local"
    endpoint_label = OLLAMA_ENDPOINT_LABEL

    def __init__(self) -> None:
        self._opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}),
            _RejectRedirects(),
        )

    @staticmethod
    def validate_model_name(value: Any) -> str:
        if not isinstance(value, str) or not _MODEL_PATTERN.fullmatch(value):
            raise LocalEmbeddingProviderError("invalid_model_name")
        lowered = value.casefold()
        if (
            any(character.isspace() or ord(character) < 32 for character in value)
            or "?" in value
            or "#" in value
            or "\\" in value
            or "://" in value
            or "cloud" in lowered
            or lowered.startswith(("http:", "https:", "http/", "https/"))
        ):
            raise LocalEmbeddingProviderError("invalid_model_name")
        return value

    def embed(
        self,
        model_name: str,
        inputs: list[str],
        *,
        timeout: float,
        expected_dimensions: int | None = None,
    ) -> EmbeddingResponse:
        model_name = self.validate_model_name(model_name)
        if (
            not isinstance(inputs, list)
            or not inputs
            or any(not isinstance(value, str) or not value for value in inputs)
        ):
            raise LocalEmbeddingProviderError("embedding_input_too_large")
        body = json.dumps(
            {"model": model_name, "input": inputs, "truncate": False},
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        if len(body) > MAX_REQUEST_BYTES:
            raise LocalEmbeddingProviderError("embedding_input_too_large")
        request = urllib.request.Request(
            OLLAMA_EMBEDDING_URL,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with self._opener.open(request, timeout=timeout) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
        except LocalEmbeddingProviderError:
            raise
        except urllib.error.HTTPError as exc:
            if 300 <= exc.code < 400:
                raise LocalEmbeddingProviderError("provider_redirect_blocked") from None
            if exc.code in {400, 404}:
                raise LocalEmbeddingProviderError("model_unavailable") from None
            raise LocalEmbeddingProviderError("provider_unavailable") from None
        except (TimeoutError, socket.timeout):
            raise LocalEmbeddingProviderError("provider_timeout") from None
        except (urllib.error.URLError, OSError):
            raise LocalEmbeddingProviderError("provider_unavailable") from None
        if len(raw) > MAX_RESPONSE_BYTES:
            raise LocalEmbeddingProviderError("provider_response_too_large")
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise LocalEmbeddingProviderError("invalid_provider_response") from None
        return self._validate_response(payload, len(inputs), expected_dimensions)

    @staticmethod
    def _validate_response(
        payload: Any,
        expected_count: int,
        expected_dimensions: int | None,
    ) -> EmbeddingResponse:
        if not isinstance(payload, dict) or not isinstance(payload.get("embeddings"), list):
            raise LocalEmbeddingProviderError("invalid_provider_response")
        embeddings = payload["embeddings"]
        if len(embeddings) != expected_count:
            raise LocalEmbeddingProviderError("invalid_provider_response")
        normalized: list[tuple[float, ...]] = []
        dimensions: int | None = None
        for vector in embeddings:
            if not isinstance(vector, list) or not vector:
                raise LocalEmbeddingProviderError("invalid_provider_response")
            if any(
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(float(value))
                for value in vector
            ):
                raise LocalEmbeddingProviderError("invalid_provider_response")
            if dimensions is None:
                dimensions = len(vector)
                if not 8 <= dimensions <= 4096:
                    raise LocalEmbeddingProviderError("invalid_provider_response")
            elif len(vector) != dimensions:
                raise LocalEmbeddingProviderError("embedding_dimension_mismatch")
            magnitude = math.sqrt(sum(float(value) * float(value) for value in vector))
            if not math.isfinite(magnitude) or magnitude == 0:
                raise LocalEmbeddingProviderError("invalid_provider_response")
            unit = tuple(float(value) / magnitude for value in vector)
            if any(not math.isfinite(value) for value in unit):
                raise LocalEmbeddingProviderError("invalid_provider_response")
            normalized.append(unit)
        assert dimensions is not None
        if expected_dimensions is not None and dimensions != expected_dimensions:
            raise LocalEmbeddingProviderError("embedding_dimension_mismatch")
        return EmbeddingResponse(tuple(normalized), dimensions)
