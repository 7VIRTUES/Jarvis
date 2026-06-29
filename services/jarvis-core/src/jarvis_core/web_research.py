from __future__ import annotations

import ipaddress
import json
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
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
MAX_WEB_CONTEXT_SOURCES = 5
MAX_WEB_CONTEXT_EXCERPT_CHARS = 4000

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
WEB_CONTEXT_RESPONSE_LIMITATIONS = [
    "web_context is optional reviewed source context supplied in the manual request payload.",
    "Local response agents do not browse, fetch, search, follow links, or verify live source freshness.",
    "web_context is not persisted by the response-agent endpoints.",
    "Source excerpts should be reviewed by the user before relying on them.",
    "Citation labels are for reference, not certification or proof.",
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
            "web_context_supported": True,
            "web_context_is_optional": True,
            "web_context_is_non_persistent": True,
            "agents_do_not_auto_browse": True,
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
        "web_context_supported": True,
        "webContextSupported": True,
        "web_context_is_optional": True,
        "webContextIsOptional": True,
        "web_context_is_non_persistent": True,
        "webContextIsNonPersistent": True,
        "web_research_requires_manual_fetch": True,
        "webResearchRequiresManualFetch": True,
        "agents_do_not_auto_browse": True,
        "agentsDoNotAutoBrowse": True,
        "source_evidence_supported": True,
        "sourceEvidenceSupported": True,
        "citation_labels_supported": True,
        "citationLabelsSupported": True,
        "source_recency_flags_supported": True,
        "sourceRecencyFlagsSupported": True,
        "source_aware_response_supported": True,
        "sourceAwareResponseSupported": True,
    }


def build_web_context_template_sample() -> list[dict[str, Any]]:
    return [
        {
            "source_url": "https://example.com/public-source",
            "final_url": "https://example.com/public-source",
            "title": "Example public source",
            "excerpt": "Short reviewed public excerpt for manual testing only.",
            "content_type": "text/plain",
            "fetched": True,
            "user_notes": "Optional reviewer notes about why this excerpt is relevant.",
            "source_type": "public_web_excerpt",
            "limitations": list(WEB_CONTEXT_RESPONSE_LIMITATIONS),
        }
    ]


def normalize_web_context(raw_context: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_context, list):
        return []
    normalized: list[dict[str, Any]] = []
    seen_source_keys: set[str] = set()
    for raw_source in raw_context:
        if not isinstance(raw_source, dict):
            continue
        source_url = _clean_web_context_url(raw_source.get("source_url") or raw_source.get("url"))
        final_url = _clean_web_context_url(raw_source.get("final_url") or raw_source.get("finalUrl"))
        if source_url:
            validation = validate_public_url(source_url)
            if not validation["is_allowed"]:
                continue
            source_url = validation["normalized_url"]
        if final_url:
            validation = validate_public_url(final_url)
            if not validation["is_allowed"]:
                final_url = ""
            else:
                final_url = validation["normalized_url"]
        source_key = _source_dedupe_key(source_url, final_url)
        if source_key and source_key in seen_source_keys:
            continue
        if source_key:
            seen_source_keys.add(source_key)
        excerpt = _collapse_whitespace(raw_source.get("excerpt", ""))[:MAX_WEB_CONTEXT_EXCERPT_CHARS]
        if not excerpt:
            continue
        source_index = len(normalized) + 1
        source = {
            "source_url": source_url,
            "final_url": final_url,
            "title": _collapse_whitespace(raw_source.get("title", ""))[:240],
            "excerpt": excerpt,
            "content_type": _collapse_whitespace(raw_source.get("content_type") or raw_source.get("contentType") or "")[:120],
            "fetched": bool(raw_source.get("fetched", False)),
            "fetched_at": _collapse_whitespace(raw_source.get("fetched_at") or raw_source.get("fetchedAt") or "")[:120],
            "user_notes": _collapse_whitespace(raw_source.get("user_notes") or raw_source.get("userNotes") or "")[:500],
            "source_type": _collapse_whitespace(raw_source.get("source_type") or raw_source.get("sourceType") or "public_web_excerpt")[:80],
            "limitations": _normalize_limitations(raw_source.get("limitations")),
        }
        normalized.append(_source_evidence_item(source, source_index))
        if len(normalized) >= MAX_WEB_CONTEXT_SOURCES:
            break
    return normalized


def summarize_web_context(web_context: Any) -> str:
    sources = normalize_web_context(web_context)
    if not sources:
        return "No reviewed public source context was provided."
    titled = [source["title"] or source["source_url"] or "Untitled reviewed source" for source in sources]
    return f"{len(sources)} reviewed public source excerpt(s) were supplied: {', '.join(titled[:3])}."


def build_sources_used(web_context: Any) -> list[dict[str, Any]]:
    return [
        {
            "source_id": source["source_id"],
            "citation_label": source["citation_label"],
            "source_url": source["source_url"],
            "final_url": source["final_url"],
            "title": source["title"],
            "domain": source["domain"],
            "source_type": source["source_type"],
        }
        for source in normalize_web_context(web_context)
    ]


def build_source_evidence(web_context: Any) -> list[dict[str, Any]]:
    return normalize_web_context(web_context)


def build_citation_labels(web_context: Any) -> list[str]:
    return [source["citation_label"] for source in normalize_web_context(web_context)]


def build_source_quality_warnings(web_context: Any) -> list[str]:
    warnings: list[str] = []
    for source in normalize_web_context(web_context):
        warnings.extend(source["quality_warnings"])
    return warnings


def build_source_recency_notes(web_context: Any) -> list[str]:
    return [source["recency_note"] for source in normalize_web_context(web_context)]


def build_web_context_limitations(web_context: Any) -> list[str]:
    sources = normalize_web_context(web_context)
    if not sources:
        return ["No web_context was provided; the agent used only the manual request payload."]
    return list(WEB_CONTEXT_RESPONSE_LIMITATIONS)


def build_source_aware_context(agent_id: str, category: str, web_context: Any) -> dict[str, Any]:
    evidence = build_source_evidence(web_context)
    return {
        "source_use_summary": _source_use_summary(agent_id, category, evidence),
        "source_supported_points": build_source_supported_points(web_context),
        "source_cautions": build_source_cautions(web_context, category),
        "source_followup_checks": build_source_followup_checks(web_context, category),
        "source_informed_assumptions": _source_informed_assumptions(evidence),
        "citation_usage_note": _citation_usage_note(evidence),
    }


def build_source_supported_points(web_context: Any) -> list[str]:
    points = []
    for source in build_source_evidence(web_context):
        title_or_domain = source["title"] or source["domain"] or "untitled reviewed source"
        excerpt_preview = _collapse_whitespace(source["excerpt"])[:220]
        points.append(
            f"{source['citation_label']} can support local response context from {title_or_domain}: {excerpt_preview}"
        )
    return points


def build_source_cautions(web_context: Any, category: str) -> list[str]:
    evidence = build_source_evidence(web_context)
    if not evidence:
        return []
    cautions: list[str] = []
    for source in evidence:
        cautions.extend(source["quality_warnings"])
        cautions.append(source["recency_note"])
    cautions.extend(_category_source_cautions(category))
    cautions.append("Reviewed excerpts are supporting context only; they are not proof, certification, or independent fact-checking.")
    return _unique_text(cautions)


def build_source_followup_checks(web_context: Any, category: str) -> list[str]:
    evidence = build_source_evidence(web_context)
    if not evidence:
        return []
    labels = ", ".join(source["citation_label"] for source in evidence)
    checks = [
        f"Review the full source text for {labels} before acting on source-specific details.",
        "Manually verify source freshness, source authority, and exact details before relying on the excerpts.",
        "Treat source-supported output as conditional on the reviewed excerpts being accurate, current, and relevant.",
    ]
    checks.extend(_category_followup_checks(category))
    return _unique_text(checks)


def apply_source_aware_response_fields(
    response: dict[str, Any],
    agent_id: str,
    category: str,
    web_context: Any,
) -> dict[str, Any]:
    enriched = add_web_context_response_fields(response, web_context)
    enriched.update(build_source_aware_context(agent_id, category, web_context))
    return enriched


def add_web_context_response_fields(response: dict[str, Any], web_context: Any) -> dict[str, Any]:
    enriched = dict(response)
    enriched["source_evidence"] = build_source_evidence(web_context)
    enriched["citation_labels"] = build_citation_labels(web_context)
    enriched["source_quality_warnings"] = build_source_quality_warnings(web_context)
    enriched["source_recency_notes"] = build_source_recency_notes(web_context)
    enriched["source_context_summary"] = summarize_web_context(web_context)
    enriched["sources_used"] = build_sources_used(web_context)
    enriched["web_context_limitations"] = build_web_context_limitations(web_context)
    return enriched


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
            fetched_at = datetime.now(timezone.utc).isoformat()
            return {
                **_base_fetch_response(url, final_url),
                "is_allowed": True,
                "fetched": True,
                "fetched_at": fetched_at,
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


def _clean_web_context_url(value: Any) -> str:
    return str(value or "").strip()[:1000]


def _source_use_summary(agent_id: str, category: str, evidence: list[dict[str, Any]]) -> str:
    if not evidence:
        return "No reviewed source context was provided; source-aware response sections are empty."
    labels = ", ".join(source["citation_label"] for source in evidence)
    agent_text = _collapse_whitespace(agent_id) or "local response agent"
    category_text = _collapse_whitespace(category) or "general"
    return (
        f"{agent_text} used {len(evidence)} reviewed source excerpt(s) as supporting context for {category_text}: "
        f"{labels}. The agent did not browse, search, fetch, follow links, or independently verify these sources."
    )


def _source_informed_assumptions(evidence: list[dict[str, Any]]) -> list[str]:
    if not evidence:
        return []
    labels = ", ".join(source["citation_label"] for source in evidence)
    return [
        f"Source-informed points are limited to the reviewed excerpts labeled {labels}.",
        "Any source-informed recommendation is conditional on the excerpts being accurate, current, and relevant.",
        "Unprovided pages, linked pages, account-only content, and live updates were not reviewed by the local response agent.",
    ]


def _citation_usage_note(evidence: list[dict[str, Any]]) -> str:
    if not evidence:
        return "No citation labels were used because no web_context was provided."
    labels = ", ".join(source["citation_label"] for source in evidence)
    return f"Citation labels {labels} refer only to reviewed excerpts in the manual payload; they are not proof, certification, live verification, or source authority validation."


def _category_source_cautions(category: str) -> list[str]:
    normalized = _collapse_whitespace(category).lower()
    if normalized == "health/food/home":
        return [
            "Reviewed web excerpts are not clinical advice, diagnosis, treatment, allergy certainty, food-safety certification, or diet prescription.",
            "High-stakes health, fitness, food, allergy, or safety decisions require qualified professionals or official sources.",
        ]
    if normalized == "safety/emergency":
        return [
            "Reviewed web excerpts are not legal advice, filing certainty, live emergency awareness, dispatch, alerting, evacuation-order verification, real-time hazard awareness, or security certification.",
            "Immediate danger requires local emergency services or official emergency channels.",
        ]
    if normalized == "finance/housing/travel":
        return [
            "Reviewed web excerpts are not financial advice and do not provide APR, loan, aid, benefit, price, availability, booking, application, or transaction certainty.",
            "Financial, housing, moving, and travel details require manual verification with official or qualified sources before action.",
        ]
    if normalized == "school/career":
        return [
            "Reviewed web excerpts do not guarantee admission, enrollment, grades, scholarships, hiring, salary, policy acceptance, or placement outcomes.",
            "School, program, employer, and policy details require manual verification with the official source.",
        ]
    if normalized == "social/family":
        return [
            "Reviewed web excerpts are not therapy, diagnosis, crisis intervention, professional counseling, or a relationship outcome guarantee.",
            "Urgent mental-health or safety concerns require appropriate professional, crisis, or local support.",
        ]
    return [
        "Reviewed web excerpts are supporting context only and require manual review of source freshness, source authority, and exact details before action.",
    ]


def _category_followup_checks(category: str) -> list[str]:
    normalized = _collapse_whitespace(category).lower()
    if normalized == "health/food/home":
        return ["For medical, allergy, nutrition, food-safety, or injury-sensitive choices, confirm with qualified professionals or official safety guidance."]
    if normalized == "safety/emergency":
        return ["For emergency, legal, immigration, official, security, or hazard-sensitive choices, confirm with qualified professionals, official agencies, or local emergency services as appropriate."]
    if normalized == "finance/housing/travel":
        return ["Before financial, loan, housing, travel, or booking-related action, verify terms, eligibility, availability, prices, and deadlines with official sources."]
    if normalized == "school/career":
        return ["Before school, robotics, career, job, or portfolio action, verify policies, deadlines, requirements, and outcomes with the official program or employer."]
    if normalized == "social/family":
        return ["For relationship, emotional reflection, resilience, or crisis-sensitive choices, consider qualified professional or crisis support where appropriate."]
    return ["Before taking action, verify the relevant source authority, dates, and details manually."]


def _source_dedupe_key(source_url: str, final_url: str) -> str:
    return (final_url or source_url or "").strip().lower()


def _source_evidence_item(source: dict[str, Any], source_index: int) -> dict[str, Any]:
    source_id = f"S{source_index}"
    citation_label = f"[{source_id}]"
    domain = _safe_domain(source.get("final_url") or source.get("source_url") or "")
    quality_warnings = _source_quality_warnings(source, citation_label)
    recency_note = _source_recency_note(source.get("fetched_at", ""), citation_label)
    limitations = _normalize_limitations(source.get("limitations"))
    for limitation in (
        "Excerpt may be partial and should be reviewed against the original source before action.",
        "This source was user-reviewed source context, not independently verified by the local response agent.",
        "Citation label is for reference only and is not proof or certification.",
    ):
        if limitation not in limitations:
            limitations.append(limitation)
    return {
        "source_id": source_id,
        "citation_label": citation_label,
        "source_url": source.get("source_url", ""),
        "final_url": source.get("final_url", ""),
        "title": source.get("title", ""),
        "domain": domain,
        "excerpt": source.get("excerpt", ""),
        "content_type": source.get("content_type", ""),
        "fetched": bool(source.get("fetched", False)),
        "fetched_at": source.get("fetched_at", ""),
        "user_notes": source.get("user_notes", ""),
        "source_type": source.get("source_type", "public_web_excerpt"),
        "recency_note": recency_note,
        "quality_warnings": quality_warnings,
        "limitations": limitations,
    }


def _safe_domain(url: str) -> str:
    try:
        parsed = urllib.parse.urlsplit(str(url or "").strip())
    except ValueError:
        return ""
    return (parsed.hostname or "").strip().lower()


def _source_quality_warnings(source: dict[str, Any], citation_label: str) -> list[str]:
    warnings = [
        f"{citation_label} is a reviewed excerpt only; the local response agent did not independently verify the source.",
        f"{citation_label} may be partial because excerpts are bounded to {MAX_WEB_CONTEXT_EXCERPT_CHARS} characters.",
    ]
    if not source.get("title"):
        warnings.append(f"{citation_label} has no title in the reviewed source context.")
    if not source.get("source_url") and not source.get("final_url"):
        warnings.append(f"{citation_label} has no public source URL in the reviewed source context.")
    if _url_has_query(source.get("source_url", "")) or _url_has_query(source.get("final_url", "")):
        warnings.append(f"{citation_label} URL includes a query string; review it for identifiers before use.")
    if not source.get("fetched_at"):
        warnings.append(f"{citation_label} has no fetched_at timestamp in the reviewed source context.")
    return warnings


def _source_recency_note(fetched_at: str, citation_label: str) -> str:
    value = _collapse_whitespace(fetched_at)
    if not value:
        return f"{citation_label} recency unknown: no fetched_at timestamp was supplied."
    parsed = _parse_timestamp(value)
    if parsed is None:
        return f"{citation_label} recency unknown: fetched_at timestamp could not be parsed."
    age_days = (datetime.now(timezone.utc) - parsed).days
    if age_days > 365:
        return f"{citation_label} may be stale: fetched_at is more than 365 days old."
    return f"{citation_label} fetched_at timestamp was supplied; source freshness still requires manual review."


def _parse_timestamp(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _url_has_query(url: str) -> bool:
    try:
        return bool(urllib.parse.urlsplit(str(url or "").strip()).query)
    except ValueError:
        return False


def _unique_text(values: list[str]) -> list[str]:
    unique = []
    seen = set()
    for value in values:
        cleaned = _collapse_whitespace(value)
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            unique.append(cleaned)
    return unique


def _normalize_limitations(value: Any) -> list[str]:
    if isinstance(value, str):
        values = [value]
    elif isinstance(value, list):
        values = value
    else:
        values = []
    return [_collapse_whitespace(item)[:240] for item in values[:8] if _collapse_whitespace(item)]


def _collapse_whitespace(value: str) -> str:
    return " ".join(str(value or "").split())
