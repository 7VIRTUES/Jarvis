from __future__ import annotations


REQUIRED_IMPLEMENTATION_REPORT_SECTIONS = [
    "Summary",
    "Files created",
    "Files changed",
    "What each file did",
    "Endpoints implemented or changed",
    "Database/schema changes",
    "Agents/tools/connectors changed",
    "Safety boundaries enforced",
    "Commands run",
    "Command results",
    "Tests added or changed",
    "Test results",
    "Blocked actions or safety decisions",
    "Known risks",
    "Whether safe to build on",
    "Recommended next task",
]


def missing_implementation_report_sections(text: str) -> list[str]:
    normalized = text.lower()
    return [section for section in REQUIRED_IMPLEMENTATION_REPORT_SECTIONS if section.lower() not in normalized]


def validate_implementation_report(text: str) -> bool:
    return not missing_implementation_report_sections(text)

