from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_everyday_life_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_everyday_life_planning"
SUPPORTED_OUTPUT_TYPES = (
    "life_brief",
    "daily_plan",
    "weekly_plan",
    "routine_plan",
    "errand_plan",
    "household_plan",
    "preparation_checklist",
    "priority_review",
)


@dataclass(frozen=True)
class LocalEverydayLifeRequest:
    situation: str
    life_area: str = ""
    goals: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    schedule_notes: str = ""
    household_notes: str = ""
    errands: list[str] = field(default_factory=list)
    people_involved: list[str] = field(default_factory=list)
    resources: list[str] = field(default_factory=list)
    energy_notes: str = ""
    budget_notes: str = ""
    desired_output_type: str = "life_brief"


class LocalEverydayLifeAgentService:
    def create_plan(self, request: LocalEverydayLifeRequest) -> dict[str, Any]:
        life_area = _clean_text(request.life_area) or "Everyday life"
        situation = _clean_text(request.situation) or "Untitled everyday-life situation"
        goals = _clean_list(request.goals)
        constraints = _clean_list(request.constraints)
        schedule_notes = _clean_text(request.schedule_notes)
        household_notes = _clean_text(request.household_notes)
        errands = _clean_list(request.errands)
        people_involved = _clean_list(request.people_involved)
        resources = _clean_list(request.resources)
        energy_notes = _clean_text(request.energy_notes)
        budget_notes = _clean_text(request.budget_notes)
        desired_output_type = _normalize_output_type(request.desired_output_type)
        high_stakes = _looks_high_stakes(
            situation,
            life_area,
            " ".join(goals),
            " ".join(constraints),
            household_notes,
            energy_notes,
            budget_notes,
        )
        thin_input = _thin_input(
            goals,
            constraints,
            schedule_notes,
            household_notes,
            errands,
            people_involved,
            resources,
            energy_notes,
            budget_notes,
        )

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "lifeArea": life_area,
            "situation": situation,
            "desiredOutputType": desired_output_type,
            "lifeFocus": _life_focus(life_area, situation, desired_output_type, goals, thin_input, high_stakes),
            "situationSummary": _situation_summary(situation, household_notes, people_involved, resources, thin_input),
            "prioritySummary": _priority_summary(goals, constraints, energy_notes, budget_notes, high_stakes),
            "dailyPlan": _daily_plan(goals, constraints, schedule_notes, energy_notes, thin_input),
            "weeklyPlan": _weekly_plan(goals, errands, household_notes, constraints),
            "routinePlan": _routine_plan(life_area, goals, schedule_notes, energy_notes),
            "errandPlan": _errand_plan(errands, constraints, resources, budget_notes),
            "householdPlan": _household_plan(household_notes, people_involved, resources, constraints),
            "preparationChecklist": _preparation_checklist(situation, goals, errands, resources, constraints, high_stakes),
            "nextActions": _next_actions(desired_output_type, thin_input, high_stakes),
            "openQuestions": _open_questions(goals, constraints, schedule_notes, household_notes, errands, people_involved, resources, energy_notes, budget_notes),
            "warnings": _warnings(thin_input, high_stakes),
            "limitations": _limitations(thin_input, high_stakes),
            "safety": local_everyday_life_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_everyday_life_dashboard_summary()


def local_everyday_life_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Everyday Life Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/everyday-life/local-plan",
        "outputTypes": list(SUPPORTED_OUTPUT_TYPES),
        "responseOnly": True,
        "manualInputOnly": True,
        "localOnly": True,
        "externalServices": False,
        "connectors": False,
        "oauth": False,
        "accountAccess": False,
        "webBrowsing": False,
        "paidApis": False,
        "calendarAccess": False,
        "emailSending": False,
        "publicPosting": False,
        "purchases": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "smartHomeControl": False,
        "locationAccess": False,
        "mutation": False,
        "certificationClaims": False,
        "limitations": ["based only on user-provided everyday-life planning inputs"],
    }


def local_everyday_life_safety() -> dict[str, bool]:
    return {
        "localOnly": True,
        "responseOnly": True,
        "manualInputOnly": True,
        "externalServices": False,
        "connectors": False,
        "oauth": False,
        "accountAccess": False,
        "webBrowsing": False,
        "paidApis": False,
        "calendarAccess": False,
        "emailSending": False,
        "publicPosting": False,
        "purchases": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "smartHomeControl": False,
        "locationAccess": False,
        "mutation": False,
        "certificationClaims": False,
    }


def _normalize_output_type(value: str) -> str:
    normalized = (value or "life_brief").strip().lower()
    return normalized if normalized in SUPPORTED_OUTPUT_TYPES else "life_brief"


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
    goals: list[str],
    constraints: list[str],
    schedule_notes: str,
    household_notes: str,
    errands: list[str],
    people_involved: list[str],
    resources: list[str],
    energy_notes: str,
    budget_notes: str,
) -> bool:
    return not any([goals, constraints, schedule_notes, household_notes, errands, people_involved, resources, energy_notes, budget_notes])


def _looks_high_stakes(*values: str) -> bool:
    text = " ".join(values).lower()
    terms = (
        "emergency",
        "urgent",
        "unsafe",
        "danger",
        "eviction",
        "legal",
        "court",
        "medical",
        "medicine",
        "injury",
        "safety",
        "financial crisis",
        "debt",
        "violence",
        "abuse",
        "fire",
        "flood",
        "gas leak",
    )
    return any(term in text for term in terms)


def _life_focus(life_area: str, situation: str, desired_output_type: str, goals: list[str], thin_input: bool, high_stakes: bool) -> str:
    if high_stakes:
        return "Frame the situation as manual planning support only, with appropriate human or professional help for high-stakes concerns."
    if thin_input:
        return f"Clarify a practical everyday-life plan for: {situation}."
    if desired_output_type == "daily_plan":
        return f"Turn {life_area} into a simple manual daily plan."
    if desired_output_type == "weekly_plan":
        return f"Group {life_area} into a lightweight weekly planning outline."
    if desired_output_type == "routine_plan":
        return f"Shape {life_area} into a repeatable routine suggestion."
    if desired_output_type == "errand_plan":
        return "Organize user-provided errands into a manual route-free errand plan."
    if desired_output_type == "household_plan":
        return "Organize household notes, people, and resources into a manual coordination plan."
    if desired_output_type == "preparation_checklist":
        return "Create a non-persistent preparation checklist from the supplied situation."
    if desired_output_type == "priority_review":
        return "Review simple priorities without claiming completion or execution."
    if goals:
        return f"Start with the first stated goal: {goals[0]}."
    return f"Create a response-only everyday-life brief for {life_area}."


def _situation_summary(situation: str, household_notes: str, people_involved: list[str], resources: list[str], thin_input: bool) -> list[str]:
    summary = ["Summary is based only on user-provided everyday-life inputs.", f"Situation: {situation}."]
    if household_notes:
        summary.append(f"Household note: {household_notes}.")
    if people_involved:
        summary.append(f"People involved: {', '.join(people_involved[:4])}.")
    if resources:
        summary.append(f"Available resource: {resources[0]}.")
    if thin_input:
        summary.append("Context is thin; add goals, constraints, timing, people, resources, energy, budget, or errand details for a more useful plan.")
    return summary


def _priority_summary(goals: list[str], constraints: list[str], energy_notes: str, budget_notes: str, high_stakes: bool) -> list[str]:
    priorities = []
    if goals:
        priorities.append(f"Primary goal to consider first: {goals[0]}.")
    else:
        priorities.append("No explicit goal was provided; choose one small useful outcome.")
    if constraints:
        priorities.append(f"Constraint to respect: {constraints[0]}.")
    if energy_notes:
        priorities.append(f"Energy note: {energy_notes}.")
    if budget_notes:
        priorities.append(f"Budget note: {budget_notes}.")
    if high_stakes:
        priorities.append("High-stakes wording detected; use human, professional, emergency, or local authority help as appropriate.")
    return priorities


def _daily_plan(goals: list[str], constraints: list[str], schedule_notes: str, energy_notes: str, thin_input: bool) -> list[str]:
    plan = [
        "Pick one must-do item, one useful optional item, and one reset point.",
        f"Use the first stated goal as the daily anchor: {goals[0]}." if goals else "Define one clear daily anchor before adding detail.",
    ]
    if schedule_notes:
        plan.append(f"Use schedule notes as manual context only: {schedule_notes}.")
    if energy_notes:
        plan.append(f"Scale the day around energy context: {energy_notes}.")
    if constraints:
        plan.append(f"Check the day against constraint: {constraints[0]}.")
    if thin_input:
        plan.append("Add timing, people, resources, and constraints before relying on the daily outline.")
    plan.append("No calendar event, reminder, or task was created.")
    return plan


def _weekly_plan(goals: list[str], errands: list[str], household_notes: str, constraints: list[str]) -> list[str]:
    plan = [
        "Group the week into prepare, handle, reset, and review blocks manually.",
        f"Carry forward goal: {goals[0]}." if goals else "Choose a weekly focus before expanding the plan.",
    ]
    if errands:
        plan.append(f"Batch user-provided errands starting with: {errands[0]}.")
    if household_notes:
        plan.append("Use household notes to decide what needs coordination.")
    if constraints:
        plan.append(f"Do not exceed stated constraint: {constraints[0]}.")
    plan.append("No scheduling, routing, booking, delivery, or completion is performed.")
    return plan


def _routine_plan(life_area: str, goals: list[str], schedule_notes: str, energy_notes: str) -> list[str]:
    return [
        f"Define a small routine for {life_area}.",
        f"Start with: {goals[0]}." if goals else "Start with the smallest repeatable step.",
        f"Fit the routine around schedule context: {schedule_notes}." if schedule_notes else "Choose a realistic time cue manually.",
        f"Adjust for energy context: {energy_notes}." if energy_notes else "Keep a low-energy fallback option.",
        "Review manually before making the routine larger.",
    ]


def _errand_plan(errands: list[str], constraints: list[str], resources: list[str], budget_notes: str) -> list[str]:
    plan = []
    if errands:
        plan.extend([f"List errand: {errand}." for errand in errands[:5]])
    else:
        plan.append("No errands were provided; add errands before treating this as an errand plan.")
    if resources:
        plan.append(f"Use available resource manually: {resources[0]}.")
    if budget_notes:
        plan.append(f"Keep budget context visible: {budget_notes}.")
    if constraints:
        plan.append(f"Respect constraint: {constraints[0]}.")
    plan.append("No maps, location data, purchases, orders, bookings, or messages were used.")
    return plan


def _household_plan(household_notes: str, people_involved: list[str], resources: list[str], constraints: list[str]) -> list[str]:
    plan = []
    if household_notes:
        plan.append(f"Household context: {household_notes}.")
    if people_involved:
        plan.append(f"Coordinate manually with: {', '.join(people_involved[:4])}.")
    if resources:
        plan.append(f"Available resource: {resources[0]}.")
    if constraints:
        plan.append(f"Boundary: {constraints[0]}.")
    if not plan:
        plan.append("Add household notes, people, resources, or constraints for a stronger household plan.")
    plan.append("No contacts, smart-home devices, accounts, emails, posts, messages, files, or records were accessed or changed.")
    return plan


def _preparation_checklist(situation: str, goals: list[str], errands: list[str], resources: list[str], constraints: list[str], high_stakes: bool) -> list[str]:
    checklist = [
        f"Restate the situation: {situation}.",
        "Choose the next smallest manual step.",
    ]
    if goals:
        checklist.append(f"Confirm goal: {goals[0]}.")
    if errands:
        checklist.append(f"Prepare for errand: {errands[0]}.")
    if resources:
        checklist.append(f"Gather or check resource manually: {resources[0]}.")
    if constraints:
        checklist.append(f"Check constraint before acting: {constraints[0]}.")
    if high_stakes:
        checklist.append("Use appropriate human, professional, emergency, or local authority support before acting on high-stakes concerns.")
    checklist.append("Do not treat this checklist as task creation, scheduling, automation, completion, or execution.")
    return checklist


def _next_actions(desired_output_type: str, thin_input: bool, high_stakes: bool) -> list[str]:
    actions = []
    if thin_input:
        actions.append("Add goals, constraints, schedule notes, errands, people, resources, energy, budget, or household details.")
    if high_stakes:
        actions.append("Seek appropriate human, professional, emergency, or local authority help for high-stakes concerns.")
    if desired_output_type == "daily_plan":
        actions.append("Pick one manual daily anchor and one fallback.")
    elif desired_output_type == "weekly_plan":
        actions.append("Group the week into a few manual focus blocks.")
    elif desired_output_type == "errand_plan":
        actions.append("Confirm the errand list manually before leaving or buying anything.")
    elif desired_output_type == "preparation_checklist":
        actions.append("Review the checklist and remove anything unnecessary.")
    elif desired_output_type == "priority_review":
        actions.append("Choose the highest-value item and the easiest next step.")
    else:
        actions.append("Use this as manual planning support only.")
    actions.append("Do not create tasks, reminders, calendar events, emails, files, database rows, purchases, posts, or messages from this response.")
    return actions[:5]


def _open_questions(
    goals: list[str],
    constraints: list[str],
    schedule_notes: str,
    household_notes: str,
    errands: list[str],
    people_involved: list[str],
    resources: list[str],
    energy_notes: str,
    budget_notes: str,
) -> list[str]:
    questions = []
    if not goals:
        questions.append("What outcome matters most?")
    if not constraints:
        questions.append("What constraints should be respected?")
    if not schedule_notes:
        questions.append("What timing context matters?")
    if not household_notes:
        questions.append("Is there household context to include?")
    if not errands:
        questions.append("Are there errands or outside-home steps?")
    if not people_involved:
        questions.append("Who else is involved, if anyone?")
    if not resources:
        questions.append("What resources are available?")
    if not energy_notes:
        questions.append("What energy or capacity context should shape the plan?")
    if not budget_notes:
        questions.append("Is there a budget boundary?")
    return questions


def _warnings(thin_input: bool, high_stakes: bool) -> list[str]:
    warnings = []
    if thin_input:
        warnings.append("Everyday-life input is thin; output is a provisional local planning scaffold.")
    if high_stakes:
        warnings.append("Potentially high-stakes wording detected; this response is not professional, emergency, legal, medical, financial, or safety validation.")
    warnings.append("This response does not schedule, execute, complete, buy, send, post, persist, or automate anything.")
    return warnings


def _limitations(thin_input: bool, high_stakes: bool) -> list[str]:
    limitations = [
        "Based only on user-provided everyday-life planning inputs.",
        "Plans and checklists are suggestions only, not automation, scheduling, execution, completion, delivery, booking, purchase, or validation.",
        "No Gmail, Calendar, contacts, maps, location, finance, smart-home, health-app, external account, connector, file, database, task, reminder, email, post, message, purchase, shell command, web browsing, or external API was accessed or changed.",
    ]
    if thin_input:
        limitations.append("Thin input limits specificity; add goals, constraints, timing, household, errand, people, resource, energy, or budget details.")
    if high_stakes:
        limitations.append("Money, legal, medical, safety, or emergency-related situations require appropriate human, professional, emergency, or local authority help.")
    return limitations
