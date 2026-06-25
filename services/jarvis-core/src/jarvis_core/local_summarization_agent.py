from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_summarization_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_summarization"
SUPPORTED_SUMMARY_TYPES = ("general", "bullets", "executive", "action_items", "study_notes", "risks")
SUPPORTED_DETAIL_LEVELS = ("short", "medium", "detailed")


@dataclass(frozen=True)
class LocalSummarizationRequest:
    content: str
    title: str = ""
    summary_type: str = "general"
    audience: str = ""
    detail_level: str = "medium"
    focus_areas: list[str] = field(default_factory=list)
    must_preserve: list[str] = field(default_factory=list)
    must_avoid: list[str] = field(default_factory=list)


class LocalSummarizationAgentService:
    def create_summary(self, request: LocalSummarizationRequest) -> dict[str, Any]:
        title = request.title.strip()
        content = request.content.strip()
        summary_type = _normalize_summary_type(request.summary_type)
        detail_level = _normalize_detail_level(request.detail_level)
        audience = request.audience.strip()
        focus_areas = _clean_list(request.focus_areas)
        must_preserve = _clean_list(request.must_preserve)
        must_avoid = _clean_list(request.must_avoid)
        points = _extract_points(content)
        thin_content = len(content) < 80 or len(points) < 2

        key_points = _key_points(points, focus_areas, must_preserve, detail_level, thin_content)
        summary = _summary_text(title, summary_type, detail_level, audience, key_points, focus_areas, must_preserve, thin_content)
        summary = _remove_avoided_items(summary, must_avoid)

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "title": title,
            "summaryType": summary_type,
            "detailLevel": detail_level,
            "audience": audience,
            "summary": summary,
            "keyPoints": _remove_avoided_from_list(key_points, must_avoid),
            "actionItems": _action_items(points, summary_type, thin_content, must_avoid),
            "risksOrCaveats": _risks_or_caveats(points, summary_type, thin_content, must_avoid),
            "preservedItems": must_preserve,
            "avoidedItems": must_avoid,
            "missingContext": _missing_context(content, focus_areas, must_preserve, thin_content),
            "warnings": _warnings(thin_content),
            "limitations": _limitations(thin_content),
            "safety": local_summarization_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_summarization_dashboard_summary()


def local_summarization_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Summarization Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/summarization/local-summary",
        "summaryTypes": list(SUPPORTED_SUMMARY_TYPES),
        "detailLevels": list(SUPPORTED_DETAIL_LEVELS),
        "responseOnly": True,
        "summaryPersistence": False,
        "sourceValidation": False,
        "citationValidation": False,
        "externalFactChecking": False,
        "documentRetrieval": False,
        "testExecution": False,
        "repoInspection": False,
        "taskPersistence": False,
        "dbWrites": False,
        "externalServices": False,
        "paidApis": False,
        "webBrowsing": False,
        "connectorExecution": False,
        "oauth": False,
        "accountAccess": False,
        "gmailCalendarSocialAccess": False,
        "postingOrSending": False,
        "purchases": False,
        "fileReads": False,
        "fileWrites": False,
        "shellExecution": False,
        "downloads": False,
        "uploads": False,
        "mutation": False,
        "limitations": ["based only on user-provided summarization content"],
    }


def local_summarization_safety() -> dict[str, bool]:
    return {
        "localOnly": True,
        "responseOnly": True,
        "summaryPersistence": False,
        "externalServices": False,
        "paidApis": False,
        "webBrowsing": False,
        "connectorExecution": False,
        "oauth": False,
        "accountAccess": False,
        "gmailAccess": False,
        "calendarAccess": False,
        "socialAccess": False,
        "postingOrSending": False,
        "emailSending": False,
        "publicPosting": False,
        "purchases": False,
        "taskPersistence": False,
        "dbWrites": False,
        "fileReads": False,
        "fileWrites": False,
        "shellExecution": False,
        "downloads": False,
        "uploads": False,
        "mutation": False,
        "repoInspection": False,
        "testExecution": False,
        "sourceValidation": False,
        "citationValidation": False,
        "externalFactChecking": False,
        "documentRetrieval": False,
    }


def _normalize_summary_type(value: str) -> str:
    normalized = (value or "general").strip().lower()
    return normalized if normalized in SUPPORTED_SUMMARY_TYPES else "general"


def _normalize_detail_level(value: str) -> str:
    normalized = (value or "medium").strip().lower()
    return normalized if normalized in SUPPORTED_DETAIL_LEVELS else "medium"


def _clean_list(values: list[str]) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = re.sub(r"\s+", " ", value.strip())
        key = item.lower()
        if item and key not in seen:
            cleaned.append(item)
            seen.add(key)
    return cleaned[:10]


def _extract_points(content: str) -> list[str]:
    if not content:
        return []
    raw_parts = re.split(r"(?:\r?\n+|(?<=[.!?])\s+|[;:•]+)", content)
    points: list[str] = []
    seen: set[str] = set()
    for part in raw_parts:
        cleaned = re.sub(r"^\s*[-*#\d.)]+\s*", "", part).strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        points.append(cleaned)
        if len(points) >= 12:
            break
    return points


def _key_points(
    points: list[str],
    focus_areas: list[str],
    must_preserve: list[str],
    detail_level: str,
    thin_content: bool,
) -> list[str]:
    if not points and not must_preserve:
        return ["No substantive content was provided to summarize."]
    limit = {"short": 3, "medium": 5, "detailed": 8}[detail_level]
    selected: list[str] = []
    for item in [*must_preserve, *points]:
        if item and item.lower() not in {point.lower() for point in selected}:
            selected.append(item)
        if len(selected) >= limit:
            break
    if focus_areas and not thin_content:
        selected.append(f"Focus lens: {', '.join(focus_areas[:3])}.")
    return selected[: max(limit, len(must_preserve[:limit]))]


def _summary_text(
    title: str,
    summary_type: str,
    detail_level: str,
    audience: str,
    key_points: list[str],
    focus_areas: list[str],
    must_preserve: list[str],
    thin_content: bool,
) -> str:
    title_prefix = f"{title}: " if title else ""
    audience_note = f" for {audience}" if audience else ""
    if thin_content:
        base = f"{title_prefix}Limited local summary{audience_note}: the supplied content is too thin for a confident summary."
        if key_points:
            return f"{base} Available point: {key_points[0]}"
        return base
    if summary_type == "bullets":
        return "\n".join(f"- {point}" for point in key_points)
    if summary_type == "executive":
        return f"{title_prefix}Executive summary{audience_note}: {_join_points(key_points[:4])}"
    if summary_type == "action_items":
        return f"{title_prefix}Action-oriented summary{audience_note}: {_join_points(key_points[:4])}"
    if summary_type == "study_notes":
        return f"{title_prefix}Study notes{audience_note}: {_join_points(key_points)}"
    if summary_type == "risks":
        return f"{title_prefix}Risk-focused summary{audience_note}: {_join_points(key_points[:5])}"
    if detail_level == "short":
        return f"{title_prefix}{_join_points(key_points[:2])}"
    if focus_areas:
        return f"{title_prefix}Summary{audience_note} focused on {', '.join(focus_areas[:3])}: {_join_points(key_points)}"
    if must_preserve:
        return f"{title_prefix}Summary{audience_note}: {_join_points(key_points)}"
    return f"{title_prefix}Summary{audience_note}: {_join_points(key_points)}"


def _join_points(points: list[str]) -> str:
    if not points:
        return "No substantive content was provided."
    return " ".join(point.rstrip(".") + "." for point in points)


def _action_items(points: list[str], summary_type: str, thin_content: bool, must_avoid: list[str]) -> list[str]:
    if thin_content:
        return ["Provide more content before deriving reliable action items."]
    action_words = ("todo", "action", "next", "should", "must", "need", "follow up", "owner")
    actions = [point for point in points if any(word in point.lower() for word in action_words)]
    if summary_type == "action_items" and not actions:
        actions = ["Identify owners, next steps, and completion criteria from the supplied content."]
    return _remove_avoided_from_list(actions[:5] or ["No explicit action items were detected in the supplied content."], must_avoid)


def _risks_or_caveats(points: list[str], summary_type: str, thin_content: bool, must_avoid: list[str]) -> list[str]:
    caveats = []
    risk_words = ("risk", "caveat", "blocker", "issue", "warning", "limit", "unclear", "unknown", "concern")
    if thin_content:
        caveats.append("Thin content may omit important context or caveats.")
    caveats.extend(point for point in points if any(word in point.lower() for word in risk_words))
    if summary_type == "risks" and not caveats:
        caveats.append("No explicit risks were detected; review the supplied content manually for unstated caveats.")
    return _remove_avoided_from_list(caveats[:6] or ["No explicit risks or caveats were detected in the supplied content."], must_avoid)


def _missing_context(content: str, focus_areas: list[str], must_preserve: list[str], thin_content: bool) -> list[str]:
    missing = []
    if thin_content:
        missing.append("More source text is needed for a reliable summary.")
    if not content.strip():
        missing.append("Content was empty.")
    if not focus_areas:
        missing.append("No focus areas were provided.")
    if not must_preserve:
        missing.append("No must-preserve items were provided.")
    return missing or ["No obvious missing context was detected from the supplied summarization inputs."]


def _remove_avoided_items(text: str, must_avoid: list[str]) -> str:
    cleaned = text
    for item in must_avoid:
        cleaned = re.sub(re.escape(item), "[omitted]", cleaned, flags=re.IGNORECASE)
    return cleaned


def _remove_avoided_from_list(values: list[str], must_avoid: list[str]) -> list[str]:
    return [_remove_avoided_items(value, must_avoid) for value in values]


def _warnings(thin_content: bool) -> list[str]:
    if thin_content:
        return ["Summarization content is thin; output is a limited local summary."]
    return []


def _limitations(thin_content: bool) -> list[str]:
    limitations = [
        "Based only on user-provided summarization content.",
        "No source verification, citation verification, external fact checking, document retrieval, repo inspection, file reading, code execution, or test execution was performed.",
        "No files, database records, tasks, summaries, emails, posts, purchases, downloads, uploads, connectors, accounts, shell commands, or external services were used.",
    ]
    if thin_content:
        limitations.append("Thin content limits specificity; add more source text for a stronger summary.")
    return limitations
