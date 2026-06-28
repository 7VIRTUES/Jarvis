from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_life_direction_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_life_direction_planning"
SUPPORTED_OUTPUT_TYPES = (
    "life_direction_brief",
    "values_review",
    "priority_plan",
    "five_year_direction",
    "season_plan",
    "tradeoff_review",
    "identity_standards",
    "discipline_plan",
)


@dataclass(frozen=True)
class LocalLifeDirectionRequest:
    life_question: str
    profile_name: str = ""
    current_season: str = ""
    values: list[str] = field(default_factory=list)
    long_term_goals: list[str] = field(default_factory=list)
    current_priorities: list[str] = field(default_factory=list)
    tensions_or_tradeoffs: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    areas_to_improve: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    non_negotiables: list[str] = field(default_factory=list)
    reflection_notes: str = ""
    desired_output_type: str = "life_direction_brief"


class LocalLifeDirectionAgentService:
    def create_plan(self, request: LocalLifeDirectionRequest) -> dict[str, Any]:
        profile_name = _clean_text(request.profile_name) or "Local life direction profile"
        life_question = _clean_text(request.life_question)
        current_season = _clean_text(request.current_season)
        values = _clean_list(request.values)
        long_term_goals = _clean_list(request.long_term_goals)
        current_priorities = _clean_list(request.current_priorities)
        tensions_or_tradeoffs = _clean_list(request.tensions_or_tradeoffs)
        constraints = _clean_list(request.constraints)
        areas_to_improve = _clean_list(request.areas_to_improve)
        strengths = _clean_list(request.strengths)
        non_negotiables = _clean_list(request.non_negotiables)
        reflection_notes = _clean_text(request.reflection_notes)
        desired_output_type = _normalize_output_type(request.desired_output_type)
        thin_input = _thin_input(
            life_question,
            current_season,
            values,
            long_term_goals,
            current_priorities,
            tensions_or_tradeoffs,
            constraints,
            areas_to_improve,
            strengths,
            non_negotiables,
            reflection_notes,
        )
        high_stakes_context = _high_stakes_context(
            life_question,
            current_season,
            values,
            long_term_goals,
            current_priorities,
            tensions_or_tradeoffs,
            constraints,
            areas_to_improve,
            reflection_notes,
        )

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "profileName": profile_name,
            "lifeQuestion": life_question,
            "desiredOutputType": desired_output_type,
            "directionFocus": _direction_focus(life_question, values, long_term_goals, desired_output_type, thin_input),
            "valuesSummary": _values_summary(values, non_negotiables, strengths, thin_input),
            "longTermDirection": _long_term_direction(life_question, long_term_goals, values, constraints),
            "currentSeasonSummary": _current_season_summary(current_season, current_priorities, reflection_notes, thin_input),
            "priorityPlan": _priority_plan(current_priorities, values, long_term_goals, constraints),
            "fiveYearDirection": _five_year_direction(long_term_goals, values, strengths, areas_to_improve),
            "seasonPlan": _season_plan(current_season, current_priorities, areas_to_improve, non_negotiables, constraints),
            "tradeoffReview": _tradeoff_review(tensions_or_tradeoffs, values, non_negotiables, constraints, high_stakes_context),
            "identityStandards": _identity_standards(values, strengths, areas_to_improve, non_negotiables),
            "disciplinePlan": _discipline_plan(current_priorities, areas_to_improve, strengths, constraints),
            "nextActions": _next_actions(desired_output_type, thin_input, high_stakes_context),
            "openQuestions": _open_questions(
                life_question,
                current_season,
                values,
                long_term_goals,
                current_priorities,
                tensions_or_tradeoffs,
                constraints,
                areas_to_improve,
                strengths,
                non_negotiables,
                reflection_notes,
            ),
            "warnings": _warnings(thin_input, high_stakes_context),
            "limitations": _limitations(thin_input, high_stakes_context),
            "safety": local_life_direction_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_life_direction_dashboard_summary()


def local_life_direction_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Life Direction / Values Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/life-direction/local-plan",
        "outputTypes": list(SUPPORTED_OUTPUT_TYPES),
        "responseOnly": True,
        "manualInputOnly": True,
        "localOnly": True,
        "externalServices": False,
        "connectors": False,
        "oauth": False,
        "OAuth": False,
        "accountAccess": False,
        "webBrowsing": False,
        "paidApis": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "calendarAccess": False,
        "messageSending": False,
        "publicPosting": False,
        "purchases": False,
        "healthDataAccess": False,
        "financeDataAccess": False,
        "schoolPortalAccess": False,
        "contactAccess": False,
        "shellExecution": False,
        "mutation": False,
        "therapyClaims": False,
        "diagnosis": False,
        "treatmentPlan": False,
        "crisisIntervention": False,
        "legalValidation": False,
        "financialValidation": False,
        "medicalValidation": False,
        "outcomeGuarantee": False,
        "certificationClaims": False,
        "limitations": ["based only on user-provided life direction, values, and planning notes"],
    }


def local_life_direction_safety() -> dict[str, bool]:
    return {
        "localOnly": True,
        "responseOnly": True,
        "manualInputOnly": True,
        "externalServices": False,
        "connectors": False,
        "oauth": False,
        "OAuth": False,
        "accountAccess": False,
        "webBrowsing": False,
        "paidApis": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "calendarAccess": False,
        "messageSending": False,
        "publicPosting": False,
        "purchases": False,
        "healthDataAccess": False,
        "financeDataAccess": False,
        "schoolPortalAccess": False,
        "contactAccess": False,
        "shellExecution": False,
        "mutation": False,
        "therapyClaims": False,
        "diagnosis": False,
        "treatmentPlan": False,
        "crisisIntervention": False,
        "legalValidation": False,
        "financialValidation": False,
        "medicalValidation": False,
        "outcomeGuarantee": False,
        "certificationClaims": False,
    }


def _normalize_output_type(value: str) -> str:
    normalized = (value or "life_direction_brief").strip().lower()
    return normalized if normalized in SUPPORTED_OUTPUT_TYPES else "life_direction_brief"


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def _clean_list(values: list[str], limit: int = 10) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = _clean_text(value)
        key = item.lower()
        if item and key not in seen:
            cleaned.append(item)
            seen.add(key)
    return cleaned[:limit]


def _thin_input(
    life_question: str,
    current_season: str,
    values: list[str],
    long_term_goals: list[str],
    current_priorities: list[str],
    tensions_or_tradeoffs: list[str],
    constraints: list[str],
    areas_to_improve: list[str],
    strengths: list[str],
    non_negotiables: list[str],
    reflection_notes: str,
) -> bool:
    return not any(
        [
            life_question,
            current_season,
            values,
            long_term_goals,
            current_priorities,
            tensions_or_tradeoffs,
            constraints,
            areas_to_improve,
            strengths,
            non_negotiables,
            reflection_notes,
        ]
    )


def _high_stakes_context(
    life_question: str,
    current_season: str,
    values: list[str],
    long_term_goals: list[str],
    current_priorities: list[str],
    tensions_or_tradeoffs: list[str],
    constraints: list[str],
    areas_to_improve: list[str],
    reflection_notes: str,
) -> bool:
    text = " ".join(
        [
            life_question,
            current_season,
            " ".join(values),
            " ".join(long_term_goals),
            " ".join(current_priorities),
            " ".join(tensions_or_tradeoffs),
            " ".join(constraints),
            " ".join(areas_to_improve),
            reflection_notes,
        ]
    ).lower()
    terms = (
        "self-harm",
        "suicide",
        "crisis",
        "abuse",
        "violence",
        "severe mental health",
        "panic",
        "medical",
        "legal",
        "financial",
        "immigration",
        "eviction",
        "unsafe",
        "emergency",
    )
    return any(term in text for term in terms)


def _direction_focus(life_question: str, values: list[str], long_term_goals: list[str], desired_output_type: str, thin_input: bool) -> list[str]:
    if thin_input:
        return [
            "Capture the life question, current season, values, long-term goals, priorities, tradeoffs, constraints, growth areas, strengths, and non-negotiables before relying on the plan.",
            "Keep the result as reflection and planning only because no files, journals, calendars, tasks, messages, accounts, health data, finance data, school portals, contacts, or external services are accessed.",
        ]
    focus = [f"Primary life question: {life_question}.", f"Requested output shape: {desired_output_type}."]
    if values:
        focus.append("Values to preserve: " + "; ".join(values) + ".")
    if long_term_goals:
        focus.append("Long-term goals to align: " + "; ".join(long_term_goals) + ".")
    focus.append("Use this as values planning, not therapy, diagnosis, treatment, crisis support, professional advice, guaranteed success, or life-outcome certainty.")
    return focus


def _values_summary(values: list[str], non_negotiables: list[str], strengths: list[str], thin_input: bool) -> list[str]:
    if thin_input:
        return ["Values summary is limited until the user provides values, strengths, and non-negotiables."]
    summary = []
    if values:
        summary.append("Declared values: " + "; ".join(values) + ".")
    if non_negotiables:
        summary.append("Non-negotiables: " + "; ".join(non_negotiables) + ".")
    if strengths:
        summary.append("Strengths to build from: " + "; ".join(strengths) + ".")
    if not summary:
        summary.append("Add values and non-negotiables before using this for major direction choices.")
    return summary


def _long_term_direction(life_question: str, long_term_goals: list[str], values: list[str], constraints: list[str]) -> list[str]:
    direction = [
        "Name the kind of person the plan is meant to build, not only the outcomes it is meant to chase.",
        "Separate durable direction from short-term pressure.",
        "Pick goals that can survive tradeoffs across school, career, money, health, projects, relationships, and personal growth.",
    ]
    if life_question:
        direction.insert(0, f"Question to orient around: {life_question}.")
    if long_term_goals:
        direction.append("Long-term goals: " + "; ".join(long_term_goals) + ".")
    if values:
        direction.append("Value alignment check: " + "; ".join(values) + ".")
    if constraints:
        direction.append("Constraints to respect: " + "; ".join(constraints) + ".")
    return direction


def _current_season_summary(current_season: str, current_priorities: list[str], reflection_notes: str, thin_input: bool) -> list[str]:
    if thin_input:
        return ["Current season summary is limited until the user provides season notes, priorities, and reflection context."]
    summary = []
    if current_season:
        summary.append(f"Current season: {current_season}.")
    if current_priorities:
        summary.append("Current priorities: " + "; ".join(current_priorities) + ".")
    if reflection_notes:
        summary.append(f"Reflection notes: {reflection_notes}.")
    if not summary:
        summary.append("Add season context before deciding what should receive attention now.")
    return summary


def _priority_plan(current_priorities: list[str], values: list[str], long_term_goals: list[str], constraints: list[str]) -> list[dict[str, str]]:
    priorities = current_priorities or long_term_goals or values or ["Priority to define manually"]
    plan: list[dict[str, str]] = []
    for priority in priorities[:8]:
        plan.append(
            {
                "priority": priority,
                "whyItMatters": "Tie this priority to a value, long-term goal, or current-season need.",
                "dailyStandard": "Choose one repeatable action small enough to do without drama.",
                "boundary": "; ".join(constraints) if constraints else "Protect focus from goals that do not match the current season.",
            }
        )
    return plan


def _five_year_direction(long_term_goals: list[str], values: list[str], strengths: list[str], areas_to_improve: list[str]) -> list[str]:
    direction = [
        "Imagine the five-year version as a pattern of choices, not a guaranteed destination.",
        "Preserve values before optimizing status, speed, or comparison.",
        "Choose skills, relationships, health, money, school, career, and project habits that compound steadily.",
    ]
    if long_term_goals:
        direction.append("Five-year goal candidates: " + "; ".join(long_term_goals) + ".")
    if values:
        direction.append("Values that should still be visible in five years: " + "; ".join(values) + ".")
    if strengths:
        direction.append("Strengths to compound: " + "; ".join(strengths) + ".")
    if areas_to_improve:
        direction.append("Growth areas to deliberately train: " + "; ".join(areas_to_improve) + ".")
    return direction


def _season_plan(current_season: str, current_priorities: list[str], areas_to_improve: list[str], non_negotiables: list[str], constraints: list[str]) -> list[str]:
    plan = [
        "Pick one main season theme and keep it visible when tradeoffs appear.",
        "Limit active priorities so school, career, money, health, projects, relationships, and growth do not all demand maximum intensity at once.",
        "Review weekly what to continue, reduce, pause, or stop.",
    ]
    if current_season:
        plan.insert(0, f"Season theme from user input: {current_season}.")
    if current_priorities:
        plan.append("Season priorities: " + "; ".join(current_priorities) + ".")
    if areas_to_improve:
        plan.append("Growth practice: " + "; ".join(areas_to_improve) + ".")
    if non_negotiables:
        plan.append("Non-negotiables to protect: " + "; ".join(non_negotiables) + ".")
    if constraints:
        plan.append("Season constraints: " + "; ".join(constraints) + ".")
    return plan


def _tradeoff_review(tensions_or_tradeoffs: list[str], values: list[str], non_negotiables: list[str], constraints: list[str], high_stakes_context: bool) -> list[str]:
    tradeoffs = tensions_or_tradeoffs or ["Tradeoff to define manually"]
    review = []
    for tradeoff in tradeoffs[:8]:
        review.append(f"Tradeoff: {tradeoff}. Compare it against values, non-negotiables, constraints, and long-term direction before deciding.")
    if values:
        review.append("Values lens: " + "; ".join(values) + ".")
    if non_negotiables:
        review.append("Non-negotiable line: " + "; ".join(non_negotiables) + ".")
    if constraints:
        review.append("Constraint reality: " + "; ".join(constraints) + ".")
    if high_stakes_context:
        review.append("High-stakes tradeoffs need appropriate human, professional, official, or emergency support before action.")
    return review


def _identity_standards(values: list[str], strengths: list[str], areas_to_improve: list[str], non_negotiables: list[str]) -> list[str]:
    standards = [
        "Define standards as behaviors that can be practiced, not labels to perform.",
        "Use values to choose what gets repeated when motivation drops.",
        "Keep standards honest, humane, and reviewable.",
    ]
    if values:
        standards.append("Values to turn into standards: " + "; ".join(values) + ".")
    if strengths:
        standards.append("Strengths to embody: " + "; ".join(strengths) + ".")
    if areas_to_improve:
        standards.append("Standards to train: " + "; ".join(areas_to_improve) + ".")
    if non_negotiables:
        standards.append("Lines not to cross: " + "; ".join(non_negotiables) + ".")
    return standards


def _discipline_plan(current_priorities: list[str], areas_to_improve: list[str], strengths: list[str], constraints: list[str]) -> list[str]:
    plan = [
        "Choose one boring repeatable action for the next seven days.",
        "Pair discipline with environment design: remove friction from the right action and add friction to the wrong one.",
        "Track manually what was done, what blocked it, and what to adjust.",
    ]
    if current_priorities:
        plan.append("Discipline should support: " + "; ".join(current_priorities) + ".")
    if areas_to_improve:
        plan.append("Training targets: " + "; ".join(areas_to_improve) + ".")
    if strengths:
        plan.append("Use strengths: " + "; ".join(strengths) + ".")
    if constraints:
        plan.append("Respect constraints: " + "; ".join(constraints) + ".")
    return plan


def _next_actions(desired_output_type: str, thin_input: bool, high_stakes_context: bool) -> list[str]:
    actions = [
        f"Review the {desired_output_type} response and mark what is grounded in user-provided input versus what needs more reflection.",
        "Add missing manual notes for values, long-term goals, current priorities, tradeoffs, constraints, strengths, growth areas, and non-negotiables.",
        "Pick one next manual reflection or checklist step; Jarvis does not create tasks, reminders, messages, posts, purchases, or stored goals.",
    ]
    if thin_input:
        actions.insert(0, "Add enough manual life-direction context before using this for major school, career, money, health, project, relationship, or personal-growth decisions.")
    if high_stakes_context:
        actions.append("Seek appropriate human, professional, official, or emergency help for crisis, self-harm, abuse, violence, severe mental-health distress, legal, medical, financial, immigration, or other high-stakes situations.")
    return actions


def _open_questions(
    life_question: str,
    current_season: str,
    values: list[str],
    long_term_goals: list[str],
    current_priorities: list[str],
    tensions_or_tradeoffs: list[str],
    constraints: list[str],
    areas_to_improve: list[str],
    strengths: list[str],
    non_negotiables: list[str],
    reflection_notes: str,
) -> list[str]:
    questions = []
    if not life_question:
        questions.append("What life-direction or values question should this plan support?")
    if not current_season:
        questions.append("What season is the user in right now?")
    if not values:
        questions.append("Which values should guide the decision?")
    if not long_term_goals:
        questions.append("Which long-term goals matter across school, career, money, health, projects, relationships, and growth?")
    if not current_priorities:
        questions.append("What should receive attention this season?")
    if not tensions_or_tradeoffs:
        questions.append("What tradeoffs, tensions, or sacrifices need to be named?")
    if not constraints:
        questions.append("What constraints are real right now?")
    if not areas_to_improve:
        questions.append("Which areas need deliberate growth?")
    if not strengths:
        questions.append("Which strengths should the plan build from?")
    if not non_negotiables:
        questions.append("What standards or boundaries are non-negotiable?")
    if not reflection_notes:
        questions.append("What reflection notes should be preserved?")
    return questions[:8]


def _warnings(thin_input: bool, high_stakes_context: bool) -> list[str]:
    warnings = [
        "No files, journals, calendars, tasks, accounts, messages, health data, finance data, school portals, contacts, or external services are accessed.",
        "The response does not persist goals, create tasks, create reminders, schedule events, message anyone, post publicly, make purchases, mutate files, or write to databases.",
        "No therapy, mental-health diagnosis, treatment plan, crisis intervention, legal advice, financial advice, medical advice, spiritual authority, guaranteed success, life-outcome certainty, production readiness, or certification is claimed.",
    ]
    if thin_input:
        warnings.insert(0, "The life-direction input is thin; results are a planning scaffold rather than a specific values review.")
    if high_stakes_context:
        warnings.append("Crisis, self-harm, abuse, violence, severe mental-health distress, legal, medical, financial, immigration, or other high-stakes situations need appropriate human, professional, official, or emergency help.")
    return warnings


def _limitations(thin_input: bool, high_stakes_context: bool) -> list[str]:
    limitations = [
        "Based only on user-provided life question, season, values, long-term goals, priorities, tradeoffs, constraints, growth areas, strengths, non-negotiables, and reflection notes.",
        "No file, journal, calendar, task, account, message, health-data, finance-data, school-portal, contact, connector, browsing, posting, purchase, scheduling, persistence, shell execution, database write, or mutation behavior.",
        "No therapy claim, diagnosis, treatment plan, crisis intervention, legal validation, financial validation, medical validation, spiritual authority, guaranteed success, life-outcome certainty, production readiness, security certification, or certification claim.",
    ]
    if thin_input:
        limitations.append("Thin input limits specificity until the user supplies concrete values, goals, priorities, tradeoffs, constraints, strengths, growth areas, and non-negotiables.")
    if high_stakes_context:
        limitations.append("Crisis, self-harm, abuse, violence, severe mental-health distress, legal, medical, financial, immigration, and other high-stakes situations should be handled with appropriate human, professional, official, or emergency support.")
    return limitations
