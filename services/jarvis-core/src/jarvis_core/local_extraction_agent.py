from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_extraction_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_extraction"
SUPPORTED_EXTRACTION_TYPES = ("general", "action_items", "requirements", "risks", "entities", "questions", "timeline")
SUPPORTED_DETAIL_LEVELS = ("short", "medium", "detailed")


@dataclass(frozen=True)
class LocalExtractionRequest:
    content: str
    title: str = ""
    extraction_type: str = "general"
    focus_areas: list[str] = field(default_factory=list)
    must_capture: list[str] = field(default_factory=list)
    must_ignore: list[str] = field(default_factory=list)
    detail_level: str = "medium"


class LocalExtractionAgentService:
    def extract_items(self, request: LocalExtractionRequest) -> dict[str, Any]:
        title = request.title.strip()
        content = request.content.strip()
        extraction_type = _normalize_extraction_type(request.extraction_type)
        detail_level = _normalize_detail_level(request.detail_level)
        focus_areas = _clean_list(request.focus_areas)
        must_capture = _clean_list(request.must_capture)
        must_ignore = _clean_list(request.must_ignore)
        points = _extract_points(content)
        thin_content = len(content) < 80 or len(points) < 2
        limit = _detail_limit(detail_level)

        action_items = _action_items(points, extraction_type, thin_content, must_ignore, limit)
        requirements = _requirements(points, extraction_type, thin_content, must_ignore, limit)
        risks = _risks(points, extraction_type, thin_content, must_ignore, limit)
        entities = _entities(points, extraction_type, thin_content, must_ignore, limit)
        questions = _questions(points, extraction_type, thin_content, must_ignore, limit)
        timeline_items = _timeline_items(points, extraction_type, thin_content, must_ignore, limit)
        extracted_items = _extracted_items(
            points,
            must_capture,
            focus_areas,
            extraction_type,
            thin_content,
            must_ignore,
            limit,
        )

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "title": title,
            "extractionType": extraction_type,
            "detailLevel": detail_level,
            "extractionFocus": _extraction_focus(title, extraction_type, focus_areas, thin_content),
            "extractedItems": extracted_items,
            "actionItems": action_items,
            "requirements": requirements,
            "risks": risks,
            "entities": entities,
            "questions": questions,
            "timelineItems": timeline_items,
            "capturedItems": must_capture,
            "ignoredItems": must_ignore,
            "missingContext": _missing_context(content, focus_areas, must_capture, thin_content),
            "warnings": _warnings(thin_content),
            "limitations": _limitations(thin_content),
            "safety": local_extraction_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_extraction_dashboard_summary()


def local_extraction_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Extraction Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/extraction/local-extract",
        "extractionTypes": list(SUPPORTED_EXTRACTION_TYPES),
        "detailLevels": list(SUPPORTED_DETAIL_LEVELS),
        "responseOnly": True,
        "extractionPersistence": False,
        "taskCreation": False,
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
        "limitations": ["based only on user-provided extraction content"],
    }


def local_extraction_safety() -> dict[str, bool]:
    return {
        "localOnly": True,
        "responseOnly": True,
        "extractionPersistence": False,
        "taskCreation": False,
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


def _normalize_extraction_type(value: str) -> str:
    normalized = (value or "general").strip().lower()
    return normalized if normalized in SUPPORTED_EXTRACTION_TYPES else "general"


def _normalize_detail_level(value: str) -> str:
    normalized = (value or "medium").strip().lower()
    return normalized if normalized in SUPPORTED_DETAIL_LEVELS else "medium"


def _detail_limit(detail_level: str) -> int:
    return {"short": 3, "medium": 5, "detailed": 8}[detail_level]


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
        if len(points) >= 16:
            break
    return points


def _extraction_focus(title: str, extraction_type: str, focus_areas: list[str], thin_content: bool) -> str:
    subject = title or "provided text"
    if thin_content:
        return f"Limited local extraction from {subject}; content is too thin for confident structured extraction."
    if focus_areas:
        return f"Extract {extraction_type.replace('_', ' ')} from {subject}, focusing on {', '.join(focus_areas[:3])}."
    return f"Extract {extraction_type.replace('_', ' ')} from {subject} using only user-provided text."


def _extracted_items(
    points: list[str],
    must_capture: list[str],
    focus_areas: list[str],
    extraction_type: str,
    thin_content: bool,
    must_ignore: list[str],
    limit: int,
) -> list[dict[str, str]]:
    if not points and not must_capture:
        return [{"type": "limited", "text": "No substantive content was provided to extract from."}]
    selected: list[str] = []
    for item in [*must_capture, *points]:
        if item and item.lower() not in {value.lower() for value in selected}:
            selected.append(item)
        if len(selected) >= limit:
            break
    extracted = [
        {
            "type": _item_type(item, extraction_type),
            "text": _remove_ignored_items(item, must_ignore),
            "basis": "mustCapture" if item in must_capture else "userProvidedContent",
        }
        for item in selected
    ]
    if focus_areas and not thin_content:
        extracted.append(
            {
                "type": "focus",
                "text": _remove_ignored_items(f"Focus areas: {', '.join(focus_areas[:3])}.", must_ignore),
                "basis": "userProvidedFocusAreas",
            }
        )
    return extracted[: max(limit, len(must_capture[:limit]))]


def _item_type(item: str, extraction_type: str) -> str:
    if extraction_type != "general":
        return extraction_type
    lowered = item.lower()
    if _contains_any(lowered, ("todo", "action", "next", "should", "must", "need", "follow up", "owner")):
        return "action_item"
    if _contains_any(lowered, ("require", "required", "must", "shall", "needs to")):
        return "requirement"
    if _contains_any(lowered, ("risk", "blocker", "concern", "warning", "unclear", "unknown")):
        return "risk"
    if "?" in item:
        return "question"
    if _contains_any(lowered, ("today", "tomorrow", "yesterday", "week", "month", "deadline", "before", "after")):
        return "timeline"
    return "general"


def _action_items(points: list[str], extraction_type: str, thin_content: bool, must_ignore: list[str], limit: int) -> list[str]:
    if thin_content:
        return ["More content is needed before deriving reliable action items."]
    action_words = ("todo", "action", "next", "should", "must", "need", "follow up", "owner")
    actions = [point for point in points if _contains_any(point.lower(), action_words)]
    if extraction_type == "action_items" and not actions:
        actions = ["No explicit action item was found; identify owner, next step, and completion criteria manually."]
    return _clean_output_list(actions[:limit] or ["No explicit action items were detected in the supplied content."], must_ignore)


def _requirements(points: list[str], extraction_type: str, thin_content: bool, must_ignore: list[str], limit: int) -> list[str]:
    if thin_content:
        return ["More content is needed before extracting reliable requirements."]
    requirement_words = ("require", "required", "must", "shall", "needs to", "constraint", "acceptance")
    requirements = [point for point in points if _contains_any(point.lower(), requirement_words)]
    if extraction_type == "requirements" and not requirements:
        requirements = ["No explicit requirement was found; add required behavior, constraints, or acceptance criteria."]
    return _clean_output_list(requirements[:limit] or ["No explicit requirements were detected in the supplied content."], must_ignore)


def _risks(points: list[str], extraction_type: str, thin_content: bool, must_ignore: list[str], limit: int) -> list[str]:
    risk_words = ("risk", "blocker", "concern", "warning", "limit", "unclear", "unknown", "issue")
    risks = []
    if thin_content:
        risks.append("Thin content may omit important risks or caveats.")
    risks.extend(point for point in points if _contains_any(point.lower(), risk_words))
    if extraction_type == "risks" and not risks:
        risks = ["No explicit risk was found; review the supplied content manually for unstated caveats."]
    return _clean_output_list(risks[:limit] or ["No explicit risks were detected in the supplied content."], must_ignore)


def _entities(points: list[str], extraction_type: str, thin_content: bool, must_ignore: list[str], limit: int) -> list[str]:
    if thin_content:
        return ["More content is needed before extracting reliable entities."]
    candidates: list[str] = []
    for point in points:
        for match in re.findall(r"\b[A-Z][A-Za-z0-9_.-]*(?:\s+[A-Z][A-Za-z0-9_.-]*){0,3}\b", point):
            if match.lower() not in {candidate.lower() for candidate in candidates}:
                candidates.append(match)
            if len(candidates) >= limit:
                break
        if len(candidates) >= limit:
            break
    if extraction_type == "entities" and not candidates:
        candidates = ["No explicit named entities were found in the supplied content."]
    return _clean_output_list(candidates[:limit] or ["No explicit named entities were detected in the supplied content."], must_ignore)


def _questions(points: list[str], extraction_type: str, thin_content: bool, must_ignore: list[str], limit: int) -> list[str]:
    if thin_content:
        return ["More content is needed before extracting reliable questions."]
    questions = [point for point in points if "?" in point]
    if extraction_type == "questions" and not questions:
        questions = ["No explicit question was found; add open questions or decisions needed."]
    return _clean_output_list(questions[:limit] or ["No explicit questions were detected in the supplied content."], must_ignore)


def _timeline_items(points: list[str], extraction_type: str, thin_content: bool, must_ignore: list[str], limit: int) -> list[str]:
    if thin_content:
        return ["More content is needed before extracting reliable timeline items."]
    timeline_words = ("today", "tomorrow", "yesterday", "week", "month", "deadline", "before", "after", "next")
    timeline = [point for point in points if _contains_any(point.lower(), timeline_words)]
    if extraction_type == "timeline" and not timeline:
        timeline = ["No explicit timeline item was found; add dates, sequence, or deadline context."]
    return _clean_output_list(timeline[:limit] or ["No explicit timeline items were detected in the supplied content."], must_ignore)


def _missing_context(content: str, focus_areas: list[str], must_capture: list[str], thin_content: bool) -> list[str]:
    missing = []
    if thin_content:
        missing.append("More source text is needed for reliable extraction.")
    if not content.strip():
        missing.append("Content was empty.")
    if not focus_areas:
        missing.append("No focus areas were provided.")
    if not must_capture:
        missing.append("No must-capture items were provided.")
    return missing or ["No obvious missing context was detected from the supplied extraction inputs."]


def _warnings(thin_content: bool) -> list[str]:
    if thin_content:
        return ["Extraction content is thin; output is a limited local extraction."]
    return []


def _limitations(thin_content: bool) -> list[str]:
    limitations = [
        "Based only on user-provided extraction content.",
        "No source verification, citation verification, external fact checking, document retrieval, repo inspection, file reading, task creation, persistence, code execution, or test execution was performed.",
        "No files, database records, tasks, extracted items, emails, posts, purchases, downloads, uploads, connectors, accounts, shell commands, or external services were used.",
    ]
    if thin_content:
        limitations.append("Thin content limits specificity; add more source text for stronger extraction.")
    return limitations


def _contains_any(value: str, terms: tuple[str, ...]) -> bool:
    return any(term in value for term in terms)


def _remove_ignored_items(text: str, must_ignore: list[str]) -> str:
    cleaned = text
    for item in must_ignore:
        cleaned = re.sub(re.escape(item), "[ignored]", cleaned, flags=re.IGNORECASE)
    return cleaned


def _clean_output_list(values: list[str], must_ignore: list[str]) -> list[str]:
    return [_remove_ignored_items(value, must_ignore) for value in values]
