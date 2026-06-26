from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_transformation_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_transformation"
SUPPORTED_TARGET_FORMATS = (
    "outline",
    "checklist",
    "table",
    "sop_steps",
    "flashcards",
    "json_style",
    "csv_style",
    "cleaned_notes",
)
SUPPORTED_DETAIL_LEVELS = ("short", "medium", "detailed")


@dataclass(frozen=True)
class LocalTransformationRequest:
    title: str = ""
    content: str = ""
    items: list[str] = field(default_factory=list)
    target_format: str = "outline"
    audience: str = ""
    constraints: list[str] = field(default_factory=list)
    must_preserve: list[str] = field(default_factory=list)
    must_avoid: list[str] = field(default_factory=list)
    detail_level: str = "medium"


class LocalTransformationAgentService:
    def transform(self, request: LocalTransformationRequest) -> dict[str, Any]:
        title = request.title.strip()
        content = request.content.strip()
        target_format = _normalize_target_format(request.target_format)
        detail_level = _normalize_detail_level(request.detail_level)
        audience = request.audience.strip()
        constraints = _clean_list(request.constraints)
        must_preserve = _clean_list(request.must_preserve)
        must_avoid = _clean_list(request.must_avoid)
        content_points = _extract_points(content)
        items = _clean_list(request.items, limit=16)
        source_items = _source_items(items, content_points, must_preserve, detail_level)
        thin_input = not source_items or (not items and len(content) < 80 and len(content_points) < 2)

        outline = _outline(source_items, thin_input, must_avoid)
        checklist = _checklist(source_items, thin_input, must_avoid)
        table_rows = _table_rows(source_items, thin_input, must_avoid)
        sop_steps = _sop_steps(source_items, thin_input, must_avoid)
        flashcards = _flashcards(source_items, thin_input, must_avoid)
        json_style_text = _json_style_text(title, source_items, thin_input, must_avoid)
        csv_style_text = _csv_style_text(source_items, thin_input, must_avoid)
        cleaned_notes = _cleaned_notes(source_items, thin_input, must_avoid)
        transformed_text = _transformed_text(
            target_format,
            outline,
            checklist,
            table_rows,
            sop_steps,
            flashcards,
            json_style_text,
            csv_style_text,
            cleaned_notes,
        )

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "title": title,
            "targetFormat": target_format,
            "detailLevel": detail_level,
            "audience": audience,
            "transformationFocus": _transformation_focus(title, target_format, audience, constraints, thin_input),
            "transformedText": transformed_text,
            "outline": outline,
            "checklist": checklist,
            "tableRows": table_rows,
            "sopSteps": sop_steps,
            "flashcards": flashcards,
            "jsonStyleText": json_style_text,
            "csvStyleText": csv_style_text,
            "cleanedNotes": cleaned_notes,
            "preservedItems": must_preserve,
            "avoidedItems": must_avoid,
            "missingContext": _missing_context(content, items, must_preserve, constraints, thin_input),
            "warnings": _warnings(thin_input, target_format),
            "limitations": _limitations(thin_input, target_format),
            "safety": local_transformation_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_transformation_dashboard_summary()


def local_transformation_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Transformation Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/transformation/local-transform",
        "targetFormats": list(SUPPORTED_TARGET_FORMATS),
        "detailLevels": list(SUPPORTED_DETAIL_LEVELS),
        "responseOnly": True,
        "transformationPersistence": False,
        "fileExportCreation": False,
        "documentCreation": False,
        "spreadsheetCreation": False,
        "deckCreation": False,
        "taskCreation": False,
        "sourceValidation": False,
        "citationValidation": False,
        "externalFactChecking": False,
        "documentRetrieval": False,
        "testExecution": False,
        "repoInspection": False,
        "professionalValidation": False,
        "complianceCertification": False,
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
        "limitations": ["based only on user-provided transformation inputs"],
    }


def local_transformation_safety() -> dict[str, bool]:
    return {
        "localOnly": True,
        "responseOnly": True,
        "transformationPersistence": False,
        "fileExportCreation": False,
        "documentCreation": False,
        "spreadsheetCreation": False,
        "deckCreation": False,
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
        "professionalValidation": False,
        "complianceCertification": False,
    }


def _normalize_target_format(value: str) -> str:
    normalized = (value or "outline").strip().lower()
    return normalized if normalized in SUPPORTED_TARGET_FORMATS else "outline"


def _normalize_detail_level(value: str) -> str:
    normalized = (value or "medium").strip().lower()
    return normalized if normalized in SUPPORTED_DETAIL_LEVELS else "medium"


def _detail_limit(detail_level: str) -> int:
    return {"short": 3, "medium": 5, "detailed": 8}[detail_level]


def _clean_list(values: list[str], limit: int = 10) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = re.sub(r"\s+", " ", value.strip())
        key = item.lower()
        if item and key not in seen:
            cleaned.append(item)
            seen.add(key)
    return cleaned[:limit]


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


def _source_items(items: list[str], points: list[str], must_preserve: list[str], detail_level: str) -> list[str]:
    limit = _detail_limit(detail_level)
    source: list[str] = []
    for value in [*must_preserve, *items, *points]:
        if value and value.lower() not in {item.lower() for item in source}:
            source.append(value)
        if len(source) >= max(limit, len(must_preserve[:limit])):
            break
    return source


def _transformation_focus(
    title: str,
    target_format: str,
    audience: str,
    constraints: list[str],
    thin_input: bool,
) -> str:
    subject = title or "provided inputs"
    audience_note = f" for {audience}" if audience else ""
    if thin_input:
        return f"Limited local transformation of {subject}{audience_note}; usable text or items are thin."
    if constraints:
        return f"Transform {subject}{audience_note} into {target_format} while respecting user-provided constraints."
    return f"Transform {subject}{audience_note} into {target_format} using only supplied text or items."


def _outline(items: list[str], thin_input: bool, must_avoid: list[str]) -> list[dict[str, Any]]:
    if not items:
        return [{"heading": "Limited input", "points": ["No usable content or item was provided."]}]
    if thin_input:
        return [{"heading": "Limited outline", "points": _clean_output_list(items[:2], must_avoid)}]
    return [
        {"heading": f"Section {index}", "points": [_remove_avoided_items(item, must_avoid)]}
        for index, item in enumerate(items, start=1)
    ]


def _checklist(items: list[str], thin_input: bool, must_avoid: list[str]) -> list[str]:
    if not items:
        return ["[ ] Add usable content or items before relying on this checklist."]
    prefix = "[ ] Confirm" if thin_input else "[ ]"
    return [f"{prefix} {_remove_avoided_items(item, must_avoid)}" for item in items]


def _table_rows(items: list[str], thin_input: bool, must_avoid: list[str]) -> list[dict[str, str]]:
    if not items:
        return [{"item": "No usable input", "detail": "No table file or spreadsheet was created.", "status": "limited"}]
    return [
        {
            "item": _remove_avoided_items(item, must_avoid),
            "detail": "Provisional row from user-provided input." if thin_input else "Row from user-provided input.",
            "status": "limited" if thin_input else "draft",
        }
        for item in items
    ]


def _sop_steps(items: list[str], thin_input: bool, must_avoid: list[str]) -> list[dict[str, str]]:
    if not items:
        return [{"step": "1", "action": "Add usable content or items.", "verification": "No SOP file was created."}]
    return [
        {
            "step": str(index),
            "action": _remove_avoided_items(item, must_avoid),
            "verification": "Manual review needed before use." if thin_input else "Confirm completion manually.",
        }
        for index, item in enumerate(items, start=1)
    ]


def _flashcards(items: list[str], thin_input: bool, must_avoid: list[str]) -> list[dict[str, str]]:
    if not items:
        return [{"front": "What input was provided?", "back": "No usable content or item was provided."}]
    cards = []
    for index, item in enumerate(items, start=1):
        cleaned = _remove_avoided_items(item, must_avoid)
        cards.append(
            {
                "front": f"What is point {index}?",
                "back": cleaned if not thin_input else f"Limited source point: {cleaned}",
            }
        )
    return cards


def _json_style_text(title: str, items: list[str], thin_input: bool, must_avoid: list[str]) -> str:
    if not items:
        return '{"items": [], "note": "No file was created."}'
    lines = ['{', f'  "title": "{_escape_text(_remove_avoided_items(title, must_avoid))}",', '  "items": [']
    for index, item in enumerate(items):
        suffix = "," if index < len(items) - 1 else ""
        lines.append(f'    {{"text": "{_escape_text(_remove_avoided_items(item, must_avoid))}", "status": "draft"}}{suffix}')
    lines.extend(['  ],', f'  "limited": {"true" if thin_input else "false"}', '}'])
    return "\n".join(lines)


def _csv_style_text(items: list[str], thin_input: bool, must_avoid: list[str]) -> str:
    if not items:
        return "item,status,note\nNo usable input,limited,No file was created"
    rows = ["item,status,note"]
    for item in items:
        cleaned = _escape_csv(_remove_avoided_items(item, must_avoid))
        note = "Limited source point" if thin_input else "User-provided input"
        rows.append(f"{cleaned},draft,{note}")
    return "\n".join(rows)


def _cleaned_notes(items: list[str], thin_input: bool, must_avoid: list[str]) -> str:
    if not items:
        return "No usable content or items were provided."
    prefix = "Limited cleaned notes:\n" if thin_input else "Cleaned notes:\n"
    return prefix + "\n".join(f"- {_remove_avoided_items(item, must_avoid)}" for item in items)


def _transformed_text(
    target_format: str,
    outline: list[dict[str, Any]],
    checklist: list[str],
    table_rows: list[dict[str, str]],
    sop_steps: list[dict[str, str]],
    flashcards: list[dict[str, str]],
    json_style_text: str,
    csv_style_text: str,
    cleaned_notes: str,
) -> str:
    if target_format == "checklist":
        return "\n".join(checklist)
    if target_format == "table":
        return "\n".join(f"{row['item']} | {row['detail']} | {row['status']}" for row in table_rows)
    if target_format == "sop_steps":
        return "\n".join(f"{row['step']}. {row['action']} ({row['verification']})" for row in sop_steps)
    if target_format == "flashcards":
        return "\n".join(f"Q: {card['front']}\nA: {card['back']}" for card in flashcards)
    if target_format == "json_style":
        return json_style_text
    if target_format == "csv_style":
        return csv_style_text
    if target_format == "cleaned_notes":
        return cleaned_notes
    return "\n".join(f"{row['heading']}: {', '.join(row['points'])}" for row in outline)


def _missing_context(
    content: str,
    items: list[str],
    must_preserve: list[str],
    constraints: list[str],
    thin_input: bool,
) -> list[str]:
    missing = []
    if thin_input:
        missing.append("More content or more concrete items are needed for reliable transformation.")
    if not content.strip() and not items:
        missing.append("No usable content or items were provided.")
    if not must_preserve:
        missing.append("No must-preserve items were provided.")
    if not constraints:
        missing.append("No transformation constraints were provided.")
    return missing or ["No obvious missing context was detected from the supplied transformation inputs."]


def _warnings(thin_input: bool, target_format: str) -> list[str]:
    warnings = []
    if thin_input:
        warnings.append("Transformation input is empty or thin; output is limited and provisional.")
    if target_format in {"json_style", "csv_style"}:
        warnings.append(f"{target_format} output is response text only; no file was created.")
    if target_format == "table":
        warnings.append("Table output is structured response data only; no spreadsheet was created.")
    if target_format == "flashcards":
        warnings.append("Flashcards are response data only; no deck or file was created.")
    return warnings


def _limitations(thin_input: bool, target_format: str) -> list[str]:
    limitations = [
        "Based only on user-provided transformation inputs.",
        "No source verification, citation verification, external fact checking, document retrieval, repo inspection, file reading, export creation, task creation, persistence, professional validation, compliance certification, code execution, or test execution was performed.",
        "No files, documents, spreadsheets, decks, database records, tasks, transformations, emails, posts, purchases, downloads, uploads, connectors, accounts, shell commands, or external services were used.",
    ]
    if target_format in {"json_style", "csv_style"}:
        limitations.append("JSON-style and CSV-style outputs are text in the response only; no .json, .csv, or other file was created.")
    if target_format == "table":
        limitations.append("Table rows are response data only; no spreadsheet was created.")
    if target_format == "flashcards":
        limitations.append("Flashcards are response data only; no Anki deck or file was created.")
    if thin_input:
        limitations.append("Thin input limits specificity; add content, items, constraints, or must-preserve details for stronger transformation.")
    return limitations


def _remove_avoided_items(text: str, must_avoid: list[str]) -> str:
    cleaned = text
    for item in must_avoid:
        cleaned = re.sub(re.escape(item), "[omitted]", cleaned, flags=re.IGNORECASE)
    return cleaned


def _clean_output_list(values: list[str], must_avoid: list[str]) -> list[str]:
    return [_remove_avoided_items(value, must_avoid) for value in values]


def _escape_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _escape_csv(value: str) -> str:
    if "," in value or '"' in value or "\n" in value:
        return '"' + value.replace('"', '""') + '"'
    return value
