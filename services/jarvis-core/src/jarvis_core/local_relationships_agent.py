from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_relationships_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_relationship_planning"
SUPPORTED_OUTPUT_TYPES = (
    "relationship_brief",
    "conversation_plan",
    "boundary_plan",
    "conflict_prep",
    "apology_draft",
    "check_in_plan",
    "gift_occasion_plan",
    "relationship_maintenance",
)


@dataclass(frozen=True)
class LocalRelationshipsRequest:
    relationship_goal: str
    profile_name: str = ""
    relationship_type: str = ""
    people_context: str = ""
    situation_notes: str = ""
    communication_goals: list[str] = field(default_factory=list)
    concerns: list[str] = field(default_factory=list)
    boundaries: list[str] = field(default_factory=list)
    desired_tone: str = ""
    constraints: list[str] = field(default_factory=list)
    desired_output_type: str = "relationship_brief"


class LocalRelationshipsAgentService:
    def create_plan(self, request: LocalRelationshipsRequest) -> dict[str, Any]:
        profile_name = _clean_text(request.profile_name) or "Local relationship profile"
        relationship_goal = _clean_text(request.relationship_goal)
        relationship_type = _clean_text(request.relationship_type)
        people_context = _clean_text(request.people_context)
        situation_notes = _clean_text(request.situation_notes)
        communication_goals = _clean_list(request.communication_goals)
        concerns = _clean_list(request.concerns)
        boundaries = _clean_list(request.boundaries)
        desired_tone = _clean_text(request.desired_tone)
        constraints = _clean_list(request.constraints)
        desired_output_type = _normalize_output_type(request.desired_output_type)
        unsafe_context = _unsafe_context(
            relationship_goal,
            people_context,
            situation_notes,
            communication_goals,
            concerns,
            boundaries,
            constraints,
        )
        high_stakes_context = _high_stakes_context(relationship_goal, people_context, situation_notes, concerns, boundaries, constraints)
        thin_input = _thin_input(
            relationship_goal,
            relationship_type,
            people_context,
            situation_notes,
            communication_goals,
            concerns,
            boundaries,
            desired_tone,
            constraints,
        )

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "profileName": profile_name,
            "relationshipGoal": relationship_goal,
            "desiredOutputType": desired_output_type,
            "relationshipFocus": _relationship_focus(relationship_goal, relationship_type, desired_output_type, thin_input, unsafe_context),
            "situationSummary": _situation_summary(relationship_type, people_context, situation_notes, desired_tone, thin_input),
            "communicationPlan": _communication_plan(communication_goals, desired_tone, concerns, boundaries, unsafe_context),
            "conversationScripts": _conversation_scripts(relationship_goal, communication_goals, desired_tone, boundaries, unsafe_context),
            "boundaryPlan": _boundary_plan(boundaries, concerns, desired_tone, unsafe_context),
            "conflictPrep": _conflict_prep(relationship_goal, concerns, boundaries, constraints, high_stakes_context),
            "apologyDrafts": _apology_drafts(relationship_goal, relationship_type, desired_tone, unsafe_context),
            "checkInPlan": _check_in_plan(relationship_type, communication_goals, concerns, boundaries),
            "giftOccasionPlan": _gift_occasion_plan(relationship_type, people_context, situation_notes, constraints),
            "relationshipMaintenance": _relationship_maintenance(relationship_type, communication_goals, boundaries, constraints),
            "nextActions": _next_actions(desired_output_type, thin_input, unsafe_context, high_stakes_context),
            "openQuestions": _open_questions(
                relationship_goal,
                relationship_type,
                people_context,
                situation_notes,
                communication_goals,
                concerns,
                boundaries,
                desired_tone,
                constraints,
            ),
            "warnings": _warnings(thin_input, unsafe_context, high_stakes_context),
            "limitations": _limitations(thin_input, unsafe_context, high_stakes_context),
            "safety": local_relationships_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_relationships_dashboard_summary()


def local_relationships_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Relationship / Family Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/relationships/local-plan",
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
        "contactAccess": False,
        "messageAccess": False,
        "emailSending": False,
        "calendarAccess": False,
        "socialPlatformAccess": False,
        "publicPosting": False,
        "messaging": False,
        "profileScraping": False,
        "locationAccess": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "mutation": False,
        "manipulationGuidance": False,
        "coercionGuidance": False,
        "harassmentGuidance": False,
        "stalkingGuidance": False,
        "doxxingGuidance": False,
        "impersonationGuidance": False,
        "therapyClaims": False,
        "diagnosis": False,
        "treatmentPlan": False,
        "relationshipOutcomeGuarantee": False,
        "legalValidation": False,
        "safetyValidation": False,
        "certificationClaims": False,
        "limitations": ["based only on user-provided relationship and family communication notes"],
    }


def local_relationships_safety() -> dict[str, bool]:
    summary = local_relationships_dashboard_summary().copy()
    summary.pop("agentId", None)
    summary.pop("name", None)
    summary.pop("status", None)
    summary.pop("mode", None)
    summary.pop("endpoint", None)
    summary.pop("outputTypes", None)
    summary.pop("limitations", None)
    return summary


def _normalize_output_type(value: str) -> str:
    normalized = (value or "relationship_brief").strip().lower()
    return normalized if normalized in SUPPORTED_OUTPUT_TYPES else "relationship_brief"


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
    relationship_goal: str,
    relationship_type: str,
    people_context: str,
    situation_notes: str,
    communication_goals: list[str],
    concerns: list[str],
    boundaries: list[str],
    desired_tone: str,
    constraints: list[str],
) -> bool:
    return not any([relationship_goal, relationship_type, people_context, situation_notes, communication_goals, concerns, boundaries, desired_tone, constraints])


def _unsafe_context(
    relationship_goal: str,
    people_context: str,
    situation_notes: str,
    communication_goals: list[str],
    concerns: list[str],
    boundaries: list[str],
    constraints: list[str],
) -> bool:
    text = " ".join([relationship_goal, people_context, situation_notes, " ".join(communication_goals), " ".join(concerns), " ".join(boundaries), " ".join(constraints)]).lower()
    terms = (
        "manipulate",
        "coerce",
        "deceive",
        "harass",
        "stalk",
        "dox",
        "impersonate",
        "evade",
        "jealousy control",
        "make them",
        "track them",
        "private information",
        "pressure them",
    )
    return any(term in text for term in terms)


def _high_stakes_context(
    relationship_goal: str,
    people_context: str,
    situation_notes: str,
    concerns: list[str],
    boundaries: list[str],
    constraints: list[str],
) -> bool:
    text = " ".join([relationship_goal, people_context, situation_notes, " ".join(concerns), " ".join(boundaries), " ".join(constraints)]).lower()
    terms = (
        "abuse",
        "violence",
        "stalking",
        "coercive control",
        "self-harm",
        "suicide",
        "severe mental health",
        "legal danger",
        "immediate safety",
        "threat",
        "unsafe",
    )
    return any(term in text for term in terms)


def _relationship_focus(relationship_goal: str, relationship_type: str, desired_output_type: str, thin_input: bool, unsafe_context: bool) -> list[str]:
    if thin_input:
        return [
            "Capture the relationship goal, relationship type, people context, situation notes, communication goals, concerns, boundaries, tone, and constraints before relying on the plan.",
            "Keep the result as manual planning and drafts only because no contacts, messages, accounts, calendars, files, locations, platforms, or external services are accessed.",
        ]
    if unsafe_context:
        return [
            "Redirect the relationship plan toward respectful, consent-aware, honest, non-controlling communication.",
            "Avoid manipulation, coercion, deception, harassment, stalking, doxxing, impersonation, jealousy-control, pressure, or evasion.",
        ]
    focus = [f"Relationship goal: {relationship_goal}.", f"Requested output shape: {desired_output_type}."]
    if relationship_type:
        focus.append(f"Relationship type from user input: {relationship_type}.")
    focus.append("Use this as communication planning, not therapy, diagnosis, treatment, legal validation, safety validation, emotional certainty, or a guaranteed relationship outcome.")
    return focus


def _situation_summary(relationship_type: str, people_context: str, situation_notes: str, desired_tone: str, thin_input: bool) -> list[str]:
    if thin_input:
        return ["Situation summary is limited until the user provides relationship context, situation notes, and desired tone."]
    summary = []
    if relationship_type:
        summary.append(f"Relationship type: {relationship_type}.")
    if people_context:
        summary.append(f"People context: {people_context}.")
    if situation_notes:
        summary.append(f"Situation notes: {situation_notes}.")
    if desired_tone:
        summary.append(f"Desired tone: {desired_tone}.")
    if not summary:
        summary.append("Add people context and situation notes before choosing a communication plan.")
    return summary


def _communication_plan(communication_goals: list[str], desired_tone: str, concerns: list[str], boundaries: list[str], unsafe_context: bool) -> list[str]:
    if unsafe_context:
        return ["Use direct, honest, low-pressure communication and remove any controlling, deceptive, or invasive tactics."]
    plan = [
        "Start with one clear purpose for the conversation.",
        "Use observations and feelings without claiming certainty about the other person's motives.",
        "Ask one open question and leave room for pause, disagreement, or ending the conversation.",
    ]
    if communication_goals:
        plan.insert(0, "Communication goals: " + "; ".join(communication_goals) + ".")
    if desired_tone:
        plan.append(f"Tone to aim for: {desired_tone}.")
    if concerns:
        plan.append("Concerns to name carefully: " + "; ".join(concerns) + ".")
    if boundaries:
        plan.append("Boundaries to keep visible: " + "; ".join(boundaries) + ".")
    return plan


def _conversation_scripts(relationship_goal: str, communication_goals: list[str], desired_tone: str, boundaries: list[str], unsafe_context: bool) -> list[str]:
    if unsafe_context:
        return ["I want to keep this respectful and honest. I will not pressure you, track you, or push past your boundaries."]
    goal = relationship_goal or "this situation"
    tone = desired_tone or "calm and respectful"
    scripts = [
        f"I want to talk about {goal} in a {tone} way.",
        "My goal is to understand your perspective and share mine without turning this into a fight.",
        "If now is not a good time, we can pause and choose another time manually.",
    ]
    if communication_goals:
        scripts.append("What I hope we can cover: " + "; ".join(communication_goals[:4]) + ".")
    if boundaries:
        scripts.append("A boundary I need to be honest about: " + "; ".join(boundaries[:3]) + ".")
    return scripts


def _boundary_plan(boundaries: list[str], concerns: list[str], desired_tone: str, unsafe_context: bool) -> list[str]:
    if unsafe_context:
        return ["Set boundaries for safety and honesty only; do not use boundaries as threats, tests, traps, or control tactics."]
    plan = [
        "State the boundary in plain language.",
        "Explain what you will do to protect the boundary, not what you will force the other person to do.",
        "Keep the tone steady and repeatable.",
    ]
    if boundaries:
        plan.insert(0, "Boundaries from user input: " + "; ".join(boundaries) + ".")
    if concerns:
        plan.append("Concerns the boundary should address: " + "; ".join(concerns) + ".")
    if desired_tone:
        plan.append(f"Tone for boundary language: {desired_tone}.")
    return plan


def _conflict_prep(relationship_goal: str, concerns: list[str], boundaries: list[str], constraints: list[str], high_stakes_context: bool) -> list[str]:
    prep = [
        "Decide what would make the conversation worth having and what would make it worth pausing.",
        "Avoid arguing every detail; focus on the pattern, request, apology, boundary, or next step.",
        "Prepare a pause line before emotions rise.",
    ]
    if relationship_goal:
        prep.insert(0, f"Conflict-prep goal: {relationship_goal}.")
    if concerns:
        prep.append("Concerns to prepare for: " + "; ".join(concerns) + ".")
    if boundaries:
        prep.append("Boundaries to protect: " + "; ".join(boundaries) + ".")
    if constraints:
        prep.append("Constraints: " + "; ".join(constraints) + ".")
    if high_stakes_context:
        prep.append("Safety, abuse, violence, coercive control, self-harm, severe mental-health distress, or legal danger needs appropriate human, professional, or emergency help.")
    return prep


def _apology_drafts(relationship_goal: str, relationship_type: str, desired_tone: str, unsafe_context: bool) -> list[str]:
    if unsafe_context:
        return ["I am sorry for my part. I do not want to pressure you into forgiving me or responding before you are ready."]
    tone = desired_tone or "plain and sincere"
    context = relationship_type or "our relationship"
    return [
        f"I want to apologize in a {tone} way for my part in {context}.",
        "I understand that impact matters, not just what I meant. I am willing to listen and change the part I control.",
        f"My goal is not to force a particular outcome. It is to take responsibility around {relationship_goal or 'what happened'}.",
    ]


def _check_in_plan(relationship_type: str, communication_goals: list[str], concerns: list[str], boundaries: list[str]) -> list[str]:
    plan = [
        "Pick a low-pressure check-in time manually.",
        "Ask how the other person is experiencing the relationship or situation.",
        "Share one appreciation, one concern, and one next step if appropriate.",
    ]
    if relationship_type:
        plan.insert(0, f"Check-in context: {relationship_type}.")
    if communication_goals:
        plan.append("Check-in goals: " + "; ".join(communication_goals[:4]) + ".")
    if concerns:
        plan.append("Concerns to check gently: " + "; ".join(concerns[:4]) + ".")
    if boundaries:
        plan.append("Boundaries to preserve: " + "; ".join(boundaries[:4]) + ".")
    return plan


def _gift_occasion_plan(relationship_type: str, people_context: str, situation_notes: str, constraints: list[str]) -> list[str]:
    plan = [
        "Choose a gift or occasion plan that reflects the person, not pressure to impress.",
        "Prefer thoughtful, appropriate, and sustainable over expensive or performative.",
        "Avoid gifts that create obligation, surveillance, or discomfort.",
    ]
    if relationship_type:
        plan.append(f"Relationship context: {relationship_type}.")
    if people_context:
        plan.append(f"People context: {people_context}.")
    if situation_notes:
        plan.append(f"Occasion or situation notes: {situation_notes}.")
    if constraints:
        plan.append("Constraints to respect: " + "; ".join(constraints) + ".")
    return plan


def _relationship_maintenance(relationship_type: str, communication_goals: list[str], boundaries: list[str], constraints: list[str]) -> list[str]:
    plan = [
        "Notice small repair moments before they become major conflict.",
        "Make appreciation specific and criticism bounded.",
        "Keep maintenance mutual: connection, respect, honesty, boundaries, and repair.",
    ]
    if relationship_type:
        plan.append(f"Maintenance context: {relationship_type}.")
    if communication_goals:
        plan.append("Habits to maintain: " + "; ".join(communication_goals[:5]) + ".")
    if boundaries:
        plan.append("Boundaries to maintain: " + "; ".join(boundaries[:5]) + ".")
    if constraints:
        plan.append("Constraints: " + "; ".join(constraints) + ".")
    return plan


def _next_actions(desired_output_type: str, thin_input: bool, unsafe_context: bool, high_stakes_context: bool) -> list[str]:
    actions = [
        f"Review the {desired_output_type} response and remove anything that feels controlling, invasive, overclaimed, or unsafe.",
        "Add missing manual notes for relationship type, people context, situation, communication goals, concerns, boundaries, tone, and constraints.",
        "Choose one script, one boundary, or one check-in step to practice manually.",
    ]
    if thin_input:
        actions.insert(0, "Add enough manual relationship context before using this for conflict, apology, boundary, or maintenance planning.")
    if unsafe_context:
        actions.append("Replace manipulation, coercion, deception, harassment, stalking, doxxing, impersonation, jealousy-control, or evasion with respectful boundary-aware communication.")
    if high_stakes_context:
        actions.append("Use appropriate human, professional, legal, safety, or emergency help for abuse, violence, stalking, coercive control, self-harm, severe distress, legal danger, or immediate safety concerns.")
    return actions


def _open_questions(
    relationship_goal: str,
    relationship_type: str,
    people_context: str,
    situation_notes: str,
    communication_goals: list[str],
    concerns: list[str],
    boundaries: list[str],
    desired_tone: str,
    constraints: list[str],
) -> list[str]:
    questions = []
    if not relationship_goal:
        questions.append("What family, friendship, dating, roommate, apology, boundary, conflict, or relationship-maintenance goal should this support?")
    if not relationship_type:
        questions.append("What relationship type is this: family, friend, dating, roommate, coworker, or another context?")
    if not people_context:
        questions.append("Who is involved, and what context matters?")
    if not situation_notes:
        questions.append("What happened, what occasion is coming up, or what pattern needs attention?")
    if not communication_goals:
        questions.append("What should the communication accomplish without pressuring anyone?")
    if not concerns:
        questions.append("What concerns, sensitivities, or risks should be handled carefully?")
    if not boundaries:
        questions.append("What boundaries need to be respected?")
    if not desired_tone:
        questions.append("What tone should the plan use?")
    if not constraints:
        questions.append("What safety, timing, privacy, family, cultural, or practical constraints apply?")
    return questions[:8]


def _warnings(thin_input: bool, unsafe_context: bool, high_stakes_context: bool) -> list[str]:
    warnings = [
        "No contacts, messages, DMs, email, calendar, social platforms, location, photos, files, accounts, or external services are accessed.",
        "The response does not send messages, schedule meetings, post publicly, scrape profiles, track people, identify private information, persist records, create tasks, or mutate files.",
        "No therapy, diagnosis, treatment plan, relationship outcome certainty, conflict resolution guarantee, legal validation, safety validation, emotional certainty, production readiness, or certification is claimed.",
    ]
    if thin_input:
        warnings.insert(0, "The relationship input is thin; results are a planning scaffold rather than specific relationship advice.")
    if unsafe_context:
        warnings.append("Manipulation, coercion, deception, harassment, stalking, doxxing, impersonation, jealousy-control, and evasion guidance are not supported.")
    if high_stakes_context:
        warnings.append("Abuse, violence, stalking, coercive control, self-harm, severe mental-health distress, legal danger, or immediate safety concerns need appropriate human, professional, or emergency help.")
    return warnings


def _limitations(thin_input: bool, unsafe_context: bool, high_stakes_context: bool) -> list[str]:
    limitations = [
        "Based only on user-provided relationship goal, relationship type, people context, situation notes, communication goals, concerns, boundaries, tone, and constraints.",
        "No contact, message, DM, email, calendar, social-platform, location, photo, file, account, connector, browsing, scraping, sending, posting, scheduling, tracking, persistence, shell execution, task creation, database write, or mutation behavior.",
        "No manipulation, coercion, deception, harassment, stalking, doxxing, impersonation, jealousy-control, evasion, therapy claim, diagnosis, treatment plan, relationship outcome certainty, conflict resolution guarantee, legal validation, safety validation, emotional certainty, production readiness, security certification, or certification claim.",
    ]
    if thin_input:
        limitations.append("Thin input limits specificity until the user supplies concrete relationship context, situation notes, goals, concerns, boundaries, tone, and constraints.")
    if unsafe_context:
        limitations.append("Unsafe or controlling goals must be reframed into respectful, consent-aware, truthful, and non-invasive communication.")
    if high_stakes_context:
        limitations.append("Abuse, violence, stalking, coercive control, self-harm, severe mental-health distress, legal danger, and immediate safety concerns should be handled with appropriate human, professional, legal, safety, or emergency support.")
    return limitations
