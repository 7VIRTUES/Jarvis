from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_home_room_living_space"
STATUS = "local_only"
MODE = "response_only_user_provided_home_room_living_space_planning"
SUPPORTED_OUTPUT_TYPES = (
    "room_setup_plan",
    "cleaning_plan",
    "storage_plan",
    "furniture_layout",
    "move_in_plan",
    "maintenance_checklist",
    "small_space_plan",
    "comfort_upgrade_plan",
    "study_or_work_zone_plan",
    "comparison",
    "checklist",
    "summary",
)


@dataclass(frozen=True)
class LocalHomeRoomLivingSpaceRequest:
    request: str = ""
    prompt_text: str = ""
    output_type: str = "summary"
    room_type: str = ""
    living_situation: str = ""
    space_goal: str = ""
    current_items: list[str] = field(default_factory=list)
    items_to_buy_or_consider: list[str] = field(default_factory=list)
    budget_level: str = ""
    budget_notes: str = ""
    room_dimensions_or_constraints: str = ""
    storage_constraints: str = ""
    cleaning_or_maintenance_needs: list[str] = field(default_factory=list)
    aesthetic_preferences: list[str] = field(default_factory=list)
    productivity_or_sleep_goals: list[str] = field(default_factory=list)
    safety_or_accessibility_notes: str = ""
    timeline: str = ""
    constraints_or_notes: str = ""


class LocalHomeRoomLivingSpaceAgentService:
    def create_plan(self, request: LocalHomeRoomLivingSpaceRequest) -> dict[str, Any]:
        request_text = _clean_text(request.request or request.prompt_text)
        output_type = _normalize_output_type(request.output_type)
        room_type = _clean_text(request.room_type) or "living space"
        living_situation = _clean_text(request.living_situation)
        space_goal = _clean_text(request.space_goal) or request_text or "Untitled room setup goal"
        current_items = _clean_list(request.current_items)
        possible_items = _clean_list(request.items_to_buy_or_consider)
        cleaning_needs = _clean_list(request.cleaning_or_maintenance_needs)
        aesthetics = _clean_list(request.aesthetic_preferences)
        productivity_goals = _clean_list(request.productivity_or_sleep_goals)
        budget_level = _clean_text(request.budget_level)
        budget_notes = _clean_text(request.budget_notes)
        dimensions = _clean_text(request.room_dimensions_or_constraints)
        storage = _clean_text(request.storage_constraints)
        safety_notes_input = _clean_text(request.safety_or_accessibility_notes)
        timeline = _clean_text(request.timeline)
        constraints = _clean_text(request.constraints_or_notes)
        combined_text = " ".join(
            [
                request_text,
                room_type,
                living_situation,
                space_goal,
                " ".join(current_items),
                " ".join(possible_items),
                budget_level,
                budget_notes,
                dimensions,
                storage,
                " ".join(cleaning_needs),
                " ".join(aesthetics),
                " ".join(productivity_goals),
                safety_notes_input,
                timeline,
                constraints,
            ]
        )
        urgent_safety = _has_home_safety_context(combined_text)
        thin_input = not any(
            [
                request_text,
                living_situation,
                current_items,
                possible_items,
                budget_level,
                budget_notes,
                dimensions,
                storage,
                cleaning_needs,
                aesthetics,
                productivity_goals,
                safety_notes_input,
                timeline,
                constraints,
            ]
        )

        return {
            "agent_id": AGENT_ID,
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "title": _title(output_type, room_type, space_goal),
            "summary": _summary(output_type, room_type, space_goal, thin_input),
            "assumptions": _assumptions(room_type, living_situation, dimensions, storage, thin_input),
            "recommended_plan": _recommended_plan(output_type, room_type, space_goal, current_items, possible_items, timeline),
            "room_zones": _room_zones(output_type, room_type, productivity_goals, storage, aesthetics),
            "item_suggestions": _item_suggestions(current_items, possible_items, budget_level),
            "step_by_step": _step_by_step(output_type, room_type, space_goal, cleaning_needs, safety_notes_input),
            "checklist": _checklist(output_type, current_items, possible_items, cleaning_needs, productivity_goals),
            "budget_notes": _budget_notes(budget_level, budget_notes, current_items, possible_items),
            "timeline": _timeline(timeline, output_type),
            "safety_notes": _safety_notes(safety_notes_input, urgent_safety),
            "limitations": _limitations(thin_input, urgent_safety),
            "follow_up_questions": _follow_up_questions(
                current_items,
                possible_items,
                budget_level,
                dimensions,
                storage,
                cleaning_needs,
                aesthetics,
                productivity_goals,
                timeline,
            ),
            "output_type": output_type,
            "safety": local_home_room_living_space_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_home_room_living_space_dashboard_summary()


def local_home_room_living_space_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Home / Room / Living Space Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/home-room-living-space/local-plan",
        "outputTypes": list(SUPPORTED_OUTPUT_TYPES),
        "responseOnly": True,
        "manualInputOnly": True,
        "localOnly": True,
        "externalServices": False,
        "connectors": False,
        "connectorExecution": False,
        "oauth": False,
        "accountAccess": False,
        "smartHomeAccess": False,
        "landlordPortalAccess": False,
        "utilityAccountAccess": False,
        "storeAccess": False,
        "paymentAccess": False,
        "locationAccess": False,
        "mapAccess": False,
        "cameraAccess": False,
        "sensorAccess": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "purchases": False,
        "bookings": False,
        "landlordContact": False,
        "maintenanceRequests": False,
        "deviceControl": False,
        "buildingCodeCompliance": False,
        "professionalInspection": False,
        "electricalPlumbingCertification": False,
        "pestControlCertification": False,
        "legalHabitabilityDetermination": False,
        "mutation": False,
        "certificationClaims": False,
        "limitations": ["based only on user-provided room, home, cleaning, storage, furniture, budget, and safety notes"],
    }


def local_home_room_living_space_safety() -> dict[str, bool]:
    return {key: value for key, value in local_home_room_living_space_dashboard_summary().items() if isinstance(value, bool)}


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


def _has_home_safety_context(text: str) -> bool:
    lowered = text.lower()
    terms = ("mold", "gas smell", "exposed wiring", "fire risk", "flood", "flooding", "break-in", "break in", "medical safety", "pest", "sparking", "carbon monoxide")
    return any(term in lowered for term in terms)


def _title(output_type: str, room_type: str, goal: str) -> str:
    return f"{output_type.replace('_', ' ').title()} for {room_type}: {goal[:70]}"


def _summary(output_type: str, room_type: str, goal: str, thin_input: bool) -> str:
    if thin_input:
        return "Local manual living-space planning scaffold; add room constraints, items, budget, storage, and safety notes for a more specific plan."
    return f"Manual {output_type.replace('_', ' ')} for {room_type}: {goal}. No smart-home, landlord portal, store, payment, file, sensor, or external service was accessed."


def _assumptions(room_type: str, living_situation: str, dimensions: str, storage: str, thin_input: bool) -> list[str]:
    assumptions = [f"Uses only user-provided notes for the {room_type}."]
    if living_situation:
        assumptions.append(f"Living situation: {living_situation}.")
    if dimensions:
        assumptions.append(f"Space constraint: {dimensions}.")
    if storage:
        assumptions.append(f"Storage constraint: {storage}.")
    if thin_input:
        assumptions.append("Context is thin; measurements, photos, sensors, landlord systems, stores, and files were not accessed.")
    return assumptions


def _recommended_plan(output_type: str, room_type: str, goal: str, current_items: list[str], possible_items: list[str], timeline: str) -> list[str]:
    plan = [f"Define the main use of the {room_type}: {goal}."]
    if output_type == "cleaning_plan":
        plan.append("Split cleaning into reset, recurring, and occasional maintenance passes.")
    elif output_type == "storage_plan":
        plan.append("Group items by frequency of use before buying more storage.")
    elif output_type == "furniture_layout":
        plan.append("Keep walking paths, outlets, doors, windows, and sleep/work zones clear.")
    elif output_type == "move_in_plan":
        plan.append("Handle essentials first: sleep, light, laundry, desk/work surface, and basic cleaning.")
    elif output_type == "maintenance_checklist":
        plan.append("List issues for human review without submitting landlord or utility requests.")
    else:
        plan.append("Start with items already owned before considering new purchases.")
    if current_items:
        plan.append(f"Anchor around current item: {current_items[0]}.")
    if possible_items:
        plan.append(f"Review optional item manually: {possible_items[0]}.")
    if timeline:
        plan.append(f"Timeline note: {timeline}.")
    return plan[:6]


def _room_zones(output_type: str, room_type: str, productivity_goals: list[str], storage: str, aesthetics: list[str]) -> dict[str, list[str]]:
    return {
        "sleep_or_rest": ["Keep rest area simple, accessible, and visually calm."],
        "study_or_work": productivity_goals[:4] or ["Define one clear work/study surface if the room needs productivity support."],
        "storage": [storage] if storage else ["Use vertical, under-bed, closet, or labeled-zone storage only if it fits the actual space."],
        "movement_or_access": ["Keep doorways, paths, outlets, vents, and emergency exits unobstructed."],
        "comfort_or_style": aesthetics[:4] or [f"Choose comfort upgrades that fit the {room_type} and budget."],
        "output_focus": [output_type],
    }


def _item_suggestions(current_items: list[str], possible_items: list[str], budget_level: str) -> dict[str, list[str]]:
    return {
        "reuse_first": current_items[:8] or ["List current furniture, storage, bedding, lighting, and cleaning supplies before buying anything."],
        "consider_later": possible_items[:8] or ["Only consider new items after confirming room measurements, budget, and actual needs."],
        "low_cost_options": ["Declutter first", "Rearrange zones", "Use bins or labels", "Improve lighting", "Use multi-purpose furniture"],
        "budget_level": [budget_level or "No budget level was provided."],
    }


def _step_by_step(output_type: str, room_type: str, goal: str, cleaning_needs: list[str], safety_notes_input: str) -> list[str]:
    steps = [
        f"Restate the {room_type} goal: {goal}.",
        "Clear floor paths and identify fixed constraints before moving items.",
        "Sort current items into keep, relocate, repair/review, and consider-later groups.",
    ]
    if output_type in {"cleaning_plan", "maintenance_checklist"} or cleaning_needs:
        steps.append(f"Start with maintenance need: {cleaning_needs[0]}." if cleaning_needs else "Make a short recurring cleaning checklist.")
    if safety_notes_input:
        steps.append(f"Treat safety/accessibility note conservatively: {safety_notes_input}.")
    steps.append("No device, portal, store, payment, booking, request, file, or record was changed.")
    return steps


def _checklist(output_type: str, current_items: list[str], possible_items: list[str], cleaning_needs: list[str], productivity_goals: list[str]) -> list[str]:
    checklist = ["Confirm room purpose.", "Check walking paths.", "Check storage friction.", "Review lighting and comfort."]
    checklist.extend([f"Use current item: {item}." for item in current_items[:3]])
    checklist.extend([f"Consider later: {item}." for item in possible_items[:2]])
    checklist.extend([f"Cleaning/maintenance: {item}." for item in cleaning_needs[:2]])
    checklist.extend([f"Productivity/sleep goal: {item}." for item in productivity_goals[:2]])
    checklist.append(f"Keep checklist manual for {output_type}.")
    return checklist[:10]


def _budget_notes(budget_level: str, budget_notes: str, current_items: list[str], possible_items: list[str]) -> list[str]:
    notes = []
    if budget_level:
        notes.append(f"Budget level: {budget_level}.")
    if budget_notes:
        notes.append(f"Budget note: {budget_notes}.")
    if current_items:
        notes.append("Use current items before spending.")
    if possible_items:
        notes.append("Treat possible purchases as optional manual considerations, not actions.")
    return notes or ["No budget details were supplied; start with free layout, cleaning, storage, and comfort changes."]


def _timeline(timeline: str, output_type: str) -> list[str]:
    if timeline:
        return [f"User-provided timeline: {timeline}.", "Sequence essentials before optional upgrades."]
    return [f"No timeline was supplied for the {output_type}; use a short manual first pass before adding detail."]


def _safety_notes(safety_notes_input: str, urgent_safety: bool) -> list[str]:
    notes = ["Keep exits, walking paths, vents, outlets, cords, heat sources, and heavy furniture risks in mind."]
    if safety_notes_input:
        notes.append(f"User safety/accessibility note: {safety_notes_input}.")
    if urgent_safety:
        notes.append("Mold, gas smell, exposed wiring, fire risk, flooding, break-ins, pests, carbon monoxide concerns, or medical safety issues require qualified local professionals or emergency services where appropriate.")
    notes.append("This response does not certify building-code compliance, inspection safety, pest control, electrical/plumbing safety, or habitability.")
    return notes


def _limitations(thin_input: bool, urgent_safety: bool) -> list[str]:
    limitations = [
        "Based only on user-provided room, home, cleaning, storage, furniture, budget, and safety notes.",
        "No smart-home device, landlord portal, utility account, map, location, store, payment system, file, camera, sensor, account, connector, or external service was accessed or changed.",
        "No furniture purchase, mover booking, landlord contact, maintenance request, door unlock, device control, file mutation, or persistent record was created.",
        "No building-code compliance, professional inspection, electrical/plumbing safety certification, pest-control certification, legal habitability determination, or certification claim is provided.",
    ]
    if thin_input:
        limitations.append("Thin input limits specificity; add room type, current items, dimensions, storage constraints, budget, cleaning needs, preferences, and timeline.")
    if urgent_safety:
        limitations.append("Safety-sensitive home issues require qualified local professionals, landlord/emergency processes, or emergency services as appropriate.")
    return limitations


def _follow_up_questions(
    current_items: list[str],
    possible_items: list[str],
    budget_level: str,
    dimensions: str,
    storage: str,
    cleaning_needs: list[str],
    aesthetics: list[str],
    productivity_goals: list[str],
    timeline: str,
) -> list[str]:
    questions = []
    if not current_items:
        questions.append("What items are already in the room?")
    if not possible_items:
        questions.append("What items are being considered, if any?")
    if not budget_level:
        questions.append("What budget level should shape the plan?")
    if not dimensions:
        questions.append("What dimensions or fixed constraints matter?")
    if not storage:
        questions.append("What storage problems need solving?")
    if not cleaning_needs:
        questions.append("What cleaning or maintenance needs should be included?")
    if not aesthetics:
        questions.append("What style or comfort preferences matter?")
    if not productivity_goals:
        questions.append("Are sleep, study, work, or exercise zones needed?")
    if not timeline:
        questions.append("What timeline should the setup use?")
    return questions[:8]
