from __future__ import annotations

import re
from typing import Any
from uuid import uuid4

from .memory import MemorySecretError, MemoryValidationError, reject_secret_like_content
from .time_utils import utc_now


SUPPORTED_SUGGESTION_TYPES = frozenset(
    {"preference", "goal", "constraint", "project_fact", "decision", "agent_instruction"}
)
DEFAULT_SUGGESTION_TYPES = ("preference", "goal", "constraint")
MAX_SUGGESTION_LENGTH = 1000

_FIELD_TYPES: dict[str, str] = {
    "goal": "goal",
    "goals": "goal",
    "primaryGoal": "goal",
    "academicGoal": "goal",
    "careerGoal": "goal",
    "financialGoal": "goal",
    "learningGoal": "goal",
    "portfolioGoal": "goal",
    "housingGoal": "goal",
    "lifeQuestion": "goal",
    "relationshipGoal": "goal",
    "reflectionGoal": "goal",
    "socialGoal": "goal",
    "adminGoal": "goal",
    "gearGoal": "goal",
    "currentGoals": "goal",
    "longTermGoals": "goal",
    "constraints": "constraint",
    "mustAvoid": "constraint",
    "allergiesOrAvoidances": "constraint",
    "injuriesOrLimitations": "constraint",
    "boundaries": "constraint",
    "nonNegotiables": "constraint",
    "riskTolerance": "constraint",
    "safetyOrAccessibilityNotes": "constraint",
    "preferredActivities": "preference",
    "preferredMethods": "preference",
    "priorities": "preference",
    "tone": "preference",
    "desiredTone": "preference",
    "aestheticPreferences": "preference",
    "cuisinePreferences": "preference",
    "dietaryPreferences": "preference",
    "decisionStyle": "preference",
    "priorityPreference": "preference",
    "projectName": "project_fact",
    "programName": "project_fact",
    "schoolName": "project_fact",
    "businessName": "project_fact",
    "currentProjects": "project_fact",
    "projectNotes": "project_fact",
    "decision": "decision",
    "decisionContext": "decision",
    "mustInclude": "agent_instruction",
}
_EXCLUDED_FIELDS = frozenset(
    {"web_context", "prior_agent_context", "memory", "memoryProposalSuggestions"}
)
_SENSITIVE_MARKERS = (
    "health", "fitness", "finance", "budget", "debt", "legal", "immigration",
    "relationship", "emotional", "identity", "security", "safety", "emergency",
    "allerg", "injur",
)


class MemoryProposalSuggestionService:
    """Build ephemeral review suggestions from allowlisted explicit request fields."""

    def suggest(
        self,
        *,
        request_fields: dict[str, Any],
        response_id: str,
        agent_id: str,
        enabled: bool,
        private_session: bool,
        allowed_types: list[str] | None,
        project_name: str | None,
        max_suggestions: int,
    ) -> dict[str, Any]:
        if not enabled:
            if private_session:
                return self._result(True, True, "private_session", [], 0)
            return self._result(False, False, None, [], 0)
        types = self._allowed_types(allowed_types or [])
        if not isinstance(max_suggestions, int) or isinstance(max_suggestions, bool) or not 1 <= max_suggestions <= 3:
            raise MemoryValidationError("maximum memory suggestions must be between 1 and 3")
        if private_session:
            return self._result(True, True, "private_session", [], 0)
        project_name = self._optional_text(project_name, 200, "project name")
        if project_name is None and "projectName" in request_fields:
            project_name = self._optional_text(
                request_fields.get("projectName"), 200, "project name"
            )
        grouped: dict[str, list[tuple[str, str]]] = {}
        skipped = 0
        for field, raw_value in request_fields.items():
            if field in _EXCLUDED_FIELDS:
                continue
            memory_type = _FIELD_TYPES.get(field)
            if memory_type not in types:
                continue
            value = self._normalize_value(raw_value)
            if value is None or len(value) > MAX_SUGGESTION_LENGTH:
                skipped += 1
                continue
            try:
                reject_secret_like_content(value, label="memory suggestion")
            except MemorySecretError:
                skipped += 1
                continue
            grouped.setdefault(memory_type, []).append((field, value))

        items: list[dict[str, Any]] = []
        seen: set[str] = set()
        for memory_type in types:
            values = grouped.get(memory_type, [])
            if not values:
                continue
            content = self._candidate_content(values)
            if content is None or content.casefold() in seen:
                skipped += 1
                continue
            seen.add(content.casefold())
            evidence_fields = [field for field, _ in values]
            scope_type, scope_value = self._scope(agent_id, project_name)
            items.append(
                {
                    "suggestionId": str(uuid4()),
                    "responseId": response_id,
                    "agentId": agent_id,
                    "memoryType": memory_type,
                    "content": content,
                    "suggestedScopeType": scope_type,
                    "suggestedScopeValue": scope_value,
                    "confidence": "medium",
                    "sensitivity": self._sensitivity(agent_id, evidence_fields),
                    "sourceType": "agent_proposal",
                    "sourceAgentId": agent_id,
                    "sourceReference": f"response:{response_id}",
                    "proposalReason": (
                        "Deterministic suggestion from explicit structured request fields: "
                        + ", ".join(evidence_fields)
                        + "."
                    ),
                    "evidenceFields": evidence_fields,
                    "generatedAt": utc_now(),
                }
            )
            if len(items) >= max_suggestions:
                break
        return self._result(True, False, None, items, skipped)

    @staticmethod
    def _allowed_types(values: list[str]) -> tuple[str, ...]:
        source = values or list(DEFAULT_SUGGESTION_TYPES)
        normalized: list[str] = []
        for value in source:
            if value not in SUPPORTED_SUGGESTION_TYPES:
                raise MemoryValidationError("unsupported memory suggestion type")
            if value not in normalized:
                normalized.append(value)
        return tuple(normalized)

    @staticmethod
    def _normalize_value(value: Any) -> str | None:
        if isinstance(value, str):
            normalized = re.sub(r"\s+", " ", value).strip()
        elif isinstance(value, list):
            parts = [
                re.sub(r"\s+", " ", str(item)).strip()
                for item in value
                if isinstance(item, (str, int, float)) and not isinstance(item, bool)
            ]
            normalized = "; ".join(part for part in parts if part)
        else:
            return None
        return normalized if len(normalized) >= 3 else None

    @staticmethod
    def _candidate_content(values: list[tuple[str, str]]) -> str | None:
        unique: list[str] = []
        seen: set[str] = set()
        for _, value in values:
            if value.casefold() not in seen:
                seen.add(value.casefold())
                unique.append(value)
        content = "; ".join(unique)
        return content if content and len(content) <= MAX_SUGGESTION_LENGTH else None

    @staticmethod
    def _scope(agent_id: str, project_name: str | None) -> tuple[str, str]:
        return ("project", project_name) if project_name else ("agent", agent_id)

    @staticmethod
    def _sensitivity(agent_id: str, evidence_fields: list[str]) -> str:
        material = " ".join([agent_id, *evidence_fields]).casefold()
        return "sensitive" if any(marker in material for marker in _SENSITIVE_MARKERS) else "standard"

    @staticmethod
    def _optional_text(value: Any, maximum: int, label: str) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise MemoryValidationError(f"{label} must be text")
        normalized = re.sub(r"\s+", " ", value).strip()
        if not normalized:
            return None
        if len(normalized) > maximum:
            raise MemoryValidationError(f"{label} exceeds the maximum length")
        return normalized

    @staticmethod
    def _result(
        requested: bool,
        blocked: bool,
        block_reason: str | None,
        items: list[dict[str, Any]],
        skipped: int,
    ) -> dict[str, Any]:
        limitations = [
            "Suggestions are generated deterministically from explicit structured request fields.",
            "A suggestion is not an active memory and was not persisted.",
            "Every suggestion requires user review; submission creates only a pending proposal.",
            "Pending proposals require separate approval.",
            "This does not represent model training.",
            "A suggestion may be too task-specific for durable memory.",
        ]
        if blocked:
            limitations.append("Private session blocked suggestion generation and persistence.")
        return {
            "requested": requested,
            "blocked": blocked,
            "blockReason": block_reason,
            "generatedDeterministically": requested and not blocked,
            "persisted": False,
            "count": len(items),
            "items": items,
            "skippedCount": skipped,
            "limitations": limitations,
        }
