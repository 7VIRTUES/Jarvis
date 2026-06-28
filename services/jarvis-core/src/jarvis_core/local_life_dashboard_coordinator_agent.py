from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .local_response_agents_catalog import local_response_agents_index


AGENT_ID = "local_life_dashboard_cross_agent_coordinator"
STATUS = "local_only"
MODE = "response_only_user_provided_life_dashboard_cross_agent_coordination"
SUPPORTED_OUTPUT_TYPES = (
    "life_dashboard",
    "cross_agent_plan",
    "agent_routing_plan",
    "priority_map",
    "weekly_operating_plan",
    "daily_focus_plan",
    "decision_map",
    "project_life_alignment",
    "risk_review",
    "next_action_stack",
    "checklist",
    "summary",
)


@dataclass(frozen=True)
class LocalLifeDashboardCoordinatorRequest:
    request: str = ""
    prompt_text: str = ""
    output_type: str = "summary"
    life_areas: list[str] = field(default_factory=list)
    current_goals: list[str] = field(default_factory=list)
    current_projects: list[str] = field(default_factory=list)
    urgent_items: list[str] = field(default_factory=list)
    time_horizon: str = ""
    available_time: str = ""
    energy_level: str = ""
    constraints_or_notes: str = ""
    priority_preference: str = ""
    domains_to_coordinate: list[str] = field(default_factory=list)
    existing_agent_outputs_or_notes: list[str] = field(default_factory=list)
    decision_context: str = ""
    weekly_focus: str = ""
    risk_or_stress_flags: list[str] = field(default_factory=list)
    desired_dashboard_style: str = ""


class LocalLifeDashboardCoordinatorAgentService:
    def create_plan(self, request: LocalLifeDashboardCoordinatorRequest) -> dict[str, Any]:
        request_text = _clean_text(request.request or request.prompt_text)
        output_type = _normalize_output_type(request.output_type)
        life_areas = _clean_list(request.life_areas)
        goals = _clean_list(request.current_goals)
        projects = _clean_list(request.current_projects)
        urgent_items = _clean_list(request.urgent_items)
        time_horizon = _clean_text(request.time_horizon)
        available_time = _clean_text(request.available_time)
        energy_level = _clean_text(request.energy_level)
        constraints = _clean_text(request.constraints_or_notes)
        priority_preference = _clean_text(request.priority_preference)
        domains = _clean_list(request.domains_to_coordinate)
        prior_notes = _clean_list(request.existing_agent_outputs_or_notes)
        decision_context = _clean_text(request.decision_context)
        weekly_focus = _clean_text(request.weekly_focus)
        risks = _clean_list(request.risk_or_stress_flags)
        style = _clean_text(request.desired_dashboard_style)
        dashboard_subject = _subject(life_areas, domains, goals, request_text)
        combined_text = " ".join(
            [
                request_text,
                " ".join(life_areas),
                " ".join(goals),
                " ".join(projects),
                " ".join(urgent_items),
                time_horizon,
                available_time,
                energy_level,
                constraints,
                priority_preference,
                " ".join(domains),
                " ".join(prior_notes),
                decision_context,
                weekly_focus,
                " ".join(risks),
                style,
            ]
        )
        immediate_danger = _has_immediate_danger(combined_text)
        high_stakes = _has_high_stakes_context(combined_text)
        thin_input = not any(
            [
                request_text,
                life_areas,
                goals,
                projects,
                urgent_items,
                time_horizon,
                available_time,
                energy_level,
                constraints,
                priority_preference,
                domains,
                prior_notes,
                decision_context,
                weekly_focus,
                risks,
                style,
            ]
        )
        recommended_agents = _recommended_agents(combined_text, life_areas, domains, goals, projects, urgent_items)

        return {
            "agent_id": AGENT_ID,
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "title": _title(output_type, dashboard_subject),
            "summary": _summary(output_type, dashboard_subject, thin_input),
            "assumptions": _assumptions(dashboard_subject, life_areas, domains, prior_notes, thin_input),
            "dashboard_sections": _dashboard_sections(output_type, life_areas, goals, projects, urgent_items, style),
            "life_area_snapshot": _life_area_snapshot(life_areas, goals, projects, risks),
            "priority_order": _priority_order(urgent_items, goals, projects, priority_preference, energy_level),
            "recommended_agents": recommended_agents,
            "cross_agent_plan": _cross_agent_plan(recommended_agents, output_type),
            "next_actions": _next_actions(output_type, urgent_items, goals, projects, available_time),
            "weekly_focus": _weekly_focus(weekly_focus, time_horizon, available_time, energy_level),
            "risk_flags": _risk_flags(immediate_danger, high_stakes, risks),
            "local_only_boundaries": _local_only_boundaries(),
            "limitations": _limitations(thin_input, immediate_danger, high_stakes),
            "follow_up_questions": _follow_up_questions(life_areas, goals, projects, urgent_items, time_horizon, available_time, energy_level, domains, decision_context, weekly_focus),
            "output_type": output_type,
            "safety": local_life_dashboard_coordinator_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_life_dashboard_coordinator_dashboard_summary()


def local_life_dashboard_coordinator_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Life Dashboard / Cross-Agent Coordinator",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/life-dashboard-coordinator/local-plan",
        "outputTypes": list(SUPPORTED_OUTPUT_TYPES),
        "responseOnly": True,
        "manualInputOnly": True,
        "localOnly": True,
        "nonPersistent": True,
        "externalServices": False,
        "connectors": False,
        "connectorExecution": False,
        "oauth": False,
        "accountAccess": False,
        "automaticSubAgentExecution": False,
        "agentHandoffs": False,
        "agentInvocation": False,
        "fileReads": False,
        "fileWrites": False,
        "emailAccess": False,
        "emailSending": False,
        "calendarAccess": False,
        "calendarScheduling": False,
        "socialPosting": False,
        "contactAccess": False,
        "webBrowsing": False,
        "paidApis": False,
        "paymentAccess": False,
        "dbWrites": False,
        "taskPersistence": False,
        "taskCreation": False,
        "reminderCreation": False,
        "shellExecution": False,
        "purchases": False,
        "bookings": False,
        "submissions": False,
        "officialFilings": False,
        "legalActions": False,
        "medicalDecisions": False,
        "emergencyCalls": False,
        "financialTransactions": False,
        "professionalCertainty": False,
        "mutation": False,
        "certificationClaims": False,
        "limitations": ["life dashboard, priority mapping, and cross-agent routing suggestions only from user-provided notes"],
    }


def local_life_dashboard_coordinator_safety() -> dict[str, bool]:
    return {key: value for key, value in local_life_dashboard_coordinator_dashboard_summary().items() if isinstance(value, bool)}


def _normalize_output_type(value: str) -> str:
    normalized = (value or "summary").strip().lower()
    return normalized if normalized in SUPPORTED_OUTPUT_TYPES else "summary"


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def _clean_list(values: list[str], limit: int = 16) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = _clean_text(value)
        key = item.lower()
        if item and key not in seen:
            cleaned.append(item)
            seen.add(key)
    return cleaned[:limit]


def _subject(life_areas: list[str], domains: list[str], goals: list[str], request_text: str) -> str:
    if life_areas:
        return ", ".join(life_areas[:5])
    if domains:
        return ", ".join(domains[:5])
    if goals:
        return ", ".join(goals[:3])
    return request_text or "local life dashboard"


def _has_immediate_danger(text: str) -> bool:
    lowered = text.lower()
    terms = (
        "immediate danger",
        "medical emergency",
        "violence",
        "gas leak",
        "fire",
        "carbon monoxide",
        "severe crisis",
        "active threat",
        "can't breathe",
        "cannot breathe",
        "suicide",
        "self-harm",
    )
    return any(term in lowered for term in terms)


def _has_high_stakes_context(text: str) -> bool:
    lowered = text.lower()
    terms = (
        "medical",
        "legal",
        "immigration",
        "financial",
        "loan",
        "debt",
        "emergency",
        "court",
        "visa",
        "diagnosis",
        "eviction",
        "official notice",
        "deadline",
    )
    return any(term in lowered for term in terms)


def _title(output_type: str, subject: str) -> str:
    return f"{output_type.replace('_', ' ').title()}: {subject[:80]}"


def _summary(output_type: str, subject: str, thin_input: bool) -> str:
    if thin_input:
        return "Local manual life-dashboard scaffold; add life areas, goals, projects, urgent items, time, energy, and domains for a more specific coordination plan."
    return f"Manual {output_type.replace('_', ' ')} for {subject}. No agents were invoked, no tasks were created, no dashboard state was persisted, and no accounts, files, connectors, calendars, email, or external services were accessed."


def _assumptions(subject: str, life_areas: list[str], domains: list[str], prior_notes: list[str], thin_input: bool) -> list[str]:
    assumptions = [f"Uses only user-provided life-dashboard and coordination notes for: {subject}."]
    if life_areas:
        assumptions.append(f"Life areas supplied by user: {', '.join(life_areas[:8])}.")
    if domains:
        assumptions.append(f"Domains to coordinate: {', '.join(domains[:8])}.")
    if prior_notes:
        assumptions.append("Existing agent outputs or notes were provided manually in the request; no other agents were called or queried.")
    if thin_input:
        assumptions.append("Input is thin; no history, memory, files, calendars, accounts, or agent runs were inspected.")
    return assumptions


def _dashboard_sections(output_type: str, life_areas: list[str], goals: list[str], projects: list[str], urgent_items: list[str], style: str) -> list[dict[str, Any]]:
    areas = life_areas or ["school/career", "projects", "health habits", "relationships", "money/admin"]
    sections = [
        {"name": "Today", "items": urgent_items[:5] or ["Pick one urgent item manually."]},
        {"name": "This week", "items": goals[:5] or ["Choose one weekly focus manually."]},
        {"name": "Projects", "items": projects[:5] or ["List active projects before routing to a local agent."]},
        {"name": "Life areas", "items": areas[:8]},
        {"name": "Routing", "items": ["Use recommended local agents as suggestions only; no automatic sub-agent execution."]},
    ]
    if style:
        sections.insert(0, {"name": "Dashboard style", "items": [style]})
    if output_type == "risk_review":
        sections.append({"name": "Risk review", "items": ["Separate immediate safety concerns from planning concerns."]})
    return sections


def _life_area_snapshot(life_areas: list[str], goals: list[str], projects: list[str], risks: list[str]) -> list[dict[str, str]]:
    areas = life_areas or ["school/career", "projects", "health habits", "finances/admin", "relationships"]
    snapshot: list[dict[str, str]] = []
    for index, area in enumerate(areas[:8]):
        goal = goals[index] if index < len(goals) else "No specific goal supplied."
        project = projects[index] if index < len(projects) else "No active project supplied."
        risk = risks[index] if index < len(risks) else "No specific risk supplied."
        snapshot.append({"life_area": area, "goal": goal, "active_project": project, "risk_or_stress": risk})
    return snapshot


def _priority_order(urgent_items: list[str], goals: list[str], projects: list[str], priority_preference: str, energy_level: str) -> list[str]:
    order: list[str] = []
    if priority_preference:
        order.append(f"Priority preference: {priority_preference}.")
    if urgent_items:
        order.extend([f"Urgent: {item}" for item in urgent_items[:5]])
    if goals:
        order.extend([f"Goal: {goal}" for goal in goals[:4]])
    if projects:
        order.extend([f"Project: {project}" for project in projects[:4]])
    if energy_level:
        order.append(f"Energy filter: {energy_level}. Use lower-friction actions when energy is limited.")
    if not order:
        order.append("Add urgent items, goals, and active projects to build a ranked priority order.")
    return order[:12]


def _recommended_agents(text: str, life_areas: list[str], domains: list[str], goals: list[str], projects: list[str], urgent_items: list[str]) -> list[dict[str, Any]]:
    available_agents = local_response_agents_index()
    catalog_by_name = {agent["name"]: agent for agent in available_agents}
    combined = " ".join([text, " ".join(life_areas), " ".join(domains), " ".join(goals), " ".join(projects), " ".join(urgent_items)]).lower()
    recommendations: list[dict[str, str]] = []
    for name, agent_id, keywords, reason in _agent_routing_rules():
        if any(keyword in combined for keyword in keywords):
            catalog_entry = catalog_by_name.get(name)
            if catalog_entry:
                recommendations.append(
                    {
                        "agent_id": agent_id,
                        "name": name,
                        "endpoint": catalog_entry["endpoint"],
                        "reason": reason,
                        "suggested_only": True,
                        "invoked": False,
                        "handoff_created": False,
                    }
                )
    if not recommendations:
        for name, agent_id, reason in (
            ("Local Planning Agent", "local_planning_agent", "General manual planning scaffold for undefined goals."),
            ("Local Decision Agent", "local_decision_agent", "Decision support when priority tradeoffs are unclear."),
            ("Local Life Direction / Values Agent", "local_life_direction_agent", "Values and direction framing for broad life-area choices."),
        ):
            catalog_entry = catalog_by_name.get(name)
            if catalog_entry:
                recommendations.append(
                    {
                        "agent_id": agent_id,
                        "name": name,
                        "endpoint": catalog_entry["endpoint"],
                        "reason": reason,
                        "suggested_only": True,
                        "invoked": False,
                        "handoff_created": False,
                    }
                )
    return recommendations[:8]


def _agent_routing_rules() -> tuple[tuple[str, str, tuple[str, ...], str], ...]:
    return (
        ("Local School / Robotics Agent", "local_school_robotics_agent", ("school", "class", "course", "robotics", "research", "co-op"), "School, robotics, research, or course planning needs."),
        ("Local Career / Job Search Agent", "local_career_agent", ("career", "job", "internship", "resume", "interview", "co-op", "networking"), "Career prep, job-search, internship, or interview planning."),
        ("Local Projects / Portfolio Agent", "local_projects_portfolio_agent", ("project", "portfolio", "github", "demo", "ship", "build"), "Project and portfolio planning from user-provided notes."),
        ("Local Finance / Loans / Budget Agent", "local_finance_budget_agent", ("money", "finance", "budget", "loan", "debt", "rent", "savings"), "Budget, loan, debt, rent, or cash-flow planning."),
        ("Local Health/Fitness Agent", "local_health_fitness_agent", ("health", "fitness", "workout", "sleep", "nutrition", "habit", "energy"), "Wellness, workout, nutrition, or habit planning."),
        ("Local Housing / Move / Travel Agent", "local_housing_move_travel_agent", ("housing", "move", "apartment", "travel", "commute", "relocation"), "Housing, move, commute, or travel planning."),
        ("Local Food / Cooking / Grocery Agent", "local_food_cooking_grocery", ("food", "meal", "grocery", "cooking", "pantry", "recipe"), "Meal, cooking, pantry, or grocery planning."),
        ("Local Relationship / Family Agent", "local_relationships_agent", ("relationship", "family", "friend", "roommate", "communication", "conflict"), "Relationship, family, roommate, or communication planning."),
        ("Local Hobbies / Adventure Agent", "local_hobbies_adventure", ("hobby", "adventure", "drone", "scooter", "camping", "fishing", "photography"), "Hobby, recreation, adventure, or gear planning."),
        ("Local Personal Knowledge / Memory Organizer Agent", "local_personal_knowledge_memory_organizer", ("knowledge", "memory", "notes", "wiki", "ideas", "review system"), "Personal notes, idea capture, wiki, and review-system organization."),
        ("Local Emergency / Preparedness Agent", "local_emergency_preparedness", ("emergency", "preparedness", "go bag", "fire", "gas leak", "storm", "power outage"), "Emergency preparedness planning from user-provided notes."),
        ("Local Personal Admin / Documents Agent", "local_personal_admin_agent", ("document", "admin", "forms", "paperwork", "appointment", "office"), "Personal admin and document checklist planning."),
        ("Local Legal / Immigration / Official Matters Agent", "local_legal_immigration_official_matters", ("legal", "immigration", "visa", "court", "official notice", "deadline"), "Official-matter organization with qualified-help reminders."),
        ("Local Emotional Reflection / Resilience Agent", "local_emotional_reflection_agent", ("stress", "burnout", "mood", "overwhelmed", "confidence", "resilience"), "Emotional reflection and resilience planning without therapy claims."),
        ("Local Culture / Taste / High-Class Lifestyle Agent", "local_culture_taste_high_class_lifestyle", ("culture", "taste", "etiquette", "wardrobe", "dining", "polished"), "Culture, etiquette, presentation, and taste-development planning."),
    )


def _cross_agent_plan(recommended_agents: list[dict[str, Any]], output_type: str) -> list[str]:
    plan = ["Use this as manual routing only; no local agent was invoked and no handoff was created."]
    for agent in recommended_agents[:6]:
        plan.append(f"Consider {agent['name']} for: {agent['reason']} Suggested endpoint: {agent['endpoint']}.")
    if output_type == "agent_routing_plan":
        plan.append("Copy relevant notes manually into the selected local agent request only if the user chooses to run it.")
    return plan


def _next_actions(output_type: str, urgent_items: list[str], goals: list[str], projects: list[str], available_time: str) -> list[str]:
    actions = ["Pick one manual focus before opening another local agent."]
    if urgent_items:
        actions.extend([f"Clarify urgent item: {item}" for item in urgent_items[:4]])
    if projects:
        actions.extend([f"Define next visible project step: {project}" for project in projects[:3]])
    if goals:
        actions.extend([f"Protect one goal-supporting action: {goal}" for goal in goals[:3]])
    if available_time:
        actions.append(f"Fit actions into available time: {available_time}.")
    if output_type == "next_action_stack":
        actions.append("Stack actions as: urgent safety/admin, deadline, energy-friendly progress, recovery.")
    return actions[:10]


def _weekly_focus(weekly_focus: str, time_horizon: str, available_time: str, energy_level: str) -> list[str]:
    focus = []
    if weekly_focus:
        focus.append(f"Weekly focus supplied by user: {weekly_focus}.")
    elif time_horizon:
        focus.append(f"Set focus for time horizon: {time_horizon}.")
    else:
        focus.append("Choose one weekly theme manually.")
    if available_time:
        focus.append(f"Available time: {available_time}.")
    if energy_level:
        focus.append(f"Energy level: {energy_level}.")
    focus.append("Keep the focus review manual; no reminders or tasks were scheduled.")
    return focus


def _risk_flags(immediate_danger: bool, high_stakes: bool, risks: list[str]) -> list[str]:
    flags = ["No live verification, professional certainty, emergency response, official filing, payment, transaction, or action execution was performed."]
    if risks:
        flags.extend([f"User-provided risk/stress flag: {risk}" for risk in risks[:5]])
    if high_stakes:
        flags.append("High-stakes domain detected; use qualified professionals or official sources for medical, legal, financial, immigration, emergency, psychological, academic, or professional decisions.")
    if immediate_danger:
        flags.append("Immediate-danger language detected; contact local emergency services or leave the area if safe to do so.")
    return flags


def _local_only_boundaries() -> list[str]:
    return [
        "Manual-input-only.",
        "Local-only.",
        "Response-only.",
        "Non-persistent.",
        "No connector behavior.",
        "No account access.",
        "No external services.",
        "No automatic sub-agent execution.",
        "No task creation, reminder scheduling, file mutation, purchases, bookings, submissions, official filings, emergency calls, or transactions.",
    ]


def _limitations(thin_input: bool, immediate_danger: bool, high_stakes: bool) -> list[str]:
    limitations = [
        "Based only on user-provided dashboard and coordination notes.",
        "Recommended agents are suggestions only; no agent was run, invoked, handed off, or queried.",
        "No dashboard state, task, reminder, file, record, or memory was created, edited, persisted, synced, exported, or mutated.",
        "No files, notes, history, email, calendar, contacts, accounts, connectors, web, paid APIs, payment systems, or external services were accessed.",
        "No medical, legal, financial, immigration, emergency, psychological, academic, or professional certainty is provided.",
    ]
    if high_stakes:
        limitations.append("High-stakes items should be checked with qualified professionals or official sources before action.")
    if immediate_danger:
        limitations.append("For immediate danger, medical emergency, violence, gas leak, fire, or severe crisis, contact local emergency services or leave the area if safe to do so.")
    if thin_input:
        limitations.append("Input is thin, so the dashboard remains a general local coordination scaffold.")
    return limitations


def _follow_up_questions(
    life_areas: list[str],
    goals: list[str],
    projects: list[str],
    urgent_items: list[str],
    time_horizon: str,
    available_time: str,
    energy_level: str,
    domains: list[str],
    decision_context: str,
    weekly_focus: str,
) -> list[str]:
    questions: list[str] = []
    if not life_areas:
        questions.append("Which life areas should the dashboard coordinate?")
    if not goals:
        questions.append("What current goals should be visible?")
    if not projects:
        questions.append("Which active projects need space in the plan?")
    if not urgent_items:
        questions.append("What urgent items or deadlines should be ranked first?")
    if not time_horizon:
        questions.append("What time horizon should the dashboard cover?")
    if not available_time:
        questions.append("How much available time should the plan assume?")
    if not energy_level:
        questions.append("What energy level or capacity should shape the next actions?")
    if not domains:
        questions.append("Which Jarvis local-agent domains should be coordinated?")
    if not decision_context:
        questions.append("What decision context or tradeoff matters most?")
    if not weekly_focus:
        questions.append("What should this week protect above everything else?")
    return questions[:6]
