from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_drafting_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_drafting"
SUPPORTED_FORMATS = ("message", "email_draft", "document_section", "checklist", "announcement")


@dataclass(frozen=True)
class LocalDraftingRequest:
    purpose: str
    notes: str
    audience: str = ""
    tone: str = "clear"
    draft_format: str = "message"
    constraints: list[str] = field(default_factory=list)
    must_include: list[str] = field(default_factory=list)
    must_avoid: list[str] = field(default_factory=list)


class LocalDraftingAgentService:
    def create_draft(self, request: LocalDraftingRequest) -> dict[str, Any]:
        purpose = request.purpose.strip() or "Untitled local drafting purpose"
        audience = request.audience.strip()
        tone = request.tone.strip() or "clear"
        draft_format = _normalize_format(request.draft_format)
        notes = request.notes.strip()
        note_points = _extract_points(notes)
        constraints = _clean_list(request.constraints)
        must_include = _clean_list(request.must_include)
        must_avoid = _clean_list(request.must_avoid)
        thin_notes = len(notes) < 40 or len(note_points) < 2

        included_points = _included_points(note_points, must_include)
        draft_text = _draft_text(purpose, audience, tone, draft_format, included_points, constraints, must_avoid, thin_notes)

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "purpose": purpose,
            "audience": audience,
            "format": draft_format,
            "tone": tone,
            "draftTitle": _draft_title(purpose, draft_format),
            "draftText": draft_text,
            "includedPoints": included_points,
            "avoidedItems": must_avoid,
            "revisionNotes": _revision_notes(draft_format, constraints, must_avoid, thin_notes),
            "warnings": _warnings(draft_format, thin_notes),
            "limitations": _limitations(draft_format, thin_notes),
            "safety": local_drafting_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_drafting_dashboard_summary()


def local_drafting_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Drafting Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/drafting/local-draft",
        "formats": list(SUPPORTED_FORMATS),
        "responseOnly": True,
        "draftPersistence": False,
        "emailSending": False,
        "publicPosting": False,
        "gmailCalendarSocialAccess": False,
        "taskPersistence": False,
        "dbWrites": False,
        "externalServices": False,
        "paidApis": False,
        "webBrowsing": False,
        "connectorExecution": False,
        "oauth": False,
        "accountAccess": False,
        "fileReads": False,
        "fileWrites": False,
        "shellExecution": False,
        "uploads": False,
        "mutation": False,
        "limitations": ["based only on user-provided drafting inputs"],
    }


def local_drafting_safety() -> dict[str, bool]:
    return {
        "localOnly": True,
        "responseOnly": True,
        "draftPersistence": False,
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
        "taskPersistence": False,
        "dbWrites": False,
        "fileReads": False,
        "fileWrites": False,
        "shellExecution": False,
        "uploads": False,
        "mutation": False,
    }


def _normalize_format(value: str) -> str:
    normalized = (value or "message").strip().lower()
    return normalized if normalized in SUPPORTED_FORMATS else "message"


def _extract_points(notes: str) -> list[str]:
    if not notes:
        return []
    raw_parts = re.split(r"(?:\r?\n+|(?<=[.!?])\s+|[;•]+)", notes)
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
        if len(points) >= 8:
            break
    return points


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


def _included_points(note_points: list[str], must_include: list[str]) -> list[str]:
    included: list[str] = []
    for item in [*must_include, *note_points]:
        if item and item.lower() not in {point.lower() for point in included}:
            included.append(item)
        if len(included) >= 8:
            break
    return included or ["No substantive note points were provided."]


def _draft_title(purpose: str, draft_format: str) -> str:
    label = draft_format.replace("_", " ").title()
    return f"{label}: {purpose}"


def _draft_text(
    purpose: str,
    audience: str,
    tone: str,
    draft_format: str,
    included_points: list[str],
    constraints: list[str],
    must_avoid: list[str],
    thin_notes: bool,
) -> str:
    audience_line = f" for {audience}" if audience else ""
    if draft_format == "checklist":
        lines = [f"Checklist{audience_line}: {purpose}"]
        lines.extend(f"- {point}" for point in included_points)
    elif draft_format == "document_section":
        lines = [f"## {purpose}", "", f"Tone: {tone}.", ""]
        lines.extend(f"- {point}" for point in included_points)
    elif draft_format == "announcement":
        lines = [f"Announcement{audience_line}: {purpose}", "", _join_points(included_points)]
    elif draft_format == "email_draft":
        greeting = f"Hello {audience}," if audience else "Hello,"
        lines = [
            f"Subject: {purpose}",
            "",
            greeting,
            "",
            _join_points(included_points),
            "",
            "Regards,",
            "[Your name]",
        ]
    else:
        lines = [f"{purpose}{audience_line}", "", _join_points(included_points)]
    if constraints:
        lines.extend(["", "Revision constraints:", *[f"- {constraint}" for constraint in constraints]])
    if thin_notes:
        lines.extend(["", "Note: This draft is provisional because the provided notes were thin."])
    return _remove_avoided_items("\n".join(lines).strip(), must_avoid)


def _join_points(points: list[str]) -> str:
    if len(points) == 1:
        return points[0]
    return " ".join(point.rstrip(".") + "." for point in points)


def _remove_avoided_items(text: str, must_avoid: list[str]) -> str:
    cleaned = text
    for item in must_avoid:
        cleaned = re.sub(re.escape(item), "[omitted]", cleaned, flags=re.IGNORECASE)
    return cleaned


def _revision_notes(draft_format: str, constraints: list[str], must_avoid: list[str], thin_notes: bool) -> list[str]:
    notes = ["Review the draft against the stated purpose, audience, tone, and format."]
    if draft_format == "email_draft":
        notes.append("Email format is draft-only; no sending, saving, Gmail access, or connector action was performed.")
    if constraints:
        notes.append("Check the draft against each user-provided constraint.")
    if must_avoid:
        notes.append("Avoided items were omitted when they appeared in generated draft text.")
    if thin_notes:
        notes.append("Add more notes before treating the draft as final.")
    return notes


def _warnings(draft_format: str, thin_notes: bool) -> list[str]:
    warnings: list[str] = []
    if thin_notes:
        warnings.append("Drafting notes are thin; output is a provisional local draft.")
    if draft_format == "email_draft":
        warnings.append("Email draft is text only; no email was sent or saved.")
    return warnings


def _limitations(draft_format: str, thin_notes: bool) -> list[str]:
    limitations = [
        "Based only on user-provided drafting inputs.",
        "No files, database records, tasks, connector drafts, emails, posts, or account actions were created.",
        "No external services, paid APIs, connectors, shell commands, uploads, file reads, or file writes were used.",
    ]
    if draft_format == "email_draft":
        limitations.append("Email draft format only creates response text; it does not use Gmail or send email.")
    if thin_notes:
        limitations.append("Thin notes limit specificity; add more notes for a stronger draft.")
    return limitations
