from __future__ import annotations


REQUIRED_IMPLEMENTATION_REPORT_SECTIONS = [
    "Summary",
    "Files created",
    "Files changed",
    "What each file change did",
    "Endpoints changed",
    "Database/schema changes",
    "Agents/tools/connectors changed",
    "Safety boundaries enforced",
    "Commands run",
    "Command results",
    "Tests added/changed",
    "Test results",
    "Post-Codex review findings",
    "Safe check results",
    "Repair attempts/results",
    "Blocked actions/safety decisions",
    "Known risks",
    "Whether safe to build on",
    "Recommended next task",
]


REQUIRED_IMPLEMENTATION_REPORT_FORMAT = "; ".join(REQUIRED_IMPLEMENTATION_REPORT_SECTIONS) + "."


def missing_implementation_report_sections(text: str) -> list[str]:
    normalized = text.lower()
    return [section for section in REQUIRED_IMPLEMENTATION_REPORT_SECTIONS if section.lower() not in normalized]


def validate_implementation_report(text: str) -> bool:
    return not missing_implementation_report_sections(text)
