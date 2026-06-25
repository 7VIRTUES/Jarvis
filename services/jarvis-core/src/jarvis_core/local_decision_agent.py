from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_decision_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_decision_support"
SUPPORTED_DECISION_STYLES = ("balanced", "safest", "fastest", "cheapest", "highest_upside")


@dataclass(frozen=True)
class LocalDecisionRequest:
    decision: str
    options: list[str]
    criteria: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    priorities: list[str] = field(default_factory=list)
    context_notes: str = ""
    decision_style: str = "balanced"


class LocalDecisionAgentService:
    def compare_options(self, request: LocalDecisionRequest) -> dict[str, Any]:
        decision = request.decision.strip() or "Untitled local decision"
        options = _clean_list(request.options, limit=12)
        criteria = _clean_list(request.criteria)
        constraints = _clean_list(request.constraints)
        priorities = _clean_list(request.priorities)
        context_notes = request.context_notes.strip()
        context_points = _extract_points(context_notes)
        decision_style = _normalize_decision_style(request.decision_style)
        thin_context = not criteria and not constraints and not priorities and len(context_notes) < 40
        limited_options = len(options) < 2
        high_stakes = _looks_high_stakes(decision, options, criteria, constraints, priorities, context_notes)

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "decision": decision,
            "decisionStyle": decision_style,
            "optionsConsidered": options,
            "decisionFocus": _decision_focus(decision, decision_style, criteria, priorities, thin_context, limited_options),
            "comparisonMatrix": _comparison_matrix(options, criteria, constraints, priorities, decision_style, limited_options),
            "tradeoffs": _tradeoffs(options, criteria, constraints, priorities, decision_style, limited_options),
            "suggestedDirection": _suggested_direction(options, decision_style, thin_context, limited_options),
            "confidence": _confidence(thin_context, limited_options, criteria, priorities),
            "assumptions": _assumptions(criteria, constraints, priorities, context_points, thin_context, limited_options),
            "risks": _risks(constraints, thin_context, limited_options, high_stakes),
            "missingInformation": _missing_information(criteria, constraints, priorities, context_points, limited_options),
            "nextActions": _next_actions(thin_context, limited_options, high_stakes),
            "reviewQuestions": _review_questions(decision_style, thin_context, limited_options),
            "warnings": _warnings(thin_context, limited_options, high_stakes),
            "limitations": _limitations(thin_context, limited_options, high_stakes),
            "safety": local_decision_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_decision_dashboard_summary()


def local_decision_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Decision Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/decision/local-decision",
        "decisionStyles": list(SUPPORTED_DECISION_STYLES),
        "responseOnly": True,
        "decisionPersistence": False,
        "professionalAdvice": False,
        "externalVerification": False,
        "sourceValidation": False,
        "citationValidation": False,
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
        "uploads": False,
        "mutation": False,
        "limitations": ["based only on user-provided decision inputs"],
    }


def local_decision_safety() -> dict[str, bool]:
    return {
        "localOnly": True,
        "responseOnly": True,
        "decisionPersistence": False,
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
        "uploads": False,
        "mutation": False,
        "repoInspection": False,
        "testExecution": False,
        "sourceValidation": False,
        "citationValidation": False,
        "externalVerification": False,
        "professionalAdvice": False,
    }


def _normalize_decision_style(value: str) -> str:
    normalized = (value or "balanced").strip().lower()
    return normalized if normalized in SUPPORTED_DECISION_STYLES else "balanced"


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


def _extract_points(notes: str) -> list[str]:
    if not notes.strip():
        return []
    raw_parts = re.split(r"(?:\r?\n+|(?<=[.!?])\s+|[;:•]+)", notes)
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


def _decision_focus(
    decision: str,
    decision_style: str,
    criteria: list[str],
    priorities: list[str],
    thin_context: bool,
    limited_options: bool,
) -> str:
    if limited_options:
        return f"Clarify at least two usable options before treating this as a comparison for {decision}."
    if thin_context:
        return f"Create a provisional comparison for {decision}; criteria, constraints, and priorities are thin."
    if decision_style == "safest":
        return f"Compare options for {decision} with emphasis on avoiding downside and constraint conflicts."
    if decision_style == "fastest":
        return f"Compare options for {decision} with emphasis on speed and immediate next steps."
    if decision_style == "cheapest":
        return f"Compare options for {decision} with emphasis on minimizing cost, waste, and resource burden."
    if decision_style == "highest_upside":
        return f"Compare options for {decision} with emphasis on the strongest potential upside."
    if priorities:
        return f"Compare options for {decision} against user-provided priorities, starting with {priorities[0]}."
    if criteria:
        return f"Compare options for {decision} against user-provided criteria, starting with {criteria[0]}."
    return f"Compare options for {decision} using only the supplied decision inputs."


def _comparison_matrix(
    options: list[str],
    criteria: list[str],
    constraints: list[str],
    priorities: list[str],
    decision_style: str,
    limited_options: bool,
) -> list[dict[str, Any]]:
    if not options:
        return [
            {
                "option": "No usable option provided.",
                "fit": "not_comparable",
                "criteriaNotes": ["Add at least two concrete options."],
                "constraintNotes": constraints or ["No constraints were provided."],
                "priorityNotes": priorities or ["No priorities were provided."],
                "styleNote": "No decision direction can be inferred without options.",
            }
        ]

    matrix = []
    for index, option in enumerate(options):
        matrix.append(
            {
                "option": option,
                "fit": _fit_label(index, limited_options),
                "criteriaNotes": _criteria_notes(option, criteria, limited_options),
                "constraintNotes": _constraint_notes(constraints, limited_options),
                "priorityNotes": _priority_notes(priorities, decision_style, limited_options),
                "styleNote": _style_note(option, decision_style, limited_options),
            }
        )
    return matrix


def _fit_label(index: int, limited_options: bool) -> str:
    if limited_options:
        return "not_comparable"
    labels = ("strong_initial_candidate", "comparison_candidate", "secondary_candidate")
    return labels[min(index, len(labels) - 1)]


def _criteria_notes(option: str, criteria: list[str], limited_options: bool) -> list[str]:
    if limited_options:
        return [f"{option} cannot be compared honestly until another usable option is provided."]
    if not criteria:
        return ["No explicit criteria were provided, so fit is provisional."]
    return [f"Check {option} against criterion: {criterion}." for criterion in criteria[:4]]


def _constraint_notes(constraints: list[str], limited_options: bool) -> list[str]:
    if limited_options:
        return ["Constraint fit cannot be ranked with fewer than two usable options."]
    if not constraints:
        return ["No constraints were provided."]
    return [f"Confirm compatibility with constraint: {constraint}." for constraint in constraints[:4]]


def _priority_notes(priorities: list[str], decision_style: str, limited_options: bool) -> list[str]:
    if limited_options:
        return ["Priority tradeoffs cannot be ranked with fewer than two usable options."]
    if priorities:
        return [f"Compare against priority: {priority}." for priority in priorities[:4]]
    return [f"No explicit priorities were provided; using the {decision_style} style as the main lens."]


def _style_note(option: str, decision_style: str, limited_options: bool) -> str:
    if limited_options:
        return f"{option} is described, but this is not a real comparison yet."
    if decision_style == "safest":
        return "Prefer this option only if its downsides and constraint conflicts are acceptable."
    if decision_style == "fastest":
        return "Prefer this option if speed matters more than completeness or upside."
    if decision_style == "cheapest":
        return "Prefer this option if lower cost and lower resource burden matter most."
    if decision_style == "highest_upside":
        return "Prefer this option if the best-case payoff is worth the uncertainty."
    return "Prefer this option if it balances the stated criteria, constraints, and priorities better than the alternatives."


def _tradeoffs(
    options: list[str],
    criteria: list[str],
    constraints: list[str],
    priorities: list[str],
    decision_style: str,
    limited_options: bool,
) -> list[str]:
    if limited_options:
        return ["Fewer than two usable options were provided, so tradeoffs are limited to clarifying the missing alternative."]
    tradeoffs = []
    if criteria:
        tradeoffs.append("A criteria-led choice may favor explicit fit over speed or upside.")
    if constraints:
        tradeoffs.append("A constraint-led choice may reduce risk while narrowing what can be selected.")
    if priorities:
        tradeoffs.append("A priority-led choice may sacrifice lower-priority benefits for the stated top concerns.")
    if decision_style == "safest":
        tradeoffs.append("Safest may reduce downside while missing a larger opportunity.")
    elif decision_style == "fastest":
        tradeoffs.append("Fastest may produce momentum while leaving uncertainty unresolved.")
    elif decision_style == "cheapest":
        tradeoffs.append("Cheapest may preserve resources while reducing quality, resilience, or upside.")
    elif decision_style == "highest_upside":
        tradeoffs.append("Highest upside may increase uncertainty, complexity, or downside exposure.")
    else:
        tradeoffs.append("Balanced may avoid extremes while making the top priority less decisive.")
    return tradeoffs[:5]


def _suggested_direction(options: list[str], decision_style: str, thin_context: bool, limited_options: bool) -> dict[str, str]:
    if not options:
        return {
            "option": "undetermined",
            "rationale": "No usable option was provided.",
            "certainty": "low",
        }
    if limited_options:
        return {
            "option": options[0],
            "rationale": "Only one usable option was provided, so this is a placeholder direction rather than a comparison result.",
            "certainty": "low",
        }
    certainty = "low" if thin_context else "medium"
    return {
        "option": options[0],
        "rationale": f"From the supplied inputs, start by pressure-testing this option under the {decision_style} lens before committing.",
        "certainty": certainty,
    }


def _confidence(thin_context: bool, limited_options: bool, criteria: list[str], priorities: list[str]) -> str:
    if limited_options:
        return "low"
    if thin_context:
        return "low"
    if criteria and priorities:
        return "medium"
    return "low_to_medium"


def _assumptions(
    criteria: list[str],
    constraints: list[str],
    priorities: list[str],
    context_points: list[str],
    thin_context: bool,
    limited_options: bool,
) -> list[str]:
    assumptions = ["The comparison uses only user-provided decision inputs."]
    if limited_options:
        assumptions.append("The output is not a full comparison because fewer than two usable options were provided.")
    if thin_context:
        assumptions.append("The output is provisional because criteria, constraints, priorities, or context are thin.")
    if criteria:
        assumptions.append("Criteria are treated as the main evaluation frame.")
    if constraints:
        assumptions.append("Constraints are treated as boundaries that may disqualify or weaken options.")
    if priorities:
        assumptions.append("Priorities are treated as tie-breakers when options appear close.")
    if context_points:
        assumptions.append("Context notes are treated as user-provided background, not verified fact.")
    return assumptions[:7]


def _risks(constraints: list[str], thin_context: bool, limited_options: bool, high_stakes: bool) -> list[str]:
    risks = []
    if limited_options:
        risks.append("A single-option result can create false confidence; add at least one real alternative.")
    if thin_context:
        risks.append("Thin context may hide important constraints, costs, risks, or priorities.")
    if constraints:
        risks.append("User-provided constraints should be checked manually before relying on the direction.")
    if high_stakes:
        risks.append("Potentially high-stakes decisions can have consequences that require human or qualified professional review.")
    return risks or ["No specific risk was detected from the supplied inputs, aside from local-only decision support limits."]


def _missing_information(
    criteria: list[str],
    constraints: list[str],
    priorities: list[str],
    context_points: list[str],
    limited_options: bool,
) -> list[str]:
    missing = []
    if limited_options:
        missing.append("At least two usable options are needed for an honest comparison.")
    if not criteria:
        missing.append("Decision criteria were not provided.")
    if not constraints:
        missing.append("Decision constraints were not provided.")
    if not priorities:
        missing.append("Decision priorities were not provided.")
    if not context_points:
        missing.append("Context notes were not provided or were too brief to extract concrete points.")
    return missing or ["No obvious missing information was detected from the supplied decision inputs."]


def _next_actions(thin_context: bool, limited_options: bool, high_stakes: bool) -> list[str]:
    actions = []
    if limited_options:
        actions.append("Add at least one more concrete option.")
    if thin_context:
        actions.append("Add criteria, constraints, priorities, and relevant notes before relying on the comparison.")
    actions.append("Manually check the suggested direction against the highest-cost downside.")
    actions.append("Decide what new information would change the direction.")
    if high_stakes:
        actions.append("Seek appropriate human or qualified professional review before acting.")
    return actions[:5]


def _review_questions(decision_style: str, thin_context: bool, limited_options: bool) -> list[str]:
    questions = [
        "What outcome matters most if two options both look acceptable?",
        "Which downside would make an option unacceptable?",
    ]
    if limited_options:
        questions.append("What is the strongest real alternative to the listed option?")
    if thin_context:
        questions.append("What criteria, constraints, or priorities should be added before deciding?")
    if decision_style == "safest":
        questions.append("What is the worst plausible outcome for each option?")
    elif decision_style == "fastest":
        questions.append("Which option can create a useful result soonest without violating constraints?")
    elif decision_style == "cheapest":
        questions.append("Which visible or hidden costs matter most?")
    elif decision_style == "highest_upside":
        questions.append("What upside would justify added uncertainty or effort?")
    else:
        questions.append("What tradeoff are you most willing to accept?")
    return questions[:6]


def _warnings(thin_context: bool, limited_options: bool, high_stakes: bool) -> list[str]:
    warnings = []
    if limited_options:
        warnings.append("Fewer than two usable options were provided; output is an honest limited comparison.")
    if thin_context:
        warnings.append("Decision context is thin; output is provisional local decision support.")
    if high_stakes:
        warnings.append("Potentially high-stakes subject detected; this response is local decision support only.")
    return warnings


def _limitations(thin_context: bool, limited_options: bool, high_stakes: bool) -> list[str]:
    limitations = [
        "Based only on user-provided decision inputs.",
        "No external verification, source validation, citation validation, professional advice, repo inspection, code execution, or test execution was performed.",
        "No files, database records, tasks, drafts, emails, posts, purchases, uploads, connectors, accounts, shell commands, or external services were used.",
    ]
    if limited_options:
        limitations.append("Fewer than two usable options prevents a full comparison.")
    if thin_context:
        limitations.append("Thin context limits specificity; add criteria, constraints, priorities, or notes for stronger decision support.")
    if high_stakes:
        limitations.append("For legal, medical, financial, academic, safety, or other high-stakes decisions, use this as local decision support only and obtain human or qualified professional verification where appropriate.")
    return limitations


def _looks_high_stakes(*values: object) -> bool:
    text = " ".join(str(value) for value in values).lower()
    high_stakes_terms = (
        "legal",
        "lawsuit",
        "contract",
        "medical",
        "doctor",
        "diagnosis",
        "treatment",
        "financial",
        "investment",
        "loan",
        "tax",
        "academic",
        "admission",
        "grade",
        "security",
        "safety",
        "emergency",
        "employment",
        "firing",
        "hiring",
    )
    return any(term in text for term in high_stakes_terms)
