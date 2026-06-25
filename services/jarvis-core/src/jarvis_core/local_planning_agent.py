from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_planning_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_planning"
SUPPORTED_OUTPUT_TYPES = ("project_plan", "study_plan", "checklist", "weekly_plan")


@dataclass(frozen=True)
class LocalPlanningRequest:
    goal: str
    context_notes: str = ""
    constraints: list[str] = field(default_factory=list)
    resources: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    timeframe: str | None = None
    desired_output_type: str = "project_plan"


class LocalPlanningAgentService:
    def create_plan(self, request: LocalPlanningRequest) -> dict[str, Any]:
        goal = request.goal.strip() or "Untitled local planning goal"
        desired_output_type = _normalize_output_type(request.desired_output_type)
        context_points = _extract_context_points(request.context_notes)
        constraints = _clean_list(request.constraints)
        resources = _clean_list(request.resources)
        blockers = _clean_list(request.blockers)
        timeframe = (request.timeframe or "").strip()
        thin_context = not context_points and not constraints and not resources and not blockers and not timeframe

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "goal": goal,
            "desiredOutputType": desired_output_type,
            "planningFocus": _planning_focus(goal, desired_output_type, timeframe, thin_context),
            "assumptions": _assumptions(context_points, constraints, resources, timeframe, thin_context),
            "phases": _phases(goal, desired_output_type, context_points, constraints, resources, blockers, timeframe),
            "checklist": _checklist(goal, desired_output_type, blockers, thin_context),
            "nextActions": _next_actions(desired_output_type, blockers, thin_context),
            "risks": _risks(constraints, blockers, thin_context),
            "blockers": blockers or ["No blockers were provided."],
            "reviewQuestions": _review_questions(desired_output_type, thin_context),
            "warnings": _warnings(thin_context),
            "limitations": _limitations(thin_context),
            "safety": local_planning_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_planning_dashboard_summary()


def local_planning_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Planning Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/planning/local-plan",
        "outputTypes": list(SUPPORTED_OUTPUT_TYPES),
        "responseOnly": True,
        "taskPersistence": False,
        "reminders": False,
        "calendarEmailIntegration": False,
        "externalServices": False,
        "paidApis": False,
        "webBrowsing": False,
        "connectorExecution": False,
        "fileReads": False,
        "fileWrites": False,
        "shellExecution": False,
        "uploads": False,
        "mutation": False,
        "limitations": ["based only on user-provided planning inputs"],
    }


def local_planning_safety() -> dict[str, bool]:
    return {
        "localOnly": True,
        "responseOnly": True,
        "externalServices": False,
        "paidApis": False,
        "webBrowsing": False,
        "connectorExecution": False,
        "oauth": False,
        "accountAccess": False,
        "postingOrSending": False,
        "calendarEmailIntegration": False,
        "taskPersistence": False,
        "reminders": False,
        "fileReads": False,
        "fileWrites": False,
        "shellExecution": False,
        "uploads": False,
        "mutation": False,
    }


def _normalize_output_type(value: str) -> str:
    normalized = (value or "project_plan").strip().lower()
    return normalized if normalized in SUPPORTED_OUTPUT_TYPES else "project_plan"


def _extract_context_points(notes: str) -> list[str]:
    if not notes.strip():
        return []
    raw_parts = re.split(r"(?:\r?\n+|(?<=[.!?])\s+|[;•]+)", notes)
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


def _clean_list(values: list[str]) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = re.sub(r"\s+", " ", value.strip())
        key = item.lower()
        if item and key not in seen:
            cleaned.append(item)
            seen.add(key)
    return cleaned[:10]


def _planning_focus(goal: str, desired_output_type: str, timeframe: str, thin_context: bool) -> str:
    if thin_context:
        return f"Clarify and sequence the goal before committing to a detailed plan: {goal}."
    if desired_output_type == "study_plan":
        return f"Build a study path for {goal} using the provided resources, blockers, and timeframe."
    if desired_output_type == "weekly_plan":
        return f"Turn {goal} into a week-by-week local execution plan."
    if desired_output_type == "checklist":
        return f"Turn {goal} into an ordered checklist of local next steps."
    if timeframe:
        return f"Plan {goal} around the stated timeframe: {timeframe}."
    return f"Plan {goal} from the provided notes, constraints, resources, and blockers."


def _assumptions(
    context_points: list[str],
    constraints: list[str],
    resources: list[str],
    timeframe: str,
    thin_context: bool,
) -> list[str]:
    if thin_context:
        return ["The plan is provisional because little planning context was provided."]
    assumptions = ["The plan uses only user-provided planning inputs."]
    if context_points:
        assumptions.append("Context notes identify the working background for the plan.")
    if constraints:
        assumptions.append("Constraints should shape scope and sequencing.")
    if resources:
        assumptions.append("Resources are available unless the user later says otherwise.")
    if timeframe:
        assumptions.append(f"The stated timeframe is treated as a planning guide: {timeframe}.")
    return assumptions


def _phases(
    goal: str,
    desired_output_type: str,
    context_points: list[str],
    constraints: list[str],
    resources: list[str],
    blockers: list[str],
    timeframe: str,
) -> list[dict[str, Any]]:
    phase_names = _phase_names(desired_output_type)
    phases: list[dict[str, Any]] = []
    for index, name in enumerate(phase_names, start=1):
        actions = _phase_actions(index, goal, context_points, constraints, resources, blockers, desired_output_type)
        phase: dict[str, Any] = {
            "name": name,
            "focus": actions[0],
            "actions": actions,
        }
        if index == 1 and timeframe:
            phase["timeframeNote"] = timeframe
        phases.append(phase)
    return phases


def _phase_names(desired_output_type: str) -> list[str]:
    if desired_output_type == "study_plan":
        return ["Orient", "Learn", "Practice", "Review"]
    if desired_output_type == "weekly_plan":
        return ["Week 1", "Week 2", "Week 3", "Review Week"]
    if desired_output_type == "checklist":
        return ["Prepare", "Execute", "Verify"]
    return ["Clarify", "Plan", "Execute", "Review"]


def _phase_actions(
    index: int,
    goal: str,
    context_points: list[str],
    constraints: list[str],
    resources: list[str],
    blockers: list[str],
    desired_output_type: str,
) -> list[str]:
    if index == 1:
        action = context_points[0] if context_points else f"Define what success means for {goal}."
        return [action, "List the smallest useful first outcome."]
    if index == 2:
        action = resources[0] if resources else "Identify the resources, people, time blocks, or references available locally."
        if desired_output_type == "study_plan":
            action = resources[0] if resources else "Start with fundamentals before advanced topics."
        return [action, "Convert available inputs into ordered work blocks."]
    if index == 3:
        action = constraints[0] if constraints else "Work through the plan in small reviewable steps."
        return [action, "Record what changed, what remains uncertain, and what needs review."]
    action = blockers[0] if blockers else "Review progress and update the plan from user-provided evidence."
    return [action, "Decide whether to continue, narrow scope, or revise the next actions."]


def _checklist(goal: str, desired_output_type: str, blockers: list[str], thin_context: bool) -> list[str]:
    items = [
        f"Restate the goal: {goal}.",
        "Confirm constraints, resources, blockers, and timeframe.",
        "Pick the next smallest useful action.",
    ]
    if desired_output_type == "study_plan":
        items.append("Separate learning, practice, and review blocks.")
    elif desired_output_type == "weekly_plan":
        items.append("Assign work to weekly buckets before adding detail.")
    elif desired_output_type == "checklist":
        items.append("Mark each item as todo, doing, blocked, or done outside this response-only agent.")
    else:
        items.append("Group work into clarify, plan, execute, and review phases.")
    if blockers:
        items.append("Resolve or route each named blocker before expanding scope.")
    if thin_context:
        items.append("Add more context before treating this as a committed plan.")
    return items


def _next_actions(desired_output_type: str, blockers: list[str], thin_context: bool) -> list[str]:
    if blockers:
        return [
            "Choose the highest-impact blocker and define the next local step.",
            "Clarify what can proceed while blockers remain unresolved.",
        ]
    if thin_context:
        return [
            "Add context notes, constraints, resources, blockers, or timeframe.",
            "Define one concrete success criterion for the goal.",
        ]
    if desired_output_type == "study_plan":
        return ["Choose the first learning block.", "Define how progress will be reviewed."]
    if desired_output_type == "weekly_plan":
        return ["Assign the first week of work.", "Set a review point before expanding later weeks."]
    if desired_output_type == "checklist":
        return ["Start with the first checklist item.", "Review the checklist after the first completed step."]
    return ["Start with the clarify phase.", "Review the plan after the first local milestone."]


def _risks(constraints: list[str], blockers: list[str], thin_context: bool) -> list[str]:
    risks = []
    if thin_context:
        risks.append("The plan may be too generic because little context was provided.")
    if constraints:
        risks.append("Constraints may require reducing scope or extending the timeline.")
    if blockers:
        risks.append("Named blockers may prevent progress until resolved or routed around.")
    if not risks:
        risks.append("Scope may expand if progress is not reviewed after each phase.")
    return risks


def _review_questions(desired_output_type: str, thin_context: bool) -> list[str]:
    questions = [
        "What would make the next step clearly complete?",
        "Which assumption should be checked first?",
    ]
    if desired_output_type == "study_plan":
        questions.append("How will learning be practiced or tested?")
    elif desired_output_type == "weekly_plan":
        questions.append("Which week has the highest uncertainty?")
    elif desired_output_type == "checklist":
        questions.append("Which checklist item is most likely to block the rest?")
    else:
        questions.append("Which phase needs more detail before work begins?")
    if thin_context:
        questions.append("What context should be added before relying on this plan?")
    return questions


def _warnings(thin_context: bool) -> list[str]:
    if thin_context:
        return ["Planning context is thin; output is a provisional local planning scaffold."]
    return []


def _limitations(thin_context: bool) -> list[str]:
    limitations = [
        "Based only on user-provided planning inputs.",
        "No tasks, reminders, calendar events, emails, files, or database records were created.",
        "No external services, paid APIs, connectors, shell commands, uploads, or account access were used.",
    ]
    if thin_context:
        limitations.append("Thin context limits specificity; add notes, constraints, resources, blockers, or timeframe for a stronger plan.")
    return limitations
