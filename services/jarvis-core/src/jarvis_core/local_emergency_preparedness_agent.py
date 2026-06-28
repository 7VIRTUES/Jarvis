from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_emergency_preparedness"
STATUS = "local_only"
MODE = "response_only_user_provided_emergency_preparedness_planning"
SUPPORTED_OUTPUT_TYPES = (
    "go_bag_checklist",
    "emergency_plan",
    "severe_weather_plan",
    "power_outage_plan",
    "car_emergency_kit",
    "evacuation_prep",
    "communication_plan",
    "supply_gap_analysis",
    "pet_preparedness_plan",
    "post_event_checklist",
    "comparison",
    "checklist",
    "summary",
)


@dataclass(frozen=True)
class LocalEmergencyPreparednessRequest:
    request: str = ""
    prompt_text: str = ""
    output_type: str = "summary"
    scenario_type: str = ""
    household_size: str = ""
    pets: list[str] = field(default_factory=list)
    location_context_if_user_provided: str = ""
    current_supplies: list[str] = field(default_factory=list)
    vehicle_or_travel_context: str = ""
    medical_or_accessibility_needs: list[str] = field(default_factory=list)
    budget_level: str = ""
    budget_notes: str = ""
    time_horizon: str = ""
    communication_contacts_summary: str = ""
    constraints_or_notes: str = ""


class LocalEmergencyPreparednessAgentService:
    def create_plan(self, request: LocalEmergencyPreparednessRequest) -> dict[str, Any]:
        request_text = _clean_text(request.request or request.prompt_text)
        output_type = _normalize_output_type(request.output_type)
        scenario = _clean_text(request.scenario_type) or request_text or "preparedness scenario"
        household_size = _clean_text(request.household_size)
        pets = _clean_list(request.pets)
        location_context = _clean_text(request.location_context_if_user_provided)
        supplies = _clean_list(request.current_supplies)
        vehicle_context = _clean_text(request.vehicle_or_travel_context)
        medical_needs = _clean_list(request.medical_or_accessibility_needs)
        budget_level = _clean_text(request.budget_level)
        budget_notes = _clean_text(request.budget_notes)
        time_horizon = _clean_text(request.time_horizon)
        contacts = _clean_text(request.communication_contacts_summary)
        constraints = _clean_text(request.constraints_or_notes)
        combined_text = " ".join(
            [
                request_text,
                scenario,
                household_size,
                " ".join(pets),
                location_context,
                " ".join(supplies),
                vehicle_context,
                " ".join(medical_needs),
                budget_level,
                budget_notes,
                time_horizon,
                contacts,
                constraints,
            ]
        )
        immediate_danger = _has_immediate_danger(combined_text)
        thin_input = not any([request_text, household_size, pets, location_context, supplies, vehicle_context, medical_needs, budget_level, budget_notes, time_horizon, contacts, constraints])

        return {
            "agent_id": AGENT_ID,
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "title": _title(output_type, scenario),
            "summary": _summary(output_type, scenario, household_size, thin_input),
            "assumptions": _assumptions(scenario, household_size, location_context, time_horizon, thin_input),
            "recommended_plan": _recommended_plan(output_type, scenario, supplies, pets, vehicle_context, medical_needs),
            "priority_actions": _priority_actions(output_type, scenario, immediate_danger, supplies, medical_needs),
            "supply_checklist": _supply_checklist(output_type, supplies, pets, vehicle_context, medical_needs),
            "communication_steps": _communication_steps(contacts, output_type),
            "timeline": _timeline(time_horizon, immediate_danger),
            "budget_notes": _budget_notes(budget_level, budget_notes, supplies),
            "safety_notes": _safety_notes(immediate_danger, medical_needs),
            "urgent_warning": _urgent_warning(immediate_danger),
            "limitations": _limitations(thin_input, immediate_danger),
            "follow_up_questions": _follow_up_questions(household_size, pets, location_context, supplies, vehicle_context, medical_needs, budget_level, time_horizon, contacts),
            "output_type": output_type,
            "safety": local_emergency_preparedness_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_emergency_preparedness_dashboard_summary()


def local_emergency_preparedness_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Emergency / Preparedness Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/emergency-preparedness/local-plan",
        "outputTypes": list(SUPPORTED_OUTPUT_TYPES),
        "responseOnly": True,
        "manualInputOnly": True,
        "localOnly": True,
        "externalServices": False,
        "connectors": False,
        "connectorExecution": False,
        "oauth": False,
        "accountAccess": False,
        "emergencyServicesAccess": False,
        "policeFireEmsAccess": False,
        "weatherServiceAccess": False,
        "mapAccess": False,
        "gpsLocationAccess": False,
        "smartDeviceAccess": False,
        "alarmAccess": False,
        "cameraAccess": False,
        "contactAccess": False,
        "fileReads": False,
        "fileWrites": False,
        "paymentAccess": False,
        "webBrowsing": False,
        "paidApis": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "emergencyCalling": False,
        "alertSending": False,
        "familyContact": False,
        "hotelBooking": False,
        "supplyPurchases": False,
        "doorUnlock": False,
        "deviceControl": False,
        "claimSubmission": False,
        "liveHazardDetection": False,
        "officialEmergencyGuidance": False,
        "evacuationOrderAwareness": False,
        "medicalTriageCertainty": False,
        "survivalGuarantee": False,
        "mutation": False,
        "certificationClaims": False,
        "limitations": ["preparedness planning only based on user-provided emergency, household, supply, pet, vehicle, medical/accessibility, budget, and communication notes"],
    }


def local_emergency_preparedness_safety() -> dict[str, bool]:
    return {key: value for key, value in local_emergency_preparedness_dashboard_summary().items() if isinstance(value, bool)}


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


def _has_immediate_danger(text: str) -> bool:
    lowered = text.lower()
    terms = (
        "immediate danger",
        "right now",
        "fire",
        "gas leak",
        "carbon monoxide",
        "active violence",
        "severe injury",
        "medical emergency",
        "flooding with electrical",
        "electrical risk",
        "trapped",
        "can't breathe",
        "cannot breathe",
    )
    return any(term in lowered for term in terms)


def _title(output_type: str, scenario: str) -> str:
    return f"{output_type.replace('_', ' ').title()}: {scenario[:80]}"


def _summary(output_type: str, scenario: str, household_size: str, thin_input: bool) -> str:
    if thin_input:
        return "Local manual preparedness scaffold; add household size, supplies, constraints, and contacts for more specific planning."
    household = f" Household size: {household_size}." if household_size else ""
    return f"Manual {output_type.replace('_', ' ')} for {scenario}.{household} No emergency service, weather, map, GPS, contact, file, account, device, payment, or external service was accessed."


def _assumptions(scenario: str, household_size: str, location_context: str, time_horizon: str, thin_input: bool) -> list[str]:
    assumptions = [f"Uses only user-provided preparedness notes for: {scenario}."]
    if household_size:
        assumptions.append(f"Household size: {household_size}.")
    if location_context:
        assumptions.append(f"Location context was supplied by the user only: {location_context}.")
    if time_horizon:
        assumptions.append(f"Time horizon: {time_horizon}.")
    if thin_input:
        assumptions.append("Input is thin; no live hazards, weather, maps, GPS, accounts, contacts, or official alerts were checked.")
    return assumptions


def _recommended_plan(output_type: str, scenario: str, supplies: list[str], pets: list[str], vehicle_context: str, medical_needs: list[str]) -> list[str]:
    plan = [f"Prepare manually for: {scenario}."]
    if output_type == "go_bag_checklist":
        plan.append("Prioritize water, food, light, first aid, hygiene, documents to gather manually, chargers, clothing, and cash if appropriate.")
    elif output_type == "power_outage_plan":
        plan.append("Prioritize lighting, charging, fridge/freezer decisions, heat/cooling safety, and communication.")
    elif output_type == "car_emergency_kit":
        plan.append("Prioritize vehicle-safe supplies, warmth, visibility, basic tools, water, and manual route planning.")
    elif output_type == "evacuation_prep":
        plan.append("Identify documents, essentials, pets, transport, and destination options manually without map or hotel booking.")
    else:
        plan.append("Start with highest-impact gaps before buying or storing extra supplies.")
    if supplies:
        plan.append(f"Current supply to account for: {supplies[0]}.")
    if pets:
        plan.append(f"Include pet need: {pets[0]}.")
    if vehicle_context:
        plan.append(f"Vehicle/travel context: {vehicle_context}.")
    if medical_needs:
        plan.append("Medical/accessibility needs require conservative planning and qualified help where needed.")
    return plan[:7]


def _priority_actions(output_type: str, scenario: str, immediate_danger: bool, supplies: list[str], medical_needs: list[str]) -> list[str]:
    actions = []
    if immediate_danger:
        actions.append("If there is immediate danger, contact local emergency services or leave the area if safe to do so.")
    actions.append(f"Pick the smallest useful first step for {scenario}.")
    if not supplies:
        actions.append("List current supplies before identifying gaps.")
    if medical_needs:
        actions.append("Plan around medical/accessibility needs and qualified support.")
    actions.append(f"Use this as manual {output_type} support only; no alerts, calls, bookings, purchases, claims, or device actions were performed.")
    return actions


def _supply_checklist(output_type: str, supplies: list[str], pets: list[str], vehicle_context: str, medical_needs: list[str]) -> dict[str, list[str]]:
    base = supplies[:8] or ["Water", "Shelf-stable food", "Flashlight", "Batteries or charger", "First aid basics", "Hygiene items", "Weather-appropriate clothing"]
    return {
        "current_supplies": supplies[:8] or ["No current supplies were provided."],
        "starter_gaps_to_review": base,
        "pet_items": [f"Pet need: {item}." for item in pets[:5]] or ["Add pet food, water, leash/carrier, medication, and comfort items if pets are included."],
        "vehicle_or_travel": [vehicle_context] if vehicle_context else ["Add vehicle/travel context if this is for driving, evacuation, or commuting."],
        "medical_or_accessibility": medical_needs[:6] or ["Add medication, device, mobility, sensory, or accessibility needs if relevant."],
        "output_focus": [output_type],
    }


def _communication_steps(contacts: str, output_type: str) -> list[str]:
    steps = [
        "Write contact names and numbers manually outside Jarvis if useful.",
        "Choose a check-in plan and backup meeting point manually.",
        "Do not rely on Jarvis to contact anyone or send alerts.",
    ]
    if contacts:
        steps.insert(0, f"User-provided contact summary: {contacts}.")
    if output_type == "communication_plan":
        steps.append("Decide what message template a human might send, but do not send it from Jarvis.")
    return steps


def _timeline(time_horizon: str, immediate_danger: bool) -> list[str]:
    timeline = []
    if immediate_danger:
        timeline.append("Immediate danger overrides planning; use local emergency services or leave if safe.")
    if time_horizon:
        timeline.append(f"Time horizon: {time_horizon}.")
    timeline.append("Use a staged manual plan: now, this week, and later.")
    return timeline


def _budget_notes(budget_level: str, budget_notes: str, supplies: list[str]) -> list[str]:
    notes = []
    if budget_level:
        notes.append(f"Budget level: {budget_level}.")
    if budget_notes:
        notes.append(f"Budget note: {budget_notes}.")
    if supplies:
        notes.append("Use current supplies before buying more.")
    notes.append("No supplies were purchased and no payment system was accessed.")
    return notes


def _safety_notes(immediate_danger: bool, medical_needs: list[str]) -> list[str]:
    notes = [
        "This is preparedness planning only, not real-time emergency awareness or official guidance.",
        "For immediate danger, contact local emergency services or leave the area if safe to do so.",
    ]
    if medical_needs:
        notes.append("Medical or accessibility needs may require qualified medical, local emergency, or care-team guidance.")
    if immediate_danger:
        notes.append("Medical emergencies, fire, gas leak, active violence, carbon monoxide symptoms, flooding with electrical risk, or severe injury require immediate professional or emergency-service help.")
    notes.append("No hazard detection, evacuation-order awareness, emergency call, alert, contact action, booking, purchase, claim submission, device control, or survival guarantee is provided.")
    return notes


def _urgent_warning(immediate_danger: bool) -> str:
    if immediate_danger:
        return "Immediate danger language was detected. Contact local emergency services or leave the area if safe to do so; do not wait for Jarvis."
    return "No immediate danger was detected from the user-provided text; Jarvis has no live emergency awareness."


def _limitations(thin_input: bool, immediate_danger: bool) -> list[str]:
    limitations = [
        "Based only on user-provided emergency, household, supply, pet, vehicle, medical/accessibility, budget, and communication notes.",
        "No emergency services, police/fire/EMS, weather service, map, GPS/location, smart device, alarm, camera, contact, file, account, payment system, connector, or external service was accessed or changed.",
        "No 911 call, alert, family contact, hotel booking, supply purchase, door unlock, device control, claim submission, file mutation, or persistent record was created.",
        "No live hazard detection, official emergency guidance, evacuation-order awareness, medical triage certainty, survival guarantee, or certification claim is provided.",
    ]
    if thin_input:
        limitations.append("Thin input limits specificity; add scenario, household size, pets, supplies, vehicle context, medical/accessibility needs, budget, time horizon, and communication context.")
    if immediate_danger:
        limitations.append("Immediate danger requires local emergency services or leaving the area if safe; this response cannot replace emergency help.")
    return limitations


def _follow_up_questions(
    household_size: str,
    pets: list[str],
    location_context: str,
    supplies: list[str],
    vehicle_context: str,
    medical_needs: list[str],
    budget_level: str,
    time_horizon: str,
    contacts: str,
) -> list[str]:
    questions = []
    if not household_size:
        questions.append("How many people should the plan cover?")
    if not pets:
        questions.append("Are pets included?")
    if not location_context:
        questions.append("What location context did the user provide, if any?")
    if not supplies:
        questions.append("What supplies are already available?")
    if not vehicle_context:
        questions.append("Is a vehicle or travel context relevant?")
    if not medical_needs:
        questions.append("Are there medical or accessibility needs?")
    if not budget_level:
        questions.append("What budget level should shape the plan?")
    if not time_horizon:
        questions.append("What time horizon should the plan cover?")
    if not contacts:
        questions.append("What communication/contact summary should be considered?")
    return questions[:8]
