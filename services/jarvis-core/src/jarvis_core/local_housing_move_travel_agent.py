from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_housing_move_travel_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_housing_move_travel_planning"
SUPPORTED_OUTPUT_TYPES = (
    "move_brief",
    "housing_comparison",
    "move_plan",
    "packing_plan",
    "drive_vs_fly_plan",
    "commute_review",
    "setup_checklist",
    "travel_prep_plan",
)


@dataclass(frozen=True)
class LocalHousingMoveTravelRequest:
    housing_goal: str
    plan_name: str = ""
    destination: str = ""
    timeline: str = ""
    budget_notes: str = ""
    housing_options: list[str] = field(default_factory=list)
    move_items: list[str] = field(default_factory=list)
    transportation_notes: str = ""
    commute_notes: str = ""
    utility_setup_notes: str = ""
    constraints: list[str] = field(default_factory=list)
    priorities: list[str] = field(default_factory=list)
    desired_output_type: str = "move_brief"


class LocalHousingMoveTravelAgentService:
    def create_plan(self, request: LocalHousingMoveTravelRequest) -> dict[str, Any]:
        plan_name = _clean_text(request.plan_name) or "Local housing and move plan"
        destination = _clean_text(request.destination)
        housing_goal = _clean_text(request.housing_goal)
        timeline = _clean_text(request.timeline)
        budget_notes = _clean_text(request.budget_notes)
        housing_options = _clean_list(request.housing_options)
        move_items = _clean_list(request.move_items)
        transportation_notes = _clean_text(request.transportation_notes)
        commute_notes = _clean_text(request.commute_notes)
        utility_setup_notes = _clean_text(request.utility_setup_notes)
        constraints = _clean_list(request.constraints)
        priorities = _clean_list(request.priorities)
        desired_output_type = _normalize_output_type(request.desired_output_type)
        thin_input = _thin_input(
            housing_goal,
            destination,
            timeline,
            budget_notes,
            housing_options,
            move_items,
            transportation_notes,
            commute_notes,
            utility_setup_notes,
            constraints,
            priorities,
        )
        high_stakes_context = _high_stakes_context(
            housing_goal,
            budget_notes,
            housing_options,
            transportation_notes,
            commute_notes,
            utility_setup_notes,
            constraints,
            priorities,
        )

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "planName": plan_name,
            "destination": destination,
            "housingGoal": housing_goal,
            "desiredOutputType": desired_output_type,
            "moveFocus": _move_focus(housing_goal, destination, timeline, desired_output_type, thin_input),
            "housingSummary": _housing_summary(housing_goal, destination, housing_options, priorities, thin_input),
            "housingComparison": _housing_comparison(housing_options, budget_notes, commute_notes, constraints, priorities),
            "movePlan": _move_plan(timeline, move_items, transportation_notes, constraints, priorities),
            "packingPlan": _packing_plan(move_items, timeline, constraints),
            "driveVsFlyPlan": _drive_vs_fly_plan(transportation_notes, budget_notes, timeline, constraints),
            "commuteReview": _commute_review(commute_notes, transportation_notes, destination, priorities, constraints),
            "setupChecklist": _setup_checklist(utility_setup_notes, housing_goal, timeline, constraints),
            "travelPrepPlan": _travel_prep_plan(destination, timeline, transportation_notes, move_items, constraints),
            "budgetNotes": _budget_notes(budget_notes, housing_options, transportation_notes, constraints),
            "nextActions": _next_actions(desired_output_type, thin_input, high_stakes_context),
            "openQuestions": _open_questions(
                destination,
                housing_goal,
                timeline,
                budget_notes,
                housing_options,
                move_items,
                transportation_notes,
                commute_notes,
                utility_setup_notes,
                constraints,
                priorities,
            ),
            "warnings": _warnings(thin_input, high_stakes_context),
            "limitations": _limitations(thin_input, high_stakes_context),
            "safety": local_housing_move_travel_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_housing_move_travel_dashboard_summary()


def local_housing_move_travel_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Housing / Move / Travel Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/housing-move-travel/local-plan",
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
        "mapAccess": False,
        "locationAccess": False,
        "bookingActions": False,
        "leaseActions": False,
        "applicationSubmission": False,
        "paymentActions": False,
        "emailSending": False,
        "calendarAccess": False,
        "contactAccess": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "mutation": False,
        "legalValidation": False,
        "safetyValidation": False,
        "priceAvailabilityValidation": False,
        "certificationClaims": False,
        "limitations": ["based only on user-provided housing, move, commute, setup, and travel inputs"],
    }


def local_housing_move_travel_safety() -> dict[str, bool]:
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
        "mapAccess": False,
        "locationAccess": False,
        "bookingActions": False,
        "leaseActions": False,
        "applicationSubmission": False,
        "paymentActions": False,
        "emailSending": False,
        "calendarAccess": False,
        "contactAccess": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "mutation": False,
        "legalValidation": False,
        "safetyValidation": False,
        "priceAvailabilityValidation": False,
        "certificationClaims": False,
    }


def _normalize_output_type(value: str) -> str:
    normalized = (value or "move_brief").strip().lower()
    return normalized if normalized in SUPPORTED_OUTPUT_TYPES else "move_brief"


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
    housing_goal: str,
    destination: str,
    timeline: str,
    budget_notes: str,
    housing_options: list[str],
    move_items: list[str],
    transportation_notes: str,
    commute_notes: str,
    utility_setup_notes: str,
    constraints: list[str],
    priorities: list[str],
) -> bool:
    return not any(
        [
            housing_goal,
            destination,
            timeline,
            budget_notes,
            housing_options,
            move_items,
            transportation_notes,
            commute_notes,
            utility_setup_notes,
            constraints,
            priorities,
        ]
    )


def _high_stakes_context(
    housing_goal: str,
    budget_notes: str,
    housing_options: list[str],
    transportation_notes: str,
    commute_notes: str,
    utility_setup_notes: str,
    constraints: list[str],
    priorities: list[str],
) -> bool:
    text = " ".join(
        [
            housing_goal,
            budget_notes,
            " ".join(housing_options),
            transportation_notes,
            commute_notes,
            utility_setup_notes,
            " ".join(constraints),
            " ".join(priorities),
        ]
    ).lower()
    terms = (
        "lease",
        "deposit",
        "application",
        "legal",
        "contract",
        "insurance",
        "safety",
        "crime",
        "neighborhood",
        "student housing",
        "school housing",
        "financial aid",
        "roommate agreement",
        "security deposit",
        "hazard",
    )
    return any(term in text for term in terms)


def _move_focus(
    housing_goal: str,
    destination: str,
    timeline: str,
    desired_output_type: str,
    thin_input: bool,
) -> list[str]:
    if thin_input:
        return [
            "Capture the housing or travel goal, destination, timeline, budget notes, and constraints before making decisions.",
            "Keep the result as a manual planning outline because no live listings, maps, booking systems, or accounts are checked.",
        ]
    focus = [
        f"Primary request: {housing_goal}.",
        f"Requested output shape: {desired_output_type}.",
    ]
    if destination:
        focus.append(f"Destination or move area from user input: {destination}.")
    if timeline:
        focus.append(f"Timeline from user input: {timeline}.")
    focus.append("Use the plan as a manual review aid, not as live availability, price, commute, safety, or legal validation.")
    return focus


def _housing_summary(
    housing_goal: str,
    destination: str,
    housing_options: list[str],
    priorities: list[str],
    thin_input: bool,
) -> list[str]:
    if thin_input:
        return ["Housing summary is limited until the user provides a goal, destination, options, and priorities."]
    summary = []
    if housing_goal:
        summary.append(f"Goal: {housing_goal}.")
    if destination:
        summary.append(f"Area to consider manually: {destination}.")
    if housing_options:
        summary.append("User-provided options to compare: " + "; ".join(housing_options) + ".")
    else:
        summary.append("No specific housing options were provided, so collect candidate addresses or descriptions manually.")
    if priorities:
        summary.append("Priority lens: " + "; ".join(priorities) + ".")
    return summary


def _housing_comparison(
    housing_options: list[str],
    budget_notes: str,
    commute_notes: str,
    constraints: list[str],
    priorities: list[str],
) -> list[dict[str, str]]:
    options = housing_options or ["Option A to define manually", "Option B to define manually"]
    comparison: list[dict[str, str]] = []
    for option in options[:6]:
        comparison.append(
            {
                "option": option,
                "budgetFit": budget_notes or "Add rent, deposit, utility, fee, and move-in estimates manually.",
                "commuteFit": commute_notes or "Add commute notes from trusted manual sources; no map or time certainty is checked.",
                "constraintsToCheck": "; ".join(constraints) if constraints else "Review lease terms, move-in rules, access needs, and deal breakers manually.",
                "priorityFit": "; ".join(priorities) if priorities else "Define what matters most before choosing.",
                "manualVerificationNeeded": "Confirm availability, current price, legal terms, safety, insurance, and official requirements with the appropriate source.",
            }
        )
    return comparison


def _move_plan(
    timeline: str,
    move_items: list[str],
    transportation_notes: str,
    constraints: list[str],
    priorities: list[str],
) -> list[str]:
    plan = [
        "List fixed dates, move-in windows, travel dates, pickup/dropoff needs, and handoff responsibilities.",
        "Separate must-move items from optional items, donations, storage, and items to buy after arrival.",
        "Keep documents, medications, keys, chargers, and essential clothing in a carry-with-you bag.",
    ]
    if timeline:
        plan.insert(0, f"Use the user-provided timeline as the manual schedule anchor: {timeline}.")
    if move_items:
        plan.append("Priority items from user input: " + "; ".join(move_items) + ".")
    if transportation_notes:
        plan.append(f"Transportation notes to evaluate manually: {transportation_notes}.")
    if constraints:
        plan.append("Constraints to respect: " + "; ".join(constraints) + ".")
    if priorities:
        plan.append("Priorities to protect: " + "; ".join(priorities) + ".")
    return plan


def _packing_plan(move_items: list[str], timeline: str, constraints: list[str]) -> list[str]:
    plan = [
        "Pack identification, lease or housing paperwork, school or work documents, medications, electronics, chargers, and daily essentials first.",
        "Label boxes by room and urgency so arrival tasks stay clear.",
        "Create a small arrival kit with bedding, toiletries, basic tools, snacks, and cleaning supplies.",
    ]
    if move_items:
        plan.append("User-listed items to account for: " + "; ".join(move_items) + ".")
    if timeline:
        plan.append(f"Stage packing around the stated timeline: {timeline}.")
    if constraints:
        plan.append("Packing constraints to review manually: " + "; ".join(constraints) + ".")
    return plan


def _drive_vs_fly_plan(
    transportation_notes: str,
    budget_notes: str,
    timeline: str,
    constraints: list[str],
) -> list[str]:
    return [
        "Compare total manual cost for driving, flying, shipping, storage, rides, luggage, lodging, food, and local transit.",
        f"Transportation notes: {transportation_notes or 'Add route, baggage, vehicle, pickup, and arrival notes manually.'}",
        f"Budget lens: {budget_notes or 'Add user-estimated prices only; this agent does not verify live fares, rates, or availability.'}",
        f"Schedule lens: {timeline or 'Add dates, arrival deadline, and buffer time manually.'}",
        "Constraint lens: " + ("; ".join(constraints) if constraints else "Review mobility, pets, weather, parking, luggage, storage, and fatigue constraints manually."),
        "Choose only after confirming current prices, availability, rules, and safety through official or trusted sources.",
    ]


def _commute_review(
    commute_notes: str,
    transportation_notes: str,
    destination: str,
    priorities: list[str],
    constraints: list[str],
) -> list[str]:
    review = [
        "Treat commute notes as user-provided estimates only; no map, live transit, traffic, location, or safety validation is performed.",
        f"Destination context: {destination or 'Add campus, workplace, neighborhood, or station targets manually.'}",
        f"Commute notes: {commute_notes or 'Add expected routes, walking distance, transit modes, parking, and backup options manually.'}",
        f"Transportation notes: {transportation_notes or 'Add vehicle, transit pass, rideshare, shuttle, or bicycle assumptions manually.'}",
    ]
    if priorities:
        review.append("Priorities to weigh: " + "; ".join(priorities) + ".")
    if constraints:
        review.append("Constraints to check manually: " + "; ".join(constraints) + ".")
    return review


def _setup_checklist(
    utility_setup_notes: str,
    housing_goal: str,
    timeline: str,
    constraints: list[str],
) -> list[str]:
    checklist = [
        "Confirm move-in instructions, keys, access codes, parking or loading rules, and inspection steps with the official housing source.",
        "Plan utilities, internet, mail forwarding, renter insurance, emergency contacts, and basic supplies manually.",
        "Record lease dates, deposit expectations, payment deadlines, and maintenance contact details in the user's own trusted system.",
    ]
    if utility_setup_notes:
        checklist.append(f"Utility setup notes from user input: {utility_setup_notes}.")
    if housing_goal:
        checklist.append(f"Align setup tasks with the stated housing goal: {housing_goal}.")
    if timeline:
        checklist.append(f"Sequence setup work around: {timeline}.")
    if constraints:
        checklist.append("Setup constraints to confirm: " + "; ".join(constraints) + ".")
    return checklist


def _travel_prep_plan(
    destination: str,
    timeline: str,
    transportation_notes: str,
    move_items: list[str],
    constraints: list[str],
) -> list[str]:
    prep = [
        f"Destination: {destination or 'Add destination manually.'}",
        f"Travel timing: {timeline or 'Add dates, arrival windows, and buffer time manually.'}",
        f"Transportation plan: {transportation_notes or 'Add drive, flight, train, bus, rideshare, parking, or pickup assumptions manually.'}",
        "Keep IDs, confirmations, medication, chargers, essential clothes, housing instructions, and emergency contacts accessible.",
        "Confirm tickets, lodging, rooms, transport rules, and official requirements outside Jarvis before relying on the plan.",
    ]
    if move_items:
        prep.append("Travel-sensitive items from user input: " + "; ".join(move_items) + ".")
    if constraints:
        prep.append("Travel constraints to review: " + "; ".join(constraints) + ".")
    return prep


def _budget_notes(
    budget_notes: str,
    housing_options: list[str],
    transportation_notes: str,
    constraints: list[str],
) -> list[str]:
    notes = [
        budget_notes or "Add rent, deposits, utilities, fees, moving supplies, storage, travel, meals, and emergency buffer estimates manually.",
        "Do not treat this as live price, availability, loan, tax, legal, or financial advice validation.",
    ]
    if housing_options:
        notes.append("Compare each housing option against rent, deposit, utilities, insurance, fees, commute, and setup costs.")
    if transportation_notes:
        notes.append("Include transportation assumptions from user notes when comparing drive, fly, ship, or transit options.")
    if constraints:
        notes.append("Budget constraints to respect: " + "; ".join(constraints) + ".")
    return notes


def _next_actions(desired_output_type: str, thin_input: bool, high_stakes_context: bool) -> list[str]:
    actions = [
        f"Review the {desired_output_type} response and mark which items need official confirmation.",
        "Collect missing manual inputs for destination, dates, options, budget estimates, commute assumptions, utilities, and constraints.",
        "Confirm live availability, prices, travel rules, lease terms, safety, insurance, and official housing requirements outside Jarvis.",
    ]
    if thin_input:
        actions.insert(0, "Add enough manual context before using the plan for a real housing, move, commute, or travel decision.")
    if high_stakes_context:
        actions.append("Ask official sources or qualified professionals to confirm high-stakes housing, legal, school housing, insurance, safety, or financial details.")
    return actions


def _open_questions(
    destination: str,
    housing_goal: str,
    timeline: str,
    budget_notes: str,
    housing_options: list[str],
    move_items: list[str],
    transportation_notes: str,
    commute_notes: str,
    utility_setup_notes: str,
    constraints: list[str],
    priorities: list[str],
) -> list[str]:
    questions = []
    if not housing_goal:
        questions.append("What housing, moving, commute, or travel decision should this plan support?")
    if not destination:
        questions.append("What destination, neighborhood, campus, workplace, or route should be considered manually?")
    if not timeline:
        questions.append("What move-in, travel, lease, school, or work dates shape the plan?")
    if not budget_notes:
        questions.append("What rent, deposit, utilities, move, storage, and travel cost estimates should be used?")
    if not housing_options:
        questions.append("Which housing options should be compared from user-provided notes?")
    if not move_items:
        questions.append("Which belongings, documents, essentials, or special items need move planning?")
    if not transportation_notes:
        questions.append("What drive, flight, train, bus, parking, shipping, or pickup assumptions should be included?")
    if not commute_notes:
        questions.append("What commute assumptions, transit modes, parking notes, and backup routes should be reviewed?")
    if not utility_setup_notes:
        questions.append("What utilities, internet, insurance, mail, and setup tasks need manual confirmation?")
    if not constraints:
        questions.append("What deal breakers, accessibility needs, timing limits, roommate rules, lease rules, or safety concerns apply?")
    if not priorities:
        questions.append("Which priorities matter most: cost, commute, safety, flexibility, space, timing, reliability, or simplicity?")
    return questions[:8]


def _warnings(thin_input: bool, high_stakes_context: bool) -> list[str]:
    warnings = [
        "No maps, live listings, booking platforms, lease systems, payments, email, calendar, contacts, accounts, files, or external services are accessed.",
        "The response does not verify current availability, current prices, neighborhood safety, legal lease terms, official housing approval, travel booking, or commute-time certainty.",
    ]
    if thin_input:
        warnings.insert(0, "The housing, move, or travel input is thin; results are a checklist scaffold rather than a specific recommendation.")
    if high_stakes_context:
        warnings.append("Lease, deposit, legal, safety, insurance, finance, and official school housing details need qualified or official confirmation.")
    return warnings


def _limitations(thin_input: bool, high_stakes_context: bool) -> list[str]:
    limitations = [
        "Based only on user-provided housing, move, commute, setup, and travel notes.",
        "No browsing, listings, maps, location access, booking, applications, lease signing, payments, messaging, scheduling, persistence, file access, or account access.",
        "No live availability, current price, legal lease, neighborhood safety, official housing, travel booking, commute-time, insurance, financial, or certification validation.",
    ]
    if thin_input:
        limitations.append("Thin input limits specificity until the user supplies concrete options, dates, costs, and constraints.")
    if high_stakes_context:
        limitations.append("High-stakes lease, deposit, legal, safety, insurance, school housing, and financial questions should be confirmed with official sources or qualified professionals.")
    return limitations
