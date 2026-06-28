from __future__ import annotations

import ipaddress
import json
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from typing import Any


WEB_RESEARCH_MODE = "read_only_public_web"
WEB_RESEARCH_AGENT_MODE = "read_only_public_url_context"
MAX_URLS_PER_PREVIEW = 5
DEFAULT_EXCERPT_CHARS = 1600
MAX_EXCERPT_CHARS = 6000
MAX_RESPONSE_BYTES = 120_000
REQUEST_TIMEOUT_SECONDS = 5
MAX_REDIRECTS = 3

ALLOWED_SCHEMES = {"http", "https"}
ALLOWED_METHODS = ["GET", "HEAD"]
BLOCKED_METHODS = ["POST", "PUT", "PATCH", "DELETE"]
ALLOWED_CONTENT_TYPES = (
    "text/html",
    "text/plain",
    "application/json",
    "application/xml",
    "text/xml",
)
BLOCKED_SCHEMES = ("file", "ftp", "data", "javascript", "ws", "wss")
BLOCKED_HOST_SUFFIXES = (
    ".local",
    ".localhost",
    ".internal",
    ".lan",
    ".home",
    ".corp",
    ".intranet",
)
BLOCKED_DOWNLOAD_EXTENSIONS = (
    ".exe",
    ".msi",
    ".bat",
    ".cmd",
    ".ps1",
    ".sh",
    ".zip",
    ".rar",
    ".7z",
    ".tar",
    ".gz",
    ".dmg",
    ".pkg",
)
WEB_RESEARCH_LIMITATIONS = [
    "No logins or accounts, no cookies, forms, posts, purchases, bookings, uploads, or submissions.",
    "No private networks, localhost, internal hostnames, or cloud metadata targets.",
    "No browser automation, JavaScript execution, search-engine API integration, or connector behavior.",
    "No downloads or scripts; suspicious executable/archive/script URL paths are blocked.",
    "Fetched content is returned as a short excerpt and is not persisted by this service.",
]
WEB_RESEARCH_BOUNDARIES = [
    "Read-only public web only.",
    "Manual click required.",
    "HTTP/HTTPS public URLs only.",
    "GET/HEAD only.",
    "No logins or accounts.",
    "No forms, posts, purchases, or bookings.",
    "No private networks or localhost.",
    "No downloads or scripts.",
    "Source context is inserted for review, not executed automatically.",
]


class _TextExtractor(HTMLParser):
    def __init__(self, max_chars: int) -> None:
        super().__init__()
        self.max_chars = max_chars
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self._ignored_depth = 0
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style", "noscript"}:
            self._ignored_depth += 1
        if tag.lower() == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript"} and self._ignored_depth:
            self._ignored_depth -= 1
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        cleaned = _collapse_whitespace(data)
        if not cleaned:
            return
        if self._in_title:
            self.title_parts.append(cleaned)
        if self._ignored_depth:
            return
        current_length = sum(len(part) for part in self.text_parts)
        if current_length < self.max_chars:
            self.text_parts.append(cleaned)

    @property
    def title(self) -> str:
        return _collapse_whitespace(" ".join(self.title_parts))[:240]

    @property
    def excerpt(self) -> str:
        return _collapse_whitespace(" ".join(self.text_parts))[: self.max_chars]


def web_research_policy(agent_count: int = 37) -> dict[str, Any]:
    return {
        "enabled": True,
        "mode": WEB_RESEARCH_MODE,
        "allowed_methods": list(ALLOWED_METHODS),
        "blocked_methods": list(BLOCKED_METHODS),
        "blocked_targets": [
            "file://, ftp://, data:, javascript:, ws://, and wss:// URLs.",
            "localhost, loopback, private-network, link-local, non-public, and cloud metadata IP targets.",
            "private/internal hostnames and URLs with username/password credentials.",
            "executable, script, installer, archive, disk image, and compressed-file URL paths.",
        ],
        "content_limits": {
            "max_response_bytes": MAX_RESPONSE_BYTES,
            "default_excerpt_chars": DEFAULT_EXCERPT_CHARS,
            "max_excerpt_chars": MAX_EXCERPT_CHARS,
            "timeout_seconds": REQUEST_TIMEOUT_SECONDS,
            "max_redirects": MAX_REDIRECTS,
            "allowed_content_types": list(ALLOWED_CONTENT_TYPES),
        },
        "safety_boundaries": list(WEB_RESEARCH_BOUNDARIES),
        "agent_availability_summary": {
            "local_response_agent_count": agent_count,
            "web_research_available": True,
            "web_research_mode": WEB_RESEARCH_AGENT_MODE,
            "web_research_requires_user_enabled": True,
            "web_research_is_optional": True,
            "automatic_agent_browsing": False,
            "connector_behavior": False,
        },
    }


def web_research_agent_metadata() -> dict[str, Any]:
    return {
        "web_research_available": True,
        "webResearchAvailable": True,
        "web_research_mode": WEB_RESEARCH_AGENT_MODE,
        "webResearchMode": WEB_RESEARCH_AGENT_MODE,
        "web_research_requires_user_enabled": True,
        "webResearchRequiresUserEnabled": True,
        "web_research_is_optional": True,
        "webResearchIsOptional": True,
        "web_research_limitations": list(WEB_RESEARCH_LIMITATIONS),
        "webResearchLimitations": list(WEB_RESEARCH_LIMITATIONS),
    }


def validate_public_url(url: str, *, resolve_dns: bool = False) -> dict[str, Any]:
    original_url = str(url or "").strip()
    base_response = {
        "url": original_url,
        "is_allowed": False,
        "normalized_url": "",
        "blocked_reason": "",
        "warnings": [],
        "safety_boundaries": list(WEB_RESEARCH_BOUNDARIES),
    }
    if not original_url:
        return {**base_response, "blocked_reason": "URL is required."}
    parsed = urllib.parse.urlsplit(original_url)
    scheme = parsed.scheme.lower()
    if scheme not in ALLOWED_SCHEMES:
        return {**base_response, "blocked_reason": "Only HTTP/HTTPS public URLs are allowed."}
    if parsed.username or parsed.password:
        return {**base_response, "blocked_reason": "Credential-bearing URLs are blocked."}
    if not parsed.hostname:
        return {**base_response, "blocked_reason": "URL host is required."}
    host = parsed.hostname.strip().lower().strip("[]")
    blocked_host_reason = _blocked_host_reason(host)
    if blocked_host_reason:
        return {**base_response, "blocked_reason": blocked_host_reason}
    path = urllib.parse.unquote(parsed.path or "").lower()
    if path.endswith(BLOCKED_DOWNLOAD_EXTENSIONS):
        return {**base_response, "blocked_reason": "Executable, script, archive, installer, and compressed-file URL paths are blocked."}
    if resolve_dns:
        resolved_reason = _blocked_resolved_host_reason(host)
        if resolved_reason:
            return {**base_response, "blocked_reason": resolved_reason}
    normalized = urllib.parse.urlunsplit(
        (
            scheme,
            parsed.netloc.lower(),
            parsed.path or "/",
            parsed.query,
            "",
        )
    )
    warnings: list[str] = []
    if parsed.query:
        warnings.append("Query strings can contain identifiers; avoid secrets or account-specific URLs.")
    return {
        **base_response,
        "is_allowed": True,
        "normalized_url": normalized,
        "blocked_reason": "",
        "warnings": warnings,
    }


def fetch_public_url(
    url: str,
    *,
    purpose: str = "",
    max_excerpt_chars: int | None = None,
    allow_redirects: bool = True,
    constraints_or_notes: str = "",
) -> dict[str, Any]:
    excerpt_limit = _excerpt_limit(max_excerpt_chars)
    validation = validate_public_url(url, resolve_dns=True)
    if not validation["is_allowed"]:
        return _blocked_fetch_response(url, validation["blocked_reason"], validation)
    redirect_limit = MAX_REDIRECTS if allow_redirects else 0
    opener = urllib.request.build_opener(_safe_redirect_handler(redirect_limit)())
    request = urllib.request.Request(
        validation["normalized_url"],
        method="GET",
        headers={
            "User-Agent": "JarvisLocalReadOnlyWebResearch/0.1",
            "Accept": ", ".join(ALLOWED_CONTENT_TYPES),
        },
    )
    try:
        with opener.open(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            final_url = response.geturl()
            final_validation = validate_public_url(final_url, resolve_dns=True)
            if not final_validation["is_allowed"]:
                return _blocked_fetch_response(url, f"Final redirected URL blocked: {final_validation['blocked_reason']}", final_validation)
            status_code = int(getattr(response, "status", response.getcode() or 0))
            content_type = _clean_content_type(response.headers.get("content-type", ""))
            if not _is_allowed_content_type(content_type):
                return {
                    **_base_fetch_response(url, final_url),
                    "is_allowed": True,
                    "fetched": False,
                    "status_code": status_code,
                    "content_type": content_type,
                    "blocked_reason": "Content type is not allowed for read-only public web research.",
                    "limitations": _fetch_limitations(purpose, constraints_or_notes),
                    "safety_boundaries": list(WEB_RESEARCH_BOUNDARIES),
                }
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            truncated = len(raw) > MAX_RESPONSE_BYTES
            raw = raw[:MAX_RESPONSE_BYTES]
            text = raw.decode(_charset_from_content_type(response.headers.get("content-type", "")), errors="replace")
            title, excerpt = _extract_title_and_excerpt(text, content_type, excerpt_limit)
            limitations = _fetch_limitations(purpose, constraints_or_notes)
            if truncated:
                limitations.append("Response exceeded the byte cap; excerpt was generated from the capped prefix only.")
            return {
                **_base_fetch_response(url, final_url),
                "is_allowed": True,
                "fetched": True,
                "status_code": status_code,
                "content_type": content_type,
                "title": title,
                "excerpt": excerpt,
                "citations_or_sources": [{"source_url": url, "final_url": final_url, "title": title}],
                "blocked_reason": "",
                "limitations": limitations,
                "safety_boundaries": list(WEB_RESEARCH_BOUNDARIES),
            }
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        return {
            **_base_fetch_response(url, validation["normalized_url"]),
            "is_allowed": True,
            "fetched": False,
            "blocked_reason": f"Fetch unavailable: {_collapse_whitespace(str(exc))[:240]}",
            "limitations": _fetch_limitations(purpose, constraints_or_notes),
            "safety_boundaries": list(WEB_RESEARCH_BOUNDARIES),
        }


def agent_context_preview(
    *,
    agent_id: str,
    user_request: str,
    urls: list[str],
    output_type: str,
    web_research_enabled: bool,
    constraints_or_notes: str,
) -> dict[str, Any]:
    limited_urls = [str(url or "").strip() for url in urls[:MAX_URLS_PER_PREVIEW] if str(url or "").strip()]
    allowed_sources = []
    blocked_sources = []
    for candidate in limited_urls:
        validation = validate_public_url(candidate)
        row = {
            "url": candidate,
            "normalized_url": validation["normalized_url"],
            "blocked_reason": validation["blocked_reason"],
            "warnings": validation["warnings"],
        }
        if validation["is_allowed"]:
            allowed_sources.append(row)
        else:
            blocked_sources.append(row)
    source_summaries = [
        {
            "source_url": source["url"],
            "normalized_url": source["normalized_url"],
            "summary": "Allowed public URL source for manual context review. Agent-context preview does not fetch content or invoke an agent.",
        }
        for source in allowed_sources
    ]
    return {
        "agent_id": _collapse_whitespace(agent_id),
        "web_research_enabled": bool(web_research_enabled),
        "urls": limited_urls,
        "allowed_sources": allowed_sources if web_research_enabled else [],
        "blocked_sources": blocked_sources,
        "source_summaries": source_summaries if web_research_enabled else [],
        "not_executed_notice": "Agent context preview does not invoke agents, auto-fetch URLs, auto-submit workbench payloads, create handoffs, or persist source content.",
        "limitations": [
            "Preview validates URL suitability only; use the fetch endpoint with a manual click for bounded source excerpts.",
            "Public source context still needs user review before placing it into an agent payload.",
            f"Output type requested for preview: {_collapse_whitespace(output_type) or 'not specified'}.",
            f"User request preview: {_collapse_whitespace(user_request)[:240] or 'not provided'}.",
            f"Constraints or notes: {_collapse_whitespace(constraints_or_notes)[:240] or 'not provided'}.",
        ],
        "local_only_boundaries": list(WEB_RESEARCH_BOUNDARIES),
    }


def _blocked_host_reason(host: str) -> str:
    if host in {"localhost", "0.0.0.0"}:
        return "Localhost and unspecified hosts are blocked."
    if host.isdigit():
        return "Numeric hostnames are blocked because they can hide local IP targets."
    if "." not in host:
        return "Private or internal hostnames are blocked."
    if any(host.endswith(suffix) for suffix in BLOCKED_HOST_SUFFIXES):
        return "Private or internal hostnames are blocked."
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return ""
    if not ip.is_global:
        return "Private, local, link-local, metadata, reserved, multicast, or otherwise non-public IP targets are blocked."
    return ""


def _blocked_resolved_host_reason(host: str) -> str:
    try:
        addresses = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except OSError:
        return "Hostname could not be resolved for public-network safety validation."
    for address in addresses:
        sockaddr = address[4]
        if not sockaddr:
            continue
        ip_text = sockaddr[0]
        try:
            ip = ipaddress.ip_address(ip_text)
        except ValueError:
            return "Resolved host address could not be validated as public."
        if not ip.is_global:
            return "Resolved host points to a private, local, link-local, metadata, reserved, multicast, or otherwise non-public IP target."
    return ""


def _safe_redirect_handler(redirect_limit: int) -> type[urllib.request.HTTPRedirectHandler]:
    class SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
        max_redirections = redirect_limit
        max_repeats = redirect_limit

        def redirect_request(self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> Any:
            validation = validate_public_url(newurl, resolve_dns=True)
            if not validation["is_allowed"]:
                raise ValueError(f"Redirect target blocked: {validation['blocked_reason']}")
            return super().redirect_request(req, fp, code, msg, headers, validation["normalized_url"])

    return SafeRedirectHandler


def _base_fetch_response(url: str, final_url: str = "") -> dict[str, Any]:
    return {
        "url": str(url or "").strip(),
        "final_url": final_url,
        "is_allowed": False,
        "fetched": False,
        "status_code": None,
        "content_type": "",
        "title": "",
        "excerpt": "",
        "citations_or_sources": [],
        "blocked_reason": "",
        "limitations": [],
        "safety_boundaries": list(WEB_RESEARCH_BOUNDARIES),
    }


def _blocked_fetch_response(url: str, blocked_reason: str, validation: dict[str, Any]) -> dict[str, Any]:
    return {
        **_base_fetch_response(url, validation.get("normalized_url", "")),
        "blocked_reason": blocked_reason,
        "limitations": ["No fetch was attempted because URL validation blocked the source."],
    }


def _is_allowed_content_type(content_type: str) -> bool:
    if not content_type:
        return False
    return any(content_type.startswith(allowed) for allowed in ALLOWED_CONTENT_TYPES)


def _clean_content_type(content_type: str) -> str:
    return str(content_type or "").split(";", maxsplit=1)[0].strip().lower()


def _charset_from_content_type(content_type: str) -> str:
    match = re.search(r"charset=([\w.-]+)", content_type or "", flags=re.IGNORECASE)
    return match.group(1) if match else "utf-8"


def _extract_title_and_excerpt(text: str, content_type: str, excerpt_limit: int) -> tuple[str, str]:
    if content_type.startswith("text/html"):
        extractor = _TextExtractor(excerpt_limit)
        extractor.feed(text)
        return extractor.title, extractor.excerpt
    if content_type == "application/json":
        try:
            parsed = json.loads(text)
            text = json.dumps(parsed, ensure_ascii=False)
        except json.JSONDecodeError:
            pass
    return "", _collapse_whitespace(text)[:excerpt_limit]


def _fetch_limitations(purpose: str, constraints_or_notes: str) -> list[str]:
    limitations = list(WEB_RESEARCH_LIMITATIONS)
    purpose_text = _collapse_whitespace(purpose)
    notes_text = _collapse_whitespace(constraints_or_notes)
    if purpose_text:
        limitations.append(f"User-stated research purpose: {purpose_text[:240]}.")
    if notes_text:
        limitations.append(f"User-stated constraints: {notes_text[:240]}.")
    return limitations


def _excerpt_limit(value: int | None) -> int:
    try:
        requested = int(value or DEFAULT_EXCERPT_CHARS)
    except (TypeError, ValueError):
        requested = DEFAULT_EXCERPT_CHARS
    return min(max(requested, 200), MAX_EXCERPT_CHARS)


def _collapse_whitespace(value: str) -> str:
    return " ".join(str(value or "").split())
