from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_social_networking_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_social_networking_planning"
SUPPORTED_OUTPUT_TYPES = (
    "social_brief",
    "conversation_plan",
    "networking_plan",
    "event_prep",
    "etiquette_checklist",
    "presence_plan",
    "follow_up_draft",
    "social_review",
)


@dataclass(frozen=True)
class LocalSocialNetworkingRequest:
    social_goal: str
    profile_name: str = ""
    setting: str = ""
    people_context: str = ""
    event_notes: str = ""
    conversation_topics: list[str] = field(default_factory=list)
    networking_goals: list[str] = field(default_factory=list)
    presentation_notes: str = ""
    constraints: list[str] = field(default_factory=list)
    comfort_level: str = ""
    desired_output_type: str = "social_brief"


class LocalSocialNetworkingAgentService:
    def create_plan(self, request: LocalSocialNetworkingRequest) -> dict[str, Any]:
        profile_name = _clean_text(request.profile_name) or "Local social profile"
        social_goal = _clean_text(request.social_goal)
        setting = _clean_text(request.setting)
        people_context = _clean_text(request.people_context)
        event_notes = _clean_text(request.event_notes)
        conversation_topics = _clean_list(request.conversation_topics)
        networking_goals = _clean_list(request.networking_goals)
        presentation_notes = _clean_text(request.presentation_notes)
        constraints = _clean_list(request.constraints)
        comfort_level = _clean_text(request.comfort_level)
        desired_output_type = _normalize_output_type(request.desired_output_type)
        unsafe_context = _unsafe_context(social_goal, people_context, event_notes, conversation_topics, networking_goals, constraints)
        high_stakes_context = _high_stakes_context(social_goal, people_context, event_notes, constraints)
        thin_input = _thin_input(
            social_goal,
            setting,
            people_context,
            event_notes,
            conversation_topics,
            networking_goals,
            presentation_notes,
            constraints,
            comfort_level,
        )

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "profileName": profile_name,
            "socialGoal": social_goal,
            "desiredOutputType": desired_output_type,
            "socialFocus": _social_focus(social_goal, setting, comfort_level, desired_output_type, thin_input, unsafe_context),
            "settingSummary": _setting_summary(setting, people_context, event_notes, comfort_level, thin_input),
            "conversationPlan": _conversation_plan(social_goal, conversation_topics, people_context, constraints, unsafe_context),
            "networkingPlan": _networking_plan(networking_goals, setting, people_context, event_notes, constraints),
            "eventPrep": _event_prep(setting, event_notes, presentation_notes, comfort_level, constraints),
            "etiquetteChecklist": _etiquette_checklist(setting, people_context, constraints),
            "presencePlan": _presence_plan(presentation_notes, comfort_level, social_goal, constraints),
            "followUpDrafts": _follow_up_drafts(networking_goals, conversation_topics, setting, unsafe_context),
            "socialReview": _social_review(social_goal, setting, people_context, event_notes, constraints, unsafe_context),
            "nextActions": _next_actions(desired_output_type, thin_input, unsafe_context, high_stakes_context),
            "openQuestions": _open_questions(
                social_goal,
                setting,
                people_context,
                event_notes,
                conversation_topics,
                networking_goals,
                presentation_notes,
                constraints,
                comfort_level,
            ),
            "warnings": _warnings(thin_input, unsafe_context, high_stakes_context),
            "limitations": _limitations(thin_input, unsafe_context, high_stakes_context),
            "safety": local_social_networking_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_social_networking_dashboard_summary()


def local_social_networking_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Social / Networking / High-Class Coach Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/social-networking/local-plan",
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
        "emailSending": False,
        "calendarAccess": False,
        "socialPlatformAccess": False,
        "messaging": False,
        "publicPosting": False,
        "profileScraping": False,
        "locationAccess": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "mutation": False,
        "manipulationGuidance": False,
        "harassmentGuidance": False,
        "stalkingGuidance": False,
        "impersonationGuidance": False,
        "outcomeGuarantee": False,
        "certificationClaims": False,
        "limitations": ["based only on user-provided social, networking, event, and etiquette notes"],
    }


def local_social_networking_safety() -> dict[str, bool]:
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
        "contactAccess": False,
        "emailSending": False,
        "calendarAccess": False,
        "socialPlatformAccess": False,
        "messaging": False,
        "publicPosting": False,
        "profileScraping": False,
        "locationAccess": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "mutation": False,
        "manipulationGuidance": False,
        "harassmentGuidance": False,
        "stalkingGuidance": False,
        "impersonationGuidance": False,
        "outcomeGuarantee": False,
        "certificationClaims": False,
    }


def _normalize_output_type(value: str) -> str:
    normalized = (value or "social_brief").strip().lower()
    return normalized if normalized in SUPPORTED_OUTPUT_TYPES else "social_brief"


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
    social_goal: str,
    setting: str,
    people_context: str,
    event_notes: str,
    conversation_topics: list[str],
    networking_goals: list[str],
    presentation_notes: str,
    constraints: list[str],
    comfort_level: str,
) -> bool:
    return not any(
        [
            social_goal,
            setting,
            people_context,
            event_notes,
            conversation_topics,
            networking_goals,
            presentation_notes,
            constraints,
            comfort_level,
        ]
    )


def _unsafe_context(
    social_goal: str,
    people_context: str,
    event_notes: str,
    conversation_topics: list[str],
    networking_goals: list[str],
    constraints: list[str],
) -> bool:
    text = " ".join(
        [
            social_goal,
            people_context,
            event_notes,
            " ".join(conversation_topics),
            " ".join(networking_goals),
            " ".join(constraints),
        ]
    ).lower()
    terms = (
        "manipulate",
        "coerce",
        "deceive",
        "harass",
        "stalk",
        "dox",
        "impersonate",
        "evade",
        "pressure",
        "track them",
        "private information",
        "make them",
    )
    return any(term in text for term in terms)


def _high_stakes_context(social_goal: str, people_context: str, event_notes: str, constraints: list[str]) -> bool:
    text = " ".join([social_goal, people_context, event_notes, " ".join(constraints)]).lower()
    terms = (
        "legal",
        "workplace",
        "harassment",
        "consent",
        "safety",
        "mental health",
        "threat",
        "abuse",
        "discrimination",
        "hr",
        "manager",
    )
    return any(term in text for term in terms)


def _social_focus(
    social_goal: str,
    setting: str,
    comfort_level: str,
    desired_output_type: str,
    thin_input: bool,
    unsafe_context: bool,
) -> list[str]:
    if thin_input:
        return [
            "Capture the social goal, setting, people context, event notes, conversation topics, networking goals, constraints, and comfort level before choosing a plan.",
            "Keep the result as manual planning and drafting only because no contacts, messages, platforms, accounts, files, location, or external services are accessed.",
        ]
    if unsafe_context:
        return [
            "Redirect the request toward respectful, consent-aware, non-manipulative communication.",
            "Avoid tactics involving coercion, deception, harassment, stalking, doxxing, impersonation, pressure, or evasion.",
        ]
    focus = [f"Primary social goal: {social_goal}.", f"Requested output shape: {desired_output_type}."]
    if setting:
        focus.append(f"Setting from user input: {setting}.")
    if comfort_level:
        focus.append(f"Comfort level from user input: {comfort_level}.")
    focus.append("Use this as a social-prep aid, not a guarantee of acceptance, reputation, relationships, hiring outcomes, or etiquette certification.")
    return focus


def _setting_summary(setting: str, people_context: str, event_notes: str, comfort_level: str, thin_input: bool) -> list[str]:
    if thin_input:
        return ["Setting summary is limited until the user provides setting, people context, event notes, and comfort level."]
    summary = []
    if setting:
        summary.append(f"Setting: {setting}.")
    if people_context:
        summary.append(f"People context: {people_context}.")
    if event_notes:
        summary.append(f"Event notes: {event_notes}.")
    if comfort_level:
        summary.append(f"Comfort level: {comfort_level}.")
    if not summary:
        summary.append("Add the setting and people context before relying on the plan.")
    return summary


def _conversation_plan(
    social_goal: str,
    conversation_topics: list[str],
    people_context: str,
    constraints: list[str],
    unsafe_context: bool,
) -> list[dict[str, str]]:
    if unsafe_context:
        return [
            {
                "step": "Respectful reset",
                "script": "I want to keep this respectful and comfortable. If this topic is not welcome, I can change direction.",
                "boundary": "Do not pressure, deceive, track, harass, impersonate, or search for private information.",
            }
        ]
    topics = conversation_topics or ["Light introduction", "Shared context", "Thoughtful follow-up"]
    plan: list[dict[str, str]] = []
    for topic in topics[:6]:
        plan.append(
            {
                "topic": topic,
                "opener": f"Ask a natural, low-pressure question about {topic}.",
                "listenFor": "Specific interests, comfort, time limits, and cues to shift or pause.",
                "bridge": f"Connect {topic} back to the social goal only if it feels relevant and welcome.",
                "boundary": "Keep the exchange mutual, truthful, and easy to exit.",
            }
        )
    if social_goal:
        plan.append({"topic": "Goal alignment", "opener": social_goal, "listenFor": people_context or "Context from the other person.", "bridge": "Use one concise sentence.", "boundary": "; ".join(constraints) if constraints else "Avoid overclaiming or overtalking."})
    return plan


def _networking_plan(
    networking_goals: list[str],
    setting: str,
    people_context: str,
    event_notes: str,
    constraints: list[str],
) -> list[str]:
    plan = [
        "Prepare a one-sentence introduction that names who you are, what you care about, and one relevant project or interest.",
        "Choose two generous questions that make the other person easy to talk to.",
        "Plan one respectful exit line before the conversation starts.",
        "Write follow-up notes manually after the event if the exchange was welcome.",
    ]
    if networking_goals:
        plan.insert(0, "Networking goals: " + "; ".join(networking_goals) + ".")
    if setting:
        plan.append(f"Adapt tone to the setting: {setting}.")
    if people_context:
        plan.append(f"People context to respect: {people_context}.")
    if event_notes:
        plan.append(f"Event notes to use manually: {event_notes}.")
    if constraints:
        plan.append("Constraints and boundaries: " + "; ".join(constraints) + ".")
    return plan


def _event_prep(setting: str, event_notes: str, presentation_notes: str, comfort_level: str, constraints: list[str]) -> list[str]:
    prep = [
        "Confirm arrival time, dress expectations, format, and whether conversation is casual, formal, or mixed.",
        "Prepare a calm introduction, two conversation topics, and one graceful exit.",
        "Bring only what the event requires and avoid trying to perform a persona.",
        "Afterward, write a short reflection on what felt natural and what to practice.",
    ]
    if setting:
        prep.insert(0, f"Event setting: {setting}.")
    if event_notes:
        prep.append(f"Event notes: {event_notes}.")
    if presentation_notes:
        prep.append(f"Presentation notes: {presentation_notes}.")
    if comfort_level:
        prep.append(f"Comfort level to plan around: {comfort_level}.")
    if constraints:
        prep.append("Constraints to respect: " + "; ".join(constraints) + ".")
    return prep


def _etiquette_checklist(setting: str, people_context: str, constraints: list[str]) -> list[str]:
    checklist = [
        "Arrive with enough time to settle before approaching people.",
        "Use names carefully, listen more than you pitch, and avoid interrupting.",
        "Keep introductions short and ask permission before deeper topics.",
        "Respect exits, disinterest, relationship status, workplace boundaries, and privacy.",
        "Avoid gossip, status flexing, private information asks, and pressure tactics.",
        "Follow up only when the exchange was welcome and appropriate.",
    ]
    if setting:
        checklist.append(f"Adapt etiquette to setting: {setting}.")
    if people_context:
        checklist.append(f"Respect people context: {people_context}.")
    if constraints:
        checklist.append("Constraints: " + "; ".join(constraints) + ".")
    return checklist


def _presence_plan(presentation_notes: str, comfort_level: str, social_goal: str, constraints: list[str]) -> list[str]:
    plan = [
        "Aim for composed, sincere, and situationally appropriate rather than flashy.",
        "Use steady posture, relaxed pace, clear speech, and attentive listening.",
        "Prepare one short personal anchor story that is true and relevant.",
        "Choose grooming and dress notes manually based on the event's expectations and comfort.",
    ]
    if presentation_notes:
        plan.append(f"Presentation focus: {presentation_notes}.")
    if comfort_level:
        plan.append(f"Confidence plan around comfort level: {comfort_level}.")
    if social_goal:
        plan.append(f"Presence should support: {social_goal}.")
    if constraints:
        plan.append("Presence constraints: " + "; ".join(constraints) + ".")
    return plan


def _follow_up_drafts(
    networking_goals: list[str],
    conversation_topics: list[str],
    setting: str,
    unsafe_context: bool,
) -> list[str]:
    if unsafe_context:
        return [
            "Thanks for the conversation. I want to be respectful of your comfort and boundaries, so no reply is needed."
        ]
    goal_line = "; ".join(networking_goals) if networking_goals else "the conversation"
    topic_line = "; ".join(conversation_topics[:3]) if conversation_topics else "what we discussed"
    setting_line = f" at {setting}" if setting else ""
    return [
        f"Thanks for taking a moment to talk{setting_line}. I appreciated hearing your perspective on {topic_line}.",
        f"I enjoyed our conversation about {topic_line}. If it is useful, I would be glad to continue the conversation around {goal_line}.",
        "Thank you again for your time. Wishing you a smooth rest of the event.",
    ]


def _social_review(
    social_goal: str,
    setting: str,
    people_context: str,
    event_notes: str,
    constraints: list[str],
    unsafe_context: bool,
) -> list[str]:
    review = [
        "Does the plan respect consent, boundaries, honesty, privacy, and easy exits?",
        "Does it avoid claiming guaranteed acceptance, relationship outcomes, hiring outcomes, or reputation changes?",
        "Does the follow-up remain optional and low-pressure?",
    ]
    if unsafe_context:
        review.insert(0, "Unsafe or coercive request elements were redirected to respectful communication.")
    if social_goal:
        review.append(f"Goal to review manually: {social_goal}.")
    if setting:
        review.append(f"Setting to review manually: {setting}.")
    if people_context:
        review.append(f"People context to review manually: {people_context}.")
    if event_notes:
        review.append(f"Event notes to review manually: {event_notes}.")
    if constraints:
        review.append("Constraints to verify: " + "; ".join(constraints) + ".")
    return review


def _next_actions(desired_output_type: str, thin_input: bool, unsafe_context: bool, high_stakes_context: bool) -> list[str]:
    actions = [
        f"Review the {desired_output_type} response and remove anything that feels unnatural, intrusive, or overclaimed.",
        "Add missing manual notes for setting, people context, event format, conversation topics, networking goals, presentation needs, constraints, and comfort level.",
        "Practice one opener, one listening question, and one graceful exit out loud.",
    ]
    if thin_input:
        actions.insert(0, "Add enough manual social context before using this for an event, workplace interaction, or follow-up.")
    if unsafe_context:
        actions.append("Replace any manipulative, coercive, deceptive, harassing, stalking, doxxing, or impersonation request with respectful boundary-aware communication.")
    if high_stakes_context:
        actions.append("Ask appropriate human, workplace, legal, safety, consent, or mental-health support for high-stakes concerns.")
    return actions


def _open_questions(
    social_goal: str,
    setting: str,
    people_context: str,
    event_notes: str,
    conversation_topics: list[str],
    networking_goals: list[str],
    presentation_notes: str,
    constraints: list[str],
    comfort_level: str,
) -> list[str]:
    questions = []
    if not social_goal:
        questions.append("What social, networking, etiquette, or confidence goal should this support?")
    if not setting:
        questions.append("What setting is this for: dinner, class, conference, interview-adjacent event, party, or workplace?")
    if not people_context:
        questions.append("Who will be present, and what boundaries or relationship context matter?")
    if not event_notes:
        questions.append("What event format, dress expectations, timing, or social norms are known from user notes?")
    if not conversation_topics:
        questions.append("Which conversation topics feel natural, appropriate, and safe?")
    if not networking_goals:
        questions.append("What networking outcomes are desired without pressuring anyone?")
    if not presentation_notes:
        questions.append("What presence, grooming, voice, or confidence notes should be considered?")
    if not constraints:
        questions.append("What workplace, consent, safety, privacy, cultural, or personal constraints apply?")
    if not comfort_level:
        questions.append("How comfortable does the user feel in this setting?")
    return questions[:8]


def _warnings(thin_input: bool, unsafe_context: bool, high_stakes_context: bool) -> list[str]:
    warnings = [
        "No contacts, email, calendar, social platforms, DMs, messages, profiles, location, camera, microphone, files, accounts, or external services are accessed.",
        "The response does not send messages, schedule meetings, post publicly, scrape profiles, track people, identify private information, persist records, create tasks, or mutate files.",
        "No social success, elite acceptance, relationship outcome, hiring outcome, reputation verification, or etiquette certification is claimed.",
    ]
    if thin_input:
        warnings.insert(0, "The social or networking input is thin; results are a planning scaffold rather than specific social advice.")
    if unsafe_context:
        warnings.append("Requests involving manipulation, coercion, deception, harassment, stalking, doxxing, impersonation, or evasion are not supported.")
    if high_stakes_context:
        warnings.append("Legal, workplace, harassment, consent, safety, and mental-health concerns may require appropriate human or professional help.")
    return warnings


def _limitations(thin_input: bool, unsafe_context: bool, high_stakes_context: bool) -> list[str]:
    limitations = [
        "Based only on user-provided social goal, setting, people context, event, conversation, networking, presentation, constraint, and comfort notes.",
        "No contacts, email, calendar, social-platform, messaging, location, account, camera, microphone, file, connector, browsing, scraping, posting, scheduling, sending, tracking, persistence, shell execution, or mutation behavior.",
        "No manipulation, coercion, deception, harassment, stalking, doxxing, impersonation, evasion, social outcome guarantee, elite acceptance guarantee, relationship outcome guarantee, hiring outcome guarantee, reputation verification, etiquette certification, production readiness, or security certification claim.",
    ]
    if thin_input:
        limitations.append("Thin input limits specificity until the user supplies concrete setting, people, event, topic, goal, and boundary details.")
    if unsafe_context:
        limitations.append("Unsafe or coercive goals must be reframed into respectful, consent-aware, truthful, and non-invasive communication.")
    if high_stakes_context:
        limitations.append("Legal, workplace, harassment, consent, safety, and mental-health concerns should be confirmed with appropriate human, workplace, legal, safety, or professional support.")
    return limitations
