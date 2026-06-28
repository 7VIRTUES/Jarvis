from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_culture_taste_high_class_lifestyle"
STATUS = "local_only"
MODE = "response_only_user_provided_culture_taste_high_class_lifestyle_planning"
SUPPORTED_OUTPUT_TYPES = (
    "etiquette_plan",
    "wardrobe_plan",
    "event_prep_plan",
    "dining_prep",
    "conversation_prep",
    "cultural_literacy_plan",
    "taste_development_plan",
    "social_polish_checklist",
    "high_class_lifestyle_plan",
    "comparison",
    "checklist",
    "summary",
)


@dataclass(frozen=True)
class LocalCultureTasteHighClassLifestyleRequest:
    request: str = ""
    prompt_text: str = ""
    output_type: str = "summary"
    situation_or_event: str = ""
    culture_goal: str = ""
    current_style_or_baseline: str = ""
    desired_impression: str = ""
    budget_level: str = ""
    budget_notes: str = ""
    wardrobe_or_items_available: list[str] = field(default_factory=list)
    dining_or_event_context: str = ""
    conversation_context: str = ""
    reading_art_music_film_interests: list[str] = field(default_factory=list)
    etiquette_focus: list[str] = field(default_factory=list)
    timeline: str = ""
    constraints_or_notes: str = ""


class LocalCultureTasteHighClassLifestyleAgentService:
    def create_plan(self, request: LocalCultureTasteHighClassLifestyleRequest) -> dict[str, Any]:
        request_text = _clean_text(request.request or request.prompt_text)
        output_type = _normalize_output_type(request.output_type)
        situation = _clean_text(request.situation_or_event) or request_text or "culture and taste planning request"
        goal = _clean_text(request.culture_goal)
        baseline = _clean_text(request.current_style_or_baseline)
        impression = _clean_text(request.desired_impression)
        budget_level = _clean_text(request.budget_level)
        budget_notes = _clean_text(request.budget_notes)
        items = _clean_list(request.wardrobe_or_items_available)
        dining = _clean_text(request.dining_or_event_context)
        conversation = _clean_text(request.conversation_context)
        interests = _clean_list(request.reading_art_music_film_interests)
        etiquette = _clean_list(request.etiquette_focus)
        timeline = _clean_text(request.timeline)
        constraints = _clean_text(request.constraints_or_notes)
        thin_input = not any([request_text, goal, baseline, impression, budget_level, budget_notes, items, dining, conversation, interests, etiquette, timeline, constraints])
        safety = local_culture_taste_high_class_lifestyle_safety()

        return {
            "agent_id": AGENT_ID,
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "title": _title(output_type, situation),
            "summary": _summary(output_type, situation, goal, thin_input),
            "assumptions": _assumptions(situation, goal, baseline, impression, thin_input),
            "recommended_plan": _recommended_plan(output_type, situation, goal, items, dining, timeline),
            "style_or_taste_guidance": _style_guidance(output_type, baseline, impression, items, interests),
            "etiquette_notes": _etiquette_notes(output_type, etiquette, dining),
            "conversation_notes": _conversation_notes(output_type, conversation, interests),
            "learning_plan": _learning_plan(output_type, interests, goal),
            "checklist": _checklist(output_type, situation, items, etiquette, timeline),
            "budget_notes": _budget_guidance(budget_level, budget_notes),
            "timeline": _timeline(timeline),
            "limitations": _limitations(thin_input),
            "follow_up_questions": _follow_up_questions(goal, baseline, impression, items, dining, conversation, etiquette, timeline),
            "output_type": output_type,
            "safety": safety,
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_culture_taste_high_class_lifestyle_dashboard_summary()


def local_culture_taste_high_class_lifestyle_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Culture / Taste / High-Class Lifestyle Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/culture-taste-high-class-lifestyle/local-plan",
        "outputTypes": list(SUPPORTED_OUTPUT_TYPES),
        "responseOnly": True,
        "manualInputOnly": True,
        "localOnly": True,
        "externalServices": False,
        "connectors": False,
        "oauth": False,
        "accountAccess": False,
        "storeAccess": False,
        "fashionAppAccess": False,
        "reservationAccess": False,
        "restaurantAppAccess": False,
        "mapAccess": False,
        "locationAccess": False,
        "paymentAccess": False,
        "socialAccountAccess": False,
        "calendarAccess": False,
        "contactAccess": False,
        "fileReads": False,
        "fileWrites": False,
        "cameraAccess": False,
        "photoAccess": False,
        "webBrowsing": False,
        "paidApis": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "purchases": False,
        "reservations": False,
        "contacting": False,
        "posting": False,
        "socialAcceptanceGuarantee": False,
        "imageConsultantCertification": False,
        "legalEtiquetteAuthority": False,
        "privateNetworkAccess": False,
        "manipulationOrDeception": False,
        "mutation": False,
        "certificationClaims": False,
        "limitations": ["culture, taste, style, etiquette, and social-polish planning only from user-provided notes"],
    }


def local_culture_taste_high_class_lifestyle_safety() -> dict[str, bool]:
    return {key: value for key, value in local_culture_taste_high_class_lifestyle_dashboard_summary().items() if isinstance(value, bool)}


def _normalize_output_type(value: str) -> str:
    normalized = (value or "summary").strip().lower()
    return normalized if normalized in SUPPORTED_OUTPUT_TYPES else "summary"


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def _clean_list(values: list[str], limit: int = 12) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = _clean_text(value)
        key = item.lower()
        if item and key not in seen:
            cleaned.append(item)
            seen.add(key)
    return cleaned[:limit]


def _title(output_type: str, situation: str) -> str:
    return f"{output_type.replace('_', ' ').title()}: {situation[:80]}"


def _summary(output_type: str, situation: str, goal: str, thin_input: bool) -> str:
    if thin_input:
        return "Local manual culture and taste scaffold; add event, style baseline, budget, etiquette focus, and interests for a more specific plan."
    goal_text = f" Goal: {goal}." if goal else ""
    return f"Manual {output_type.replace('_', ' ')} for {situation}.{goal_text} No store, reservation, restaurant, map, payment, account, social, calendar, contact, file, camera, photo, or external service was accessed."


def _assumptions(situation: str, goal: str, baseline: str, impression: str, thin_input: bool) -> list[str]:
    assumptions = [f"Uses only user-provided culture, taste, etiquette, style, and event notes for: {situation}."]
    if goal:
        assumptions.append(f"Culture or polish goal: {goal}.")
    if baseline:
        assumptions.append(f"Current baseline: {baseline}.")
    if impression:
        assumptions.append(f"Desired impression: {impression}.")
    if thin_input:
        assumptions.append("Input is thin; the plan avoids status guarantees, elite-network claims, and professional certification claims.")
    return assumptions


def _recommended_plan(output_type: str, situation: str, goal: str, items: list[str], dining: str, timeline: str) -> list[str]:
    plan = [f"Prepare for {situation} with a respectful, inclusive, and realistic polish plan."]
    if output_type == "wardrobe_plan":
        plan.append("Start with fit, condition, comfort, and appropriateness before considering new items.")
    elif output_type == "dining_prep":
        plan.append("Review the dining context, pace, host norms, and graceful questions to ask manually.")
    elif output_type == "conversation_prep":
        plan.append("Prepare a few curious, low-pressure conversation threads and avoid prying or performative status signaling.")
    elif output_type == "cultural_literacy_plan":
        plan.append("Choose a small set of books, films, music, or art topics to explore steadily.")
    elif output_type == "event_prep_plan":
        plan.append("Match dress, arrival timing, introductions, conversation, and exit plan to the event context.")
    else:
        plan.append("Balance presentation, manners, curiosity, and comfort without pretending to guarantee social outcomes.")
    if goal:
        plan.append(f"Use the stated goal as the style filter: {goal}.")
    if items:
        plan.append(f"Build from available items first: {', '.join(items[:6])}.")
    if dining:
        plan.append(f"Dining or event context to respect: {dining}.")
    if timeline:
        plan.append(f"Sequence prep around the user-provided timeline: {timeline}.")
    return plan


def _style_guidance(output_type: str, baseline: str, impression: str, items: list[str], interests: list[str]) -> list[str]:
    guidance = ["Favor clean fit, good condition, situational respect, and comfort over labels or status signaling."]
    if baseline:
        guidance.append(f"Improve from current baseline: {baseline}.")
    if impression:
        guidance.append(f"Desired impression filter: {impression}.")
    if items:
        guidance.append(f"Use existing wardrobe or items before any purchase consideration: {', '.join(items[:6])}.")
    if output_type in {"taste_development_plan", "cultural_literacy_plan"} and interests:
        guidance.append(f"Use stated interests as taste anchors: {', '.join(interests[:6])}.")
    return guidance


def _etiquette_notes(output_type: str, etiquette: list[str], dining: str) -> list[str]:
    notes = ["Etiquette guidance is practical and non-authoritative; adapt to the actual host, culture, venue, and local norms."]
    if etiquette:
        notes.append(f"Focus areas: {', '.join(etiquette[:8])}.")
    if dining:
        notes.append(f"For the dining or event context, check expectations manually before relying on this plan: {dining}.")
    if output_type == "social_polish_checklist":
        notes.append("Use inclusive manners: listen well, avoid gatekeeping, and do not rank people by class or status.")
    return notes


def _conversation_notes(output_type: str, conversation: str, interests: list[str]) -> list[str]:
    notes = ["Prepare generous, curious questions and short personal observations; avoid deception, harassment, manipulation, or status-pressure tactics."]
    if conversation:
        notes.append(f"Conversation context: {conversation}.")
    if interests:
        notes.append(f"Possible topics from supplied interests: {', '.join(interests[:8])}.")
    if output_type == "conversation_prep":
        notes.append("Keep backup topics neutral: recent reading, music, food preferences, travel memories supplied by the user, or the event itself.")
    return notes


def _learning_plan(output_type: str, interests: list[str], goal: str) -> list[str]:
    plan = ["Pick one small topic, learn the vocabulary, notice what you genuinely like, and record a few personal observations manually."]
    if interests:
        plan.append(f"Rotate through user-provided culture interests: {', '.join(interests[:8])}.")
    if goal:
        plan.append(f"Connect learning back to the stated goal: {goal}.")
    if output_type in {"cultural_literacy_plan", "taste_development_plan", "high_class_lifestyle_plan"}:
        plan.append("Prefer steady exposure and reflection over pretending expertise.")
    return plan


def _checklist(output_type: str, situation: str, items: list[str], etiquette: list[str], timeline: str) -> list[str]:
    checklist = [
        f"Confirm the situation manually: {situation}.",
        "Choose an outfit or presentation option that is clean, comfortable, and context-appropriate.",
        "Prepare two sincere questions and one graceful exit line.",
    ]
    if items:
        checklist.append(f"Review available items: {', '.join(items[:6])}.")
    if etiquette:
        checklist.append(f"Review etiquette focus areas: {', '.join(etiquette[:6])}.")
    if timeline:
        checklist.append(f"Use the timeline as a reminder only: {timeline}.")
    if output_type == "checklist":
        checklist.append("Do not purchase, reserve, message, post, or contact anyone from this response.")
    return checklist


def _budget_guidance(budget_level: str, budget_notes: str) -> list[str]:
    notes = ["Budget guidance is planning-only; no store, payment, purchase, reservation, or account action is available."]
    if budget_level:
        notes.append(f"Budget level: {budget_level}.")
    if budget_notes:
        notes.append(f"Budget notes: {budget_notes}.")
    notes.append("Use existing items and free learning sources before considering purchases.")
    return notes


def _timeline(timeline: str) -> list[str]:
    steps = ["Now: clarify context and constraints.", "Before the event or practice session: review outfit, etiquette, and conversation notes manually."]
    if timeline:
        steps.insert(0, f"User-provided timeline: {timeline}.")
    return steps


def _limitations(thin_input: bool) -> list[str]:
    limitations = [
        "Based only on user-provided notes.",
        "No stores, fashion apps, reservations, restaurants, maps, location, payments, accounts, social accounts, calendar, contacts, files, camera, photos, or external services were accessed.",
        "No purchases, reservations, contacts, posts, sends, persistence, mutation, social acceptance guarantee, status guarantee, certification claim, legal etiquette authority, or private elite-network access is provided.",
    ]
    if thin_input:
        limitations.append("Input is thin, so guidance remains a general local scaffold.")
    return limitations


def _follow_up_questions(goal: str, baseline: str, impression: str, items: list[str], dining: str, conversation: str, etiquette: list[str], timeline: str) -> list[str]:
    questions: list[str] = []
    if not goal:
        questions.append("What culture, taste, etiquette, or lifestyle outcome should the plan support?")
    if not baseline:
        questions.append("What is the current style, taste, or social baseline?")
    if not impression:
        questions.append("What impression should the plan aim for while staying authentic?")
    if not items:
        questions.append("What wardrobe items or relevant materials are already available?")
    if not dining:
        questions.append("Is there a dining, venue, or event context to consider?")
    if not conversation:
        questions.append("What conversation setting or audience should be prepared for?")
    if not etiquette:
        questions.append("Which etiquette areas feel uncertain?")
    if not timeline:
        questions.append("What timeline should the manual prep follow?")
    return questions[:6]
