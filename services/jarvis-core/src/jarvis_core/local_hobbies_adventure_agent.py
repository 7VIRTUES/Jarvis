from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_hobbies_adventure"
STATUS = "local_only"
MODE = "response_only_user_provided_hobbies_adventure_planning"
SUPPORTED_OUTPUT_TYPES = (
    "hobby_plan",
    "adventure_plan",
    "beginner_progression",
    "gear_checklist",
    "safety_checklist",
    "low_cost_activity_plan",
    "weekend_plan",
    "skill_practice_plan",
    "packing_list",
    "comparison",
    "checklist",
    "summary",
)


@dataclass(frozen=True)
class LocalHobbiesAdventureRequest:
    request: str = ""
    prompt_text: str = ""
    output_type: str = "summary"
    hobby_or_activity: str = ""
    experience_level: str = ""
    adventure_goal: str = ""
    available_gear: list[str] = field(default_factory=list)
    budget_level: str = ""
    budget_notes: str = ""
    location_context_if_user_provided: str = ""
    time_available: str = ""
    group_size: str = ""
    transportation_context: str = ""
    risk_tolerance: str = ""
    safety_or_accessibility_notes: str = ""
    constraints_or_notes: str = ""


class LocalHobbiesAdventureAgentService:
    def create_plan(self, request: LocalHobbiesAdventureRequest) -> dict[str, Any]:
        request_text = _clean_text(request.request or request.prompt_text)
        output_type = _normalize_output_type(request.output_type)
        activity = _clean_text(request.hobby_or_activity) or request_text or "hobby or adventure activity"
        experience = _clean_text(request.experience_level)
        goal = _clean_text(request.adventure_goal)
        gear = _clean_list(request.available_gear)
        budget_level = _clean_text(request.budget_level)
        budget_notes = _clean_text(request.budget_notes)
        location = _clean_text(request.location_context_if_user_provided)
        time_available = _clean_text(request.time_available)
        group_size = _clean_text(request.group_size)
        transport = _clean_text(request.transportation_context)
        risk_tolerance = _clean_text(request.risk_tolerance)
        safety_notes = _clean_text(request.safety_or_accessibility_notes)
        constraints = _clean_text(request.constraints_or_notes)
        combined = " ".join([request_text, activity, goal, " ".join(gear), location, transport, risk_tolerance, safety_notes, constraints])
        drone_context = _has_drone_context(combined)
        high_risk_context = _has_high_risk_context(combined)
        thin_input = not any([request_text, experience, goal, gear, budget_level, budget_notes, location, time_available, group_size, transport, risk_tolerance, safety_notes, constraints])

        return {
            "agent_id": AGENT_ID,
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "title": _title(output_type, activity),
            "summary": _summary(output_type, activity, goal, thin_input),
            "assumptions": _assumptions(activity, experience, location, group_size, thin_input),
            "recommended_plan": _recommended_plan(output_type, activity, goal, time_available, group_size, risk_tolerance),
            "skill_steps": _skill_steps(output_type, activity, experience),
            "gear_or_supply_checklist": _gear_checklist(output_type, gear, activity),
            "safety_notes": _safety_notes(drone_context, high_risk_context, safety_notes, location),
            "budget_notes": _budget_guidance(budget_level, budget_notes, gear),
            "timeline": _timeline(output_type, time_available),
            "risk_flags": _risk_flags(drone_context, high_risk_context, transport, constraints),
            "limitations": _limitations(thin_input),
            "follow_up_questions": _follow_up_questions(experience, goal, gear, location, time_available, group_size, transport, risk_tolerance, safety_notes),
            "output_type": output_type,
            "safety": local_hobbies_adventure_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_hobbies_adventure_dashboard_summary()


def local_hobbies_adventure_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Hobbies / Adventure Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/hobbies-adventure/local-plan",
        "outputTypes": list(SUPPORTED_OUTPUT_TYPES),
        "responseOnly": True,
        "manualInputOnly": True,
        "localOnly": True,
        "externalServices": False,
        "connectors": False,
        "oauth": False,
        "accountAccess": False,
        "mapAccess": False,
        "gpsLocationAccess": False,
        "weatherServiceAccess": False,
        "parkSystemAccess": False,
        "droneAppAccess": False,
        "licenseSystemAccess": False,
        "bookingAppAccess": False,
        "storeAccess": False,
        "paymentAccess": False,
        "fileReads": False,
        "fileWrites": False,
        "cameraAccess": False,
        "sensorAccess": False,
        "webBrowsing": False,
        "paidApis": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "booking": False,
        "purchases": False,
        "permitApplication": False,
        "licenseApplication": False,
        "airspaceVerification": False,
        "legalAccessVerification": False,
        "contacting": False,
        "liveSafetyVerification": False,
        "liveLegalVerification": False,
        "mutation": False,
        "certificationClaims": False,
        "limitations": ["hobby, adventure, gear, skill, budget, and safety planning only from user-provided notes"],
    }


def local_hobbies_adventure_safety() -> dict[str, bool]:
    return {key: value for key, value in local_hobbies_adventure_dashboard_summary().items() if isinstance(value, bool)}


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


def _has_drone_context(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in ("drone", "uas", "uav", "airspace", "faa"))


def _has_high_risk_context(text: str) -> bool:
    lowered = text.lower()
    terms = ("cliff", "backcountry", "whitewater", "solo", "winter hike", "weapon", "firearm", "survival", "stunt", "trespass", "poach", "illegal")
    return any(term in lowered for term in terms)


def _title(output_type: str, activity: str) -> str:
    return f"{output_type.replace('_', ' ').title()}: {activity[:80]}"


def _summary(output_type: str, activity: str, goal: str, thin_input: bool) -> str:
    if thin_input:
        return "Local manual hobby and adventure scaffold; add experience, gear, time, location context supplied by the user, and risk constraints for a more specific plan."
    goal_text = f" Goal: {goal}." if goal else ""
    return f"Manual {output_type.replace('_', ' ')} for {activity}.{goal_text} No map, GPS, weather, park, drone, license, booking, store, payment, account, file, camera, sensor, or external service was accessed."


def _assumptions(activity: str, experience: str, location: str, group_size: str, thin_input: bool) -> list[str]:
    assumptions = [f"Uses only user-provided hobby, adventure, gear, location-context, and safety notes for: {activity}."]
    if experience:
        assumptions.append(f"Experience level: {experience}.")
    if location:
        assumptions.append(f"Location context was supplied by the user only: {location}.")
    if group_size:
        assumptions.append(f"Group size: {group_size}.")
    if thin_input:
        assumptions.append("Input is thin; no live conditions, maps, permits, licenses, legal access, bookings, or weather were checked.")
    return assumptions


def _recommended_plan(output_type: str, activity: str, goal: str, time_available: str, group_size: str, risk_tolerance: str) -> list[str]:
    plan = [f"Plan {activity} conservatively using only user-provided context."]
    if output_type == "beginner_progression":
        plan.append("Start with a low-risk practice session, repeat basics, then increase complexity only after comfort improves.")
    elif output_type == "gear_checklist":
        plan.append("Separate required safety gear from nice-to-have gear before considering purchases.")
    elif output_type == "weekend_plan":
        plan.append("Keep the first session simple enough to cancel or shorten if conditions are not right.")
    elif output_type == "skill_practice_plan":
        plan.append("Practice one skill at a time and record observations manually after each session.")
    else:
        plan.append("Prioritize preparation, conservative difficulty, and manual verification of current local rules and conditions.")
    if goal:
        plan.append(f"Use the stated goal as the focus: {goal}.")
    if time_available:
        plan.append(f"Fit the plan into the user-provided time window: {time_available}.")
    if group_size:
        plan.append(f"Scale pace and safety margin for group size: {group_size}.")
    if risk_tolerance:
        plan.append(f"Risk tolerance supplied by user: {risk_tolerance}; use the more conservative interpretation if uncertain.")
    return plan


def _skill_steps(output_type: str, activity: str, experience: str) -> list[str]:
    steps = [f"Define the smallest safe version of {activity}.", "Practice basics before adding distance, speed, height, tools, or remote settings."]
    if experience:
        steps.insert(0, f"Start from experience level: {experience}.")
    if output_type in {"beginner_progression", "skill_practice_plan"}:
        steps.extend(["Repeat a controlled practice block.", "Review what felt unsafe, unclear, or too difficult before the next attempt."])
    return steps


def _gear_checklist(output_type: str, gear: list[str], activity: str) -> list[str]:
    checklist = ["Basic safety item appropriate to the activity", "Water or hydration plan", "Weather-appropriate clothing checked manually", "Communication plan prepared manually"]
    if gear:
        checklist.insert(0, f"Available gear supplied by user: {', '.join(gear[:8])}.")
    if output_type in {"gear_checklist", "packing_list"}:
        checklist.append(f"Activity-specific gear for {activity} should be verified manually before leaving.")
    return checklist


def _safety_notes(drone_context: bool, high_risk_context: bool, safety_notes: str, location: str) -> list[str]:
    notes = ["Verify current local rules, access, weather, closures, hazards, and official safety guidance separately before acting."]
    if location:
        notes.append(f"Location context came from the user only and was not verified: {location}.")
    if safety_notes:
        notes.append(f"User-provided safety or accessibility notes: {safety_notes}.")
    if drone_context:
        notes.append("Drone-related plans require separate manual verification of current FAA rules, local rules, airspace, property rules, privacy expectations, and safe conditions.")
    if high_risk_context:
        notes.append("High-risk signals detected; choose a lower-risk alternative, bring qualified supervision when appropriate, and do not rely on this response for live safety or legal verification.")
    return notes


def _budget_guidance(budget_level: str, budget_notes: str, gear: list[str]) -> list[str]:
    notes = ["Budget guidance is planning-only; no store, payment, purchase, booking, permit, or license action is available."]
    if budget_level:
        notes.append(f"Budget level: {budget_level}.")
    if budget_notes:
        notes.append(f"Budget notes: {budget_notes}.")
    if gear:
        notes.append("Use already available gear when it is safe and appropriate.")
    return notes


def _timeline(output_type: str, time_available: str) -> list[str]:
    timeline = ["Before: verify current rules, access, conditions, and safety requirements manually.", "During: keep the plan reversible and conservative.", "After: capture what to practice next."]
    if time_available:
        timeline.insert(0, f"User-provided time available: {time_available}.")
    if output_type == "weekend_plan":
        timeline.append("Keep a backup indoor or low-risk option ready.")
    return timeline


def _risk_flags(drone_context: bool, high_risk_context: bool, transport: str, constraints: str) -> list[str]:
    flags = ["No live safety, weather, legal access, permit, license, airspace, booking, or condition verification was performed."]
    if drone_context:
        flags.append("Drone context: verify current FAA/local rules, airspace, property rules, and safe conditions separately.")
    if high_risk_context:
        flags.append("High-risk context: avoid illegal trespass, evasion, unsafe stunts, weapon use, poaching, vandalism, or dangerous survival tactics.")
    if transport:
        flags.append(f"Transportation context must be checked manually: {transport}.")
    if constraints:
        flags.append(f"Constraints supplied by user: {constraints}.")
    return flags


def _limitations(thin_input: bool) -> list[str]:
    limitations = [
        "Based only on user-provided notes.",
        "No maps, GPS, location, weather, park systems, drone apps, fishing/license systems, booking apps, stores, payments, accounts, files, camera, sensors, or external services were accessed.",
        "No booking, buying, permit application, license application, airspace verification, legal access verification, contacting, persistence, mutation, live safety verification, or live legal verification is provided.",
    ]
    if thin_input:
        limitations.append("Input is thin, so guidance remains a general local scaffold.")
    return limitations


def _follow_up_questions(experience: str, goal: str, gear: list[str], location: str, time_available: str, group_size: str, transport: str, risk_tolerance: str, safety_notes: str) -> list[str]:
    questions: list[str] = []
    if not experience:
        questions.append("What is the current experience level?")
    if not goal:
        questions.append("What is the hobby or adventure goal?")
    if not gear:
        questions.append("What gear or supplies are already available?")
    if not location:
        questions.append("What location context has the user already verified manually?")
    if not time_available:
        questions.append("How much time is available?")
    if not group_size:
        questions.append("How many people are involved?")
    if not transport:
        questions.append("What transportation constraints matter?")
    if not risk_tolerance:
        questions.append("What risk tolerance should the plan assume?")
    if not safety_notes:
        questions.append("Are there safety or accessibility notes?")
    return questions[:6]
