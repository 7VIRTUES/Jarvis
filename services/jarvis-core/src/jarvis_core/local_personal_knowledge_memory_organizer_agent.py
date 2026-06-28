from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_personal_knowledge_memory_organizer"
STATUS = "local_only"
MODE = "response_only_user_provided_personal_knowledge_memory_organization"
SUPPORTED_OUTPUT_TYPES = (
    "knowledge_map",
    "note_structure",
    "memory_index",
    "tagging_plan",
    "review_plan",
    "decision_record",
    "project_context_summary",
    "personal_wiki_outline",
    "learning_log_structure",
    "retrieval_checklist",
    "comparison",
    "checklist",
    "summary",
)


@dataclass(frozen=True)
class LocalPersonalKnowledgeMemoryOrganizerRequest:
    request: str = ""
    prompt_text: str = ""
    output_type: str = "summary"
    knowledge_area: str = ""
    source_notes_or_summary: str = ""
    organization_goal: str = ""
    categories_or_tags: list[str] = field(default_factory=list)
    projects_or_life_areas: list[str] = field(default_factory=list)
    review_frequency: str = ""
    priority_level: str = ""
    retention_goal: str = ""
    decision_or_memory_context: str = ""
    constraints_or_notes: str = ""


class LocalPersonalKnowledgeMemoryOrganizerAgentService:
    def create_plan(self, request: LocalPersonalKnowledgeMemoryOrganizerRequest) -> dict[str, Any]:
        request_text = _clean_text(request.request or request.prompt_text)
        output_type = _normalize_output_type(request.output_type)
        area = _clean_text(request.knowledge_area) or request_text or "personal knowledge area"
        notes = _clean_text(request.source_notes_or_summary)
        goal = _clean_text(request.organization_goal)
        categories_or_tags = _clean_list(request.categories_or_tags)
        projects = _clean_list(request.projects_or_life_areas)
        review_frequency = _clean_text(request.review_frequency)
        priority = _clean_text(request.priority_level)
        retention_goal = _clean_text(request.retention_goal)
        context = _clean_text(request.decision_or_memory_context)
        constraints = _clean_text(request.constraints_or_notes)
        combined = " ".join([request_text, area, notes, goal, " ".join(categories_or_tags), " ".join(projects), context, constraints])
        sensitive_context = _has_sensitive_context(combined)
        thin_input = not any([request_text, notes, goal, categories_or_tags, projects, review_frequency, priority, retention_goal, context, constraints])

        return {
            "agent_id": AGENT_ID,
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "title": _title(output_type, area),
            "summary": _summary(output_type, area, goal, thin_input),
            "assumptions": _assumptions(area, notes, projects, thin_input),
            "recommended_structure": _recommended_structure(output_type, area, notes, goal, projects),
            "categories": _categories(output_type, categories_or_tags, projects, area),
            "tags": _tags(output_type, categories_or_tags, priority, retention_goal),
            "key_points": _key_points(notes, context, sensitive_context),
            "review_plan": _review_plan(output_type, review_frequency, priority, retention_goal),
            "retrieval_prompts": _retrieval_prompts(output_type, area, projects, context),
            "checklist": _checklist(output_type, area, sensitive_context),
            "limitations": _limitations(thin_input, sensitive_context),
            "follow_up_questions": _follow_up_questions(notes, goal, categories_or_tags, projects, review_frequency, priority, retention_goal, context),
            "output_type": output_type,
            "safety": local_personal_knowledge_memory_organizer_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_personal_knowledge_memory_organizer_dashboard_summary()


def local_personal_knowledge_memory_organizer_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Personal Knowledge / Memory Organizer Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/personal-knowledge-memory-organizer/local-plan",
        "outputTypes": list(SUPPORTED_OUTPUT_TYPES),
        "responseOnly": True,
        "manualInputOnly": True,
        "localOnly": True,
        "externalServices": False,
        "connectors": False,
        "oauth": False,
        "accountAccess": False,
        "fileReads": False,
        "fileWrites": False,
        "notesAppAccess": False,
        "cloudDriveAccess": False,
        "browserHistoryAccess": False,
        "emailAccess": False,
        "calendarAccess": False,
        "contactAccess": False,
        "memoryStoreAccess": False,
        "databaseAccess": False,
        "paymentAccess": False,
        "webBrowsing": False,
        "paidApis": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "recordCreation": False,
        "recordEditing": False,
        "recordDeletion": False,
        "fileMovement": False,
        "sync": False,
        "export": False,
        "secretStorage": False,
        "sensitiveFactInference": False,
        "mutation": False,
        "certificationClaims": False,
        "limitations": ["personal knowledge, note, memory-index, review, and retrieval planning only from user-provided text"],
    }


def local_personal_knowledge_memory_organizer_safety() -> dict[str, bool]:
    return {key: value for key, value in local_personal_knowledge_memory_organizer_dashboard_summary().items() if isinstance(value, bool)}


def _normalize_output_type(value: str) -> str:
    normalized = (value or "summary").strip().lower()
    return normalized if normalized in SUPPORTED_OUTPUT_TYPES else "summary"


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def _clean_list(values: list[str], limit: int = 16) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = _clean_text(value)
        key = item.lower()
        if item and key not in seen:
            cleaned.append(item)
            seen.add(key)
    return cleaned[:limit]


def _has_sensitive_context(text: str) -> bool:
    lowered = text.lower()
    terms = (
        "password",
        "secret",
        "api key",
        "token",
        "social security",
        "ssn",
        "passport",
        "bank account",
        "credit card",
        "medical record",
        "diagnosis",
        "legal case",
        "protected personal",
    )
    return any(term in lowered for term in terms)


def _title(output_type: str, area: str) -> str:
    return f"{output_type.replace('_', ' ').title()}: {area[:80]}"


def _summary(output_type: str, area: str, goal: str, thin_input: bool) -> str:
    if thin_input:
        return "Local manual personal-knowledge scaffold; add notes, categories, projects, review frequency, and retention goal for a more specific structure."
    goal_text = f" Goal: {goal}." if goal else ""
    return f"Manual {output_type.replace('_', ' ')} for {area}.{goal_text} No files, notes apps, cloud drives, browser history, email, calendar, contacts, memory stores, databases, accounts, payments, or external services were accessed."


def _assumptions(area: str, notes: str, projects: list[str], thin_input: bool) -> list[str]:
    assumptions = [f"Uses only user-provided knowledge and memory-organization notes for: {area}."]
    if notes:
        assumptions.append("Source notes were supplied directly in the request and were not searched in files or apps.")
    if projects:
        assumptions.append(f"Project or life areas supplied by user: {', '.join(projects[:8])}.")
    if thin_input:
        assumptions.append("Input is thin; no file search, external memory, notes app, email, calendar, contacts, or database lookup was performed.")
    return assumptions


def _recommended_structure(output_type: str, area: str, notes: str, goal: str, projects: list[str]) -> list[str]:
    structure = [f"Create a manual top-level section for {area}.", "Use short entries with source note, context, category, retrieval cue, and review date fields."]
    if output_type == "decision_record":
        structure.append("Use decision, context, options, reasons, tradeoffs, owner, and revisit trigger fields.")
    elif output_type == "personal_wiki_outline":
        structure.append("Use overview, active projects, reference notes, decisions, glossary, and review queue sections.")
    elif output_type == "learning_log_structure":
        structure.append("Use lesson, evidence, example, practice task, uncertainty, and next review fields.")
    elif output_type == "memory_index":
        structure.append("Index memories by topic, date/context supplied by user, importance, and retrieval prompt.")
    if goal:
        structure.append(f"Organization goal: {goal}.")
    if projects:
        structure.append(f"Link entries manually to project or life areas: {', '.join(projects[:8])}.")
    if notes:
        structure.append("Extract only from the provided notes; do not infer facts outside them.")
    return structure


def _categories(output_type: str, categories_or_tags: list[str], projects: list[str], area: str) -> list[str]:
    categories = categories_or_tags[:8] if categories_or_tags else [area, "active", "reference", "decision", "review"]
    if projects:
        categories.extend([f"area:{project}" for project in projects[:4]])
    if output_type == "review_plan":
        categories.append("review_queue")
    return categories[:12]


def _tags(output_type: str, categories_or_tags: list[str], priority: str, retention_goal: str) -> list[str]:
    tags = [f"tag:{tag.lower().replace(' ', '-')}" for tag in categories_or_tags[:8]]
    if priority:
        tags.append(f"priority:{priority.lower().replace(' ', '-')}")
    if retention_goal:
        tags.append(f"retention:{retention_goal.lower().replace(' ', '-')}")
    if output_type:
        tags.append(f"format:{output_type}")
    return tags[:12]


def _key_points(notes: str, context: str, sensitive_context: bool) -> list[str]:
    points: list[str] = []
    if notes:
        sentences = [part.strip(" .") for part in re.split(r"[.!?]\s+", notes) if part.strip()]
        points.extend(sentences[:5])
    if context:
        points.append(f"Decision or memory context: {context}.")
    if sensitive_context:
        points.append("Sensitive-looking content was present; redact secrets, credentials, private IDs, medical/legal/financial account details, and protected personal data before storing anywhere.")
    if not points:
        points.append("Add source notes or a summary to extract concrete key points.")
    return points[:6]


def _review_plan(output_type: str, review_frequency: str, priority: str, retention_goal: str) -> list[str]:
    plan = ["Review manually; this response does not create reminders, files, database records, or memory entries."]
    if review_frequency:
        plan.append(f"Review frequency supplied by user: {review_frequency}.")
    else:
        plan.append("Default scaffold: quick weekly review for active notes and slower monthly review for reference notes.")
    if priority:
        plan.append(f"Priority level: {priority}.")
    if retention_goal:
        plan.append(f"Retention goal: {retention_goal}.")
    if output_type == "review_plan":
        plan.append("Use a small queue: review, keep, archive manually, or rewrite manually.")
    return plan


def _retrieval_prompts(output_type: str, area: str, projects: list[str], context: str) -> list[str]:
    prompts = [f"What did I decide or learn about {area}?", "What is the current next action or review question?", "What evidence did the provided notes actually contain?"]
    if projects:
        prompts.append(f"Which project or life area does this help: {', '.join(projects[:5])}?")
    if context:
        prompts.append(f"When this context appears again, what should I remember: {context}?")
    if output_type == "retrieval_checklist":
        prompts.append("Which tags, categories, and review date would help find this manually later?")
    return prompts[:6]


def _checklist(output_type: str, area: str, sensitive_context: bool) -> list[str]:
    checklist = [
        f"Name the knowledge area: {area}.",
        "Separate facts from interpretations.",
        "Choose categories and tags manually.",
        "Add review cadence manually.",
        "Keep retrieval prompts short and searchable by memory.",
    ]
    if sensitive_context:
        checklist.insert(0, "Redact sensitive details before placing notes into any storage location.")
    if output_type == "checklist":
        checklist.append("Do not create, edit, delete, move, sync, export, or persist any file or record from this response.")
    return checklist


def _limitations(thin_input: bool, sensitive_context: bool) -> list[str]:
    limitations = [
        "Based only on user-provided text.",
        "No files, notes apps, cloud drives, browser history, email, calendar, contacts, memory stores, databases, accounts, payments, or external services were accessed.",
        "No create, edit, delete, move, persist, sync, export, or mutate behavior is provided.",
        "No claim is made to search files or memory outside the provided input, and sensitive facts are not inferred beyond the text.",
    ]
    if sensitive_context:
        limitations.append("Sensitive-looking content should be redacted and stored only in a safer local system chosen by the user.")
    if thin_input:
        limitations.append("Input is thin, so guidance remains a general local scaffold.")
    return limitations


def _follow_up_questions(notes: str, goal: str, categories_or_tags: list[str], projects: list[str], review_frequency: str, priority: str, retention_goal: str, context: str) -> list[str]:
    questions: list[str] = []
    if not notes:
        questions.append("What source notes or summary should be organized?")
    if not goal:
        questions.append("What organization goal should the structure support?")
    if not categories_or_tags:
        questions.append("Which categories or tags already make sense?")
    if not projects:
        questions.append("Which projects or life areas should this connect to?")
    if not review_frequency:
        questions.append("How often should this be reviewed manually?")
    if not priority:
        questions.append("What priority level should be attached?")
    if not retention_goal:
        questions.append("What should be remembered long term?")
    if not context:
        questions.append("What decision or memory context should future-you recognize?")
    return questions[:6]
