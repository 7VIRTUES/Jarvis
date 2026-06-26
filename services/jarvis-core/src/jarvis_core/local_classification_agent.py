from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_classification_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_classification"
SUPPORTED_CLASSIFICATION_TYPES = ("general", "priority", "risk", "effort", "topic", "routing", "safety")
SUPPORTED_DETAIL_LEVELS = ("short", "medium", "detailed")


@dataclass(frozen=True)
class LocalClassificationRequest:
    title: str = ""
    content: str = ""
    items: list[str] = field(default_factory=list)
    classification_type: str = "general"
    labels: list[str] = field(default_factory=list)
    criteria: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    detail_level: str = "medium"


class LocalClassificationAgentService:
    def classify(self, request: LocalClassificationRequest) -> dict[str, Any]:
        title = request.title.strip()
        content = request.content.strip()
        classification_type = _normalize_classification_type(request.classification_type)
        detail_level = _normalize_detail_level(request.detail_level)
        labels = _clean_list(request.labels)
        criteria = _clean_list(request.criteria)
        constraints = _clean_list(request.constraints)
        content_points = _extract_points(content)
        items = _clean_list(request.items, limit=16)
        usable_items = items or content_points
        thin_input = not usable_items or (not items and len(content) < 80 and len(content_points) < 2)
        limit = _detail_limit(detail_level)

        classified_items = _classified_items(usable_items, labels, criteria, classification_type, thin_input, limit)
        priority_bands = _priority_bands(usable_items, classification_type, thin_input, limit)
        risk_bands = _risk_bands(usable_items, classification_type, constraints, thin_input, limit)
        effort_bands = _effort_bands(usable_items, classification_type, thin_input, limit)
        routing_hints = _routing_hints(usable_items, classification_type, labels, thin_input, limit)
        safety_notes = _safety_notes(usable_items, classification_type, constraints, thin_input, limit)

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "title": title,
            "classificationType": classification_type,
            "detailLevel": detail_level,
            "classificationFocus": _classification_focus(title, classification_type, labels, criteria, thin_input),
            "classifiedItems": classified_items,
            "labelsUsed": _labels_used(labels, classification_type),
            "priorityBands": priority_bands,
            "riskBands": risk_bands,
            "effortBands": effort_bands,
            "routingHints": routing_hints,
            "safetyNotes": safety_notes,
            "assumptions": _assumptions(labels, criteria, constraints, items, content_points, thin_input),
            "missingContext": _missing_context(content, items, labels, criteria, constraints, thin_input),
            "warnings": _warnings(thin_input, classification_type),
            "limitations": _limitations(thin_input, classification_type),
            "safety": local_classification_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_classification_dashboard_summary()


def local_classification_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Classification Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/classification/local-classify",
        "classificationTypes": list(SUPPORTED_CLASSIFICATION_TYPES),
        "detailLevels": list(SUPPORTED_DETAIL_LEVELS),
        "responseOnly": True,
        "classificationPersistence": False,
        "taskCreation": False,
        "agentCalls": False,
        "professionalValidation": False,
        "complianceCertification": False,
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
        "limitations": ["based only on user-provided classification inputs"],
    }


def local_classification_safety() -> dict[str, bool]:
    return {
        "localOnly": True,
        "responseOnly": True,
        "classificationPersistence": False,
        "taskCreation": False,
        "agentCalls": False,
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


def _normalize_classification_type(value: str) -> str:
    normalized = (value or "general").strip().lower()
    return normalized if normalized in SUPPORTED_CLASSIFICATION_TYPES else "general"


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


def _classification_focus(
    title: str,
    classification_type: str,
    labels: list[str],
    criteria: list[str],
    thin_input: bool,
) -> str:
    subject = title or "provided inputs"
    if thin_input:
        return f"Limited local classification for {subject}; usable text or items are thin."
    if labels:
        return f"Classify {subject} using user-provided candidate labels only."
    if criteria:
        return f"Classify {subject} for {classification_type} using user-provided criteria."
    return f"Classify {subject} for {classification_type} using only supplied text or items."


def _classified_items(
    items: list[str],
    labels: list[str],
    criteria: list[str],
    classification_type: str,
    thin_input: bool,
    limit: int,
) -> list[dict[str, Any]]:
    if not items:
        return [
            {
                "item": "No usable content or item was provided.",
                "label": "unclassified",
                "confidence": "low",
                "basis": "limited_input",
                "notes": ["Add content or items before relying on classification."],
            }
        ]
    classified = []
    for item in items[:limit]:
        label = _choose_label(item, labels, classification_type)
        notes = ["Label is based only on user-provided text and candidate labels."]
        if criteria:
            notes.append(f"Review against criterion: {criteria[0]}.")
        if thin_input:
            notes.append("Thin input makes this classification provisional.")
        classified.append(
            {
                "item": item,
                "label": label,
                "confidence": "low" if thin_input else "medium",
                "basis": "user_provided_input",
                "notes": notes,
            }
        )
    return classified


def _choose_label(item: str, labels: list[str], classification_type: str) -> str:
    if labels:
        lowered = item.lower()
        for label in labels:
            if label.lower() in lowered:
                return label
        return labels[0]
    if classification_type == "priority":
        return _priority_label(item)
    if classification_type == "risk":
        return _risk_label(item)
    if classification_type == "effort":
        return _effort_label(item)
    if classification_type == "routing":
        return "local_advisory_route"
    if classification_type == "safety":
        return "needs_manual_safety_review"
    if classification_type == "topic":
        return _topic_label(item)
    return "general"


def _labels_used(labels: list[str], classification_type: str) -> list[dict[str, str]]:
    if labels:
        return [{"label": label, "source": "user_provided_candidate_label"} for label in labels]
    defaults = {
        "priority": ["high", "medium", "low"],
        "risk": ["high_risk", "medium_risk", "low_risk"],
        "effort": ["high_effort", "medium_effort", "low_effort"],
        "routing": ["documentation", "review", "planning", "support"],
        "safety": ["needs_manual_safety_review", "normal_local_review"],
        "topic": ["topic_candidate"],
        "general": ["general"],
    }
    return [{"label": label, "source": "local_default_label"} for label in defaults[classification_type]]


def _priority_bands(items: list[str], classification_type: str, thin_input: bool, limit: int) -> dict[str, list[str]]:
    if not items:
        return {"high": [], "medium": [], "low": []}
    bands = {"high": [], "medium": [], "low": []}
    for item in items[:limit]:
        bands[_priority_label(item)].append(item)
    if classification_type != "priority" and thin_input:
        bands["medium"].append("Priority bands are provisional because input is thin.")
    return bands


def _risk_bands(items: list[str], classification_type: str, constraints: list[str], thin_input: bool, limit: int) -> dict[str, list[str]]:
    if not items:
        return {"high": [], "medium": [], "low": []}
    bands = {"high": [], "medium": [], "low": []}
    for item in items[:limit]:
        bands[_risk_label(item).replace("_risk", "")].append(item)
    if constraints:
        bands["medium"].append(f"Check against user-provided constraint: {constraints[0]}.")
    if classification_type != "risk" and thin_input:
        bands["medium"].append("Risk bands are provisional because input is thin.")
    return bands


def _effort_bands(items: list[str], classification_type: str, thin_input: bool, limit: int) -> dict[str, list[str]]:
    if not items:
        return {"high": [], "medium": [], "low": []}
    bands = {"high": [], "medium": [], "low": []}
    for item in items[:limit]:
        bands[_effort_label(item).replace("_effort", "")].append(item)
    if classification_type != "effort" and thin_input:
        bands["medium"].append("Effort bands are provisional because input is thin.")
    return bands


def _routing_hints(items: list[str], classification_type: str, labels: list[str], thin_input: bool, limit: int) -> list[dict[str, str]]:
    if not items:
        return [{"item": "No usable input.", "route": "unrouted", "note": "No task, agent call, or workflow mutation was created."}]
    hints = []
    for item in items[:limit]:
        route = _route_label(item, labels)
        note = "Advisory local routing hint only; no task, agent call, or workflow mutation was created."
        if thin_input:
            note = f"{note} Input is thin."
        hints.append({"item": item, "route": route, "note": note})
    if classification_type != "routing":
        return hints[: min(3, len(hints))]
    return hints


def _safety_notes(items: list[str], classification_type: str, constraints: list[str], thin_input: bool, limit: int) -> list[str]:
    notes = [
        "Local safety notes are conservative and this response does not certify compliance, security, legal, medical, or financial validity."
    ]
    if not items:
        notes.append("No usable input was provided for safety classification.")
        return notes
    safety_terms = ("secret", "credential", "token", "password", "legal", "medical", "financial", "security", "delete", "destructive")
    for item in items[:limit]:
        if _contains_any(item.lower(), safety_terms):
            notes.append(f"Review manually before acting: {item}")
    if constraints:
        notes.append(f"Respect user-provided constraint: {constraints[0]}.")
    if thin_input:
        notes.append("Thin input may hide important safety context.")
    if classification_type == "safety" and len(notes) == 1:
        notes.append("No explicit safety flag was detected from the supplied input; manual review is still required.")
    return notes[: limit + 2]


def _assumptions(
    labels: list[str],
    criteria: list[str],
    constraints: list[str],
    items: list[str],
    content_points: list[str],
    thin_input: bool,
) -> list[str]:
    assumptions = ["Classification uses only user-provided text, items, labels, criteria, and constraints."]
    if labels:
        assumptions.append("Labels are treated as user-provided candidate labels only, not a trained taxonomy or externally validated labels.")
    if criteria:
        assumptions.append("Criteria are treated as user-provided classification guidance.")
    if constraints:
        assumptions.append("Constraints are treated as local advisory boundaries.")
    if items:
        assumptions.append("Items are treated as the primary units to classify.")
    elif content_points:
        assumptions.append("Content was split into local text points for provisional classification.")
    if thin_input:
        assumptions.append("The output is limited because usable input is thin.")
    return assumptions[:7]


def _missing_context(
    content: str,
    items: list[str],
    labels: list[str],
    criteria: list[str],
    constraints: list[str],
    thin_input: bool,
) -> list[str]:
    missing = []
    if thin_input:
        missing.append("More content or more concrete items are needed for reliable classification.")
    if not content.strip() and not items:
        missing.append("No usable content or items were provided.")
    if not labels:
        missing.append("No user-provided candidate labels were provided.")
    if not criteria:
        missing.append("No classification criteria were provided.")
    if not constraints:
        missing.append("No classification constraints were provided.")
    return missing or ["No obvious missing context was detected from the supplied classification inputs."]


def _warnings(thin_input: bool, classification_type: str) -> list[str]:
    warnings = []
    if thin_input:
        warnings.append("Classification input is empty or thin; output is limited and provisional.")
    if classification_type == "routing":
        warnings.append("Routing output is advisory only; no task, agent call, or workflow mutation was created.")
    if classification_type == "safety":
        warnings.append("Safety output is conservative local guidance only, not professional validation or compliance certification.")
    return warnings


def _limitations(thin_input: bool, classification_type: str) -> list[str]:
    limitations = [
        "Based only on user-provided classification inputs.",
        "No source verification, citation verification, external fact checking, document retrieval, repo inspection, file reading, task creation, persistence, professional validation, compliance certification, code execution, or test execution was performed.",
        "No files, database records, tasks, classifications, emails, posts, purchases, downloads, uploads, connectors, accounts, shell commands, or external services were used.",
    ]
    if classification_type == "routing":
        limitations.append("Routing hints are local response text only; no tasks, agent calls, routing records, or workflow changes were created.")
    if classification_type == "safety":
        limitations.append("Safety notes are not formal security, compliance, legal, medical, financial, or professional validation.")
    if thin_input:
        limitations.append("Thin input limits specificity; add content, items, labels, criteria, or constraints for stronger classification.")
    return limitations


def _priority_label(item: str) -> str:
    lowered = item.lower()
    if _contains_any(lowered, ("urgent", "critical", "blocker", "asap", "high", "deadline")):
        return "high"
    if _contains_any(lowered, ("later", "optional", "low", "nice to have", "someday")):
        return "low"
    return "medium"


def _risk_label(item: str) -> str:
    lowered = item.lower()
    if _contains_any(lowered, ("critical", "security", "secret", "credential", "destructive", "data loss", "legal", "medical")):
        return "high_risk"
    if _contains_any(lowered, ("risk", "unknown", "unclear", "concern", "warning", "blocker")):
        return "medium_risk"
    return "low_risk"


def _effort_label(item: str) -> str:
    lowered = item.lower()
    if _contains_any(lowered, ("large", "complex", "migration", "rewrite", "multi-step", "many", "detailed")):
        return "high_effort"
    if _contains_any(lowered, ("small", "quick", "simple", "minor", "one-line", "tiny")):
        return "low_effort"
    return "medium_effort"


def _topic_label(item: str) -> str:
    lowered = item.lower()
    if _contains_any(lowered, ("doc", "readme", "guide")):
        return "documentation"
    if _contains_any(lowered, ("test", "pytest", "validation")):
        return "validation"
    if _contains_any(lowered, ("dashboard", "ui", "status")):
        return "dashboard"
    if _contains_any(lowered, ("risk", "safety", "security")):
        return "safety"
    return "topic_candidate"


def _route_label(item: str, labels: list[str]) -> str:
    if labels:
        return labels[0]
    topic = _topic_label(item)
    if topic == "documentation":
        return "docs_review"
    if topic == "validation":
        return "manual_validation_review"
    if topic == "dashboard":
        return "dashboard_review"
    if topic == "safety":
        return "safety_review"
    return "local_review"


def _contains_any(value: str, terms: tuple[str, ...]) -> bool:
    return any(term in value for term in terms)
