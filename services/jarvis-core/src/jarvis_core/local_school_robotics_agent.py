from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_school_robotics_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_school_robotics_planning"
SUPPORTED_OUTPUT_TYPES = (
    "school_brief",
    "course_plan",
    "robotics_prep_plan",
    "research_outreach_plan",
    "project_roadmap",
    "study_schedule",
    "coop_prep_plan",
    "campus_resource_plan",
)


@dataclass(frozen=True)
class LocalSchoolRoboticsRequest:
    academic_goal: str
    student_name: str = ""
    school_name: str = ""
    program_name: str = ""
    term_or_timeline: str = ""
    robotics_focus: str = ""
    courses: list[str] = field(default_factory=list)
    professors_or_labs: list[str] = field(default_factory=list)
    projects: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    resources: list[str] = field(default_factory=list)
    current_preparation: str = ""
    desired_output_type: str = "school_brief"


class LocalSchoolRoboticsAgentService:
    def create_plan(self, request: LocalSchoolRoboticsRequest) -> dict[str, Any]:
        student_name = _clean_text(request.student_name)
        school_name = _clean_text(request.school_name)
        program_name = _clean_text(request.program_name)
        term_or_timeline = _clean_text(request.term_or_timeline)
        academic_goal = _clean_text(request.academic_goal)
        robotics_focus = _clean_text(request.robotics_focus)
        courses = _clean_list(request.courses)
        professors_or_labs = _clean_list(request.professors_or_labs)
        projects = _clean_list(request.projects)
        constraints = _clean_list(request.constraints)
        resources = _clean_list(request.resources)
        current_preparation = _clean_text(request.current_preparation)
        desired_output_type = _normalize_output_type(request.desired_output_type)
        thin_input = _thin_input(
            academic_goal,
            robotics_focus,
            courses,
            professors_or_labs,
            projects,
            constraints,
            resources,
            current_preparation,
        )
        high_stakes_context = _high_stakes_context(academic_goal, constraints, resources, current_preparation)

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "studentName": student_name,
            "schoolName": school_name,
            "programName": program_name,
            "desiredOutputType": desired_output_type,
            "academicFocus": _academic_focus(academic_goal, program_name, school_name, desired_output_type, thin_input),
            "roboticsFocus": _robotics_focus(robotics_focus, projects, resources),
            "timelineSummary": _timeline_summary(term_or_timeline, constraints, current_preparation, thin_input),
            "coursePlan": _course_plan(courses, academic_goal, robotics_focus, constraints),
            "roboticsPrepPlan": _robotics_prep_plan(robotics_focus, projects, resources, current_preparation, constraints),
            "researchOutreachPlan": _research_outreach_plan(professors_or_labs, academic_goal, robotics_focus, projects, constraints),
            "projectRoadmap": _project_roadmap(projects, academic_goal, robotics_focus, resources, constraints),
            "studySchedule": _study_schedule(courses, term_or_timeline, current_preparation, constraints),
            "coopPrepPlan": _coop_prep_plan(academic_goal, robotics_focus, projects, resources, constraints),
            "campusResourcePlan": _campus_resource_plan(resources, school_name, program_name, constraints),
            "nextActions": _next_actions(desired_output_type, thin_input, high_stakes_context),
            "openQuestions": _open_questions(
                academic_goal,
                robotics_focus,
                courses,
                professors_or_labs,
                projects,
                constraints,
                resources,
                current_preparation,
                term_or_timeline,
            ),
            "warnings": _warnings(thin_input, high_stakes_context),
            "limitations": _limitations(thin_input, high_stakes_context),
            "safety": local_school_robotics_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_school_robotics_dashboard_summary()


def local_school_robotics_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local School / Robotics Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/school-robotics/local-plan",
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
        "schoolPortalAccess": False,
        "emailSending": False,
        "calendarAccess": False,
        "registrarAccess": False,
        "financialAidAccess": False,
        "jobApplicationSubmission": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "mutation": False,
        "officialAcademicValidation": False,
        "certificationClaims": False,
        "limitations": ["based only on user-provided school and robotics planning inputs"],
    }


def local_school_robotics_safety() -> dict[str, bool]:
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
        "schoolPortalAccess": False,
        "emailSending": False,
        "calendarAccess": False,
        "registrarAccess": False,
        "financialAidAccess": False,
        "jobApplicationSubmission": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "mutation": False,
        "officialAcademicValidation": False,
        "certificationClaims": False,
    }


def _normalize_output_type(value: str) -> str:
    normalized = (value or "school_brief").strip().lower()
    return normalized if normalized in SUPPORTED_OUTPUT_TYPES else "school_brief"


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
    academic_goal: str,
    robotics_focus: str,
    courses: list[str],
    professors_or_labs: list[str],
    projects: list[str],
    constraints: list[str],
    resources: list[str],
    current_preparation: str,
) -> bool:
    return not any(
        [academic_goal, robotics_focus, courses, professors_or_labs, projects, constraints, resources, current_preparation]
    )


def _high_stakes_context(academic_goal: str, constraints: list[str], resources: list[str], current_preparation: str) -> bool:
    text = " ".join([academic_goal, " ".join(constraints), " ".join(resources), current_preparation]).lower()
    terms = (
        "financial aid",
        "visa",
        "immigration",
        "legal",
        "medical",
        "disability",
        "accommodation",
        "scholarship",
        "graduation",
        "registration",
        "co-op offer",
        "employment",
        "job offer",
    )
    return any(term in text for term in terms)


def _academic_focus(
    academic_goal: str,
    program_name: str,
    school_name: str,
    desired_output_type: str,
    thin_input: bool,
) -> str:
    if thin_input:
        return "Clarify the academic goal before treating this as a usable school or robotics preparation plan."
    if desired_output_type == "course_plan":
        return "Compare supplied course notes manually against the stated academic goal without verifying availability."
    if desired_output_type == "robotics_prep_plan":
        return "Prepare a robotics learning path from supplied focus areas, projects, and resources."
    if desired_output_type == "research_outreach_plan":
        return "Draft manual research outreach preparation from supplied professor, lab, project, and goal notes."
    if desired_output_type == "project_roadmap":
        return "Turn supplied project ideas into a manual academic and robotics project roadmap."
    if desired_output_type == "study_schedule":
        return "Organize supplied course and preparation notes into a manual study schedule."
    if desired_output_type == "coop_prep_plan":
        return "Shape co-op preparation from supplied academic, robotics, project, and resource notes."
    if desired_output_type == "campus_resource_plan":
        return "Organize supplied campus resource notes without accessing school systems or accounts."
    context = " / ".join(part for part in [school_name, program_name] if part)
    if context:
        return f"Prepare a local school and robotics brief for {context}: {academic_goal}."
    return f"Prepare a local school and robotics brief for: {academic_goal}."


def _robotics_focus(robotics_focus: str, projects: list[str], resources: list[str]) -> list[str]:
    focus = []
    focus.append(f"Robotics focus supplied by user: {robotics_focus}." if robotics_focus else "Robotics focus is not yet specified.")
    if projects:
        focus.append(f"Project context to use manually: {projects[0]}.")
    if resources:
        focus.append(f"Resource to consider manually: {resources[0]}.")
    focus.append("No robotics repositories, lab pages, device data, simulators, or external services were accessed.")
    return focus


def _timeline_summary(term_or_timeline: str, constraints: list[str], current_preparation: str, thin_input: bool) -> list[str]:
    summary = []
    summary.append(f"Timeline supplied by user: {term_or_timeline}." if term_or_timeline else "Timeline is not specified.")
    if current_preparation:
        summary.append(f"Current preparation note: {current_preparation}.")
    if constraints:
        summary.append(f"First constraint to respect manually: {constraints[0]}.")
    if thin_input:
        summary.append("Input is thin; add courses, robotics focus, project notes, resources, constraints, and timeline details.")
    summary.append("No calendar events, tasks, registrar records, or school systems were checked or changed.")
    return summary


def _course_plan(courses: list[str], academic_goal: str, robotics_focus: str, constraints: list[str]) -> list[dict[str, str]]:
    source_courses = courses or ["Course options not supplied"]
    plan = []
    for index, course in enumerate(source_courses[:5], start=1):
        note_parts = ["Manual comparison only; course availability and requirements were not verified."]
        if academic_goal:
            note_parts.append(f"Relate to academic goal: {academic_goal}.")
        if robotics_focus:
            note_parts.append(f"Robotics connection to consider: {robotics_focus}.")
        if constraints:
            note_parts.append(f"Constraint: {constraints[0]}.")
        plan.append({"slot": f"course_{index}", "course": course, "planningNote": " ".join(note_parts)})
    return plan


def _robotics_prep_plan(
    robotics_focus: str,
    projects: list[str],
    resources: list[str],
    current_preparation: str,
    constraints: list[str],
) -> list[str]:
    focus = robotics_focus or "the supplied robotics interest"
    plan = [
        f"Map fundamentals needed for {focus}: controls, sensing, software, mechanics, or validation as applicable.",
        "Choose one small practice milestone that can be reviewed manually.",
        "Keep notes tied to user-provided course, project, and research goals.",
    ]
    if current_preparation:
        plan.append(f"Start from current preparation: {current_preparation}.")
    if projects:
        plan.append(f"Use project context: {projects[0]}.")
    if resources:
        plan.append(f"Review user-named resource manually: {resources[0]}.")
    if constraints:
        plan.append(f"Respect constraint: {constraints[0]}.")
    plan.append("No robot hardware, simulator, repository, school lab system, or external service was accessed.")
    return plan[:8]


def _research_outreach_plan(
    professors_or_labs: list[str],
    academic_goal: str,
    robotics_focus: str,
    projects: list[str],
    constraints: list[str],
) -> list[dict[str, str]]:
    targets = professors_or_labs or ["Research target not yet supplied"]
    plan = []
    for target in targets[:4]:
        talking_points = []
        if academic_goal:
            talking_points.append(f"Academic goal: {academic_goal}.")
        if robotics_focus:
            talking_points.append(f"Robotics interest: {robotics_focus}.")
        if projects:
            talking_points.append(f"Project context: {projects[0]}.")
        if constraints:
            talking_points.append(f"Constraint to mention or respect: {constraints[0]}.")
        if not talking_points:
            talking_points.append("Add goal, robotics focus, project notes, and constraints before drafting outreach.")
        plan.append(
            {
                "target": target,
                "preparation": " ".join(talking_points),
                "boundary": "Draft preparation only; no professor website lookup, email sending, form submission, or placement claim.",
            }
        )
    return plan


def _project_roadmap(
    projects: list[str],
    academic_goal: str,
    robotics_focus: str,
    resources: list[str],
    constraints: list[str],
) -> list[dict[str, str]]:
    roadmap_projects = projects or ["Project idea not yet supplied"]
    roadmap = []
    for project in roadmap_projects[:4]:
        roadmap.append(
            {
                "project": project,
                "step": _project_step(project, academic_goal, robotics_focus, resources, constraints),
                "reviewGate": "Manual review only; no repository, file, lab system, or submission was created or checked.",
            }
        )
    return roadmap


def _project_step(
    project: str,
    academic_goal: str,
    robotics_focus: str,
    resources: list[str],
    constraints: list[str],
) -> str:
    parts = [f"Define the smallest reviewable milestone for {project}."]
    if academic_goal:
        parts.append(f"Connect it to {academic_goal}.")
    if robotics_focus:
        parts.append(f"Make the robotics angle explicit: {robotics_focus}.")
    if resources:
        parts.append(f"Use the supplied resource manually: {resources[0]}.")
    if constraints:
        parts.append(f"Respect: {constraints[0]}.")
    return " ".join(parts)


def _study_schedule(
    courses: list[str],
    term_or_timeline: str,
    current_preparation: str,
    constraints: list[str],
) -> list[dict[str, str]]:
    topics = courses[:4] or ["General academic and robotics preparation"]
    schedule = []
    for index, topic in enumerate(topics, start=1):
        focus_parts = ["Manual study block only; no calendar event or reminder was created."]
        if term_or_timeline:
            focus_parts.append(f"Timeline context: {term_or_timeline}.")
        if current_preparation:
            focus_parts.append(f"Start from: {current_preparation}.")
        if constraints:
            focus_parts.append(f"Constraint: {constraints[0]}.")
        schedule.append({"block": f"study_block_{index}", "topic": topic, "focus": " ".join(focus_parts)})
    return schedule


def _coop_prep_plan(
    academic_goal: str,
    robotics_focus: str,
    projects: list[str],
    resources: list[str],
    constraints: list[str],
) -> list[str]:
    plan = [
        "Translate academic and robotics notes into a manual skills inventory.",
        "Prepare project stories with problem, action, tradeoff, and result fields; do not claim verified outcomes.",
        "Draft interview or resume talking points for human review only.",
    ]
    if academic_goal:
        plan.append(f"Align co-op preparation with academic goal: {academic_goal}.")
    if robotics_focus:
        plan.append(f"Highlight robotics focus where supported by user-provided examples: {robotics_focus}.")
    if projects:
        plan.append(f"Use project evidence from user notes: {projects[0]}.")
    if resources:
        plan.append(f"Review user-named resource manually: {resources[0]}.")
    if constraints:
        plan.append(f"Respect constraint: {constraints[0]}.")
    plan.append("No Handshake, job board, application, email, calendar, account, or employer system was accessed.")
    return plan[:8]


def _campus_resource_plan(resources: list[str], school_name: str, program_name: str, constraints: list[str]) -> list[str]:
    plan = []
    if resources:
        plan.extend(f"Review user-provided resource manually: {resource}." for resource in resources[:5])
    else:
        plan.append("List campus resources manually before relying on this plan.")
    if school_name:
        plan.append(f"Treat {school_name} references as user-provided context only; no official systems were checked.")
    if program_name:
        plan.append(f"Use {program_name} as user-provided program context only.")
    if constraints:
        plan.append(f"Resource planning constraint: {constraints[0]}.")
    plan.append("Confirm official academic, financial-aid, visa, legal, medical, or employment decisions with the school or qualified professionals.")
    return plan


def _next_actions(desired_output_type: str, thin_input: bool, high_stakes_context: bool) -> list[str]:
    actions = []
    if thin_input:
        actions.append("Add academic goal detail, courses, robotics focus, project notes, resources, constraints, and timeline.")
    if desired_output_type == "course_plan":
        actions.append("Manually compare each supplied course against the academic goal and official requirements.")
    elif desired_output_type == "robotics_prep_plan":
        actions.append("Choose one robotics preparation milestone and define how it will be reviewed manually.")
    elif desired_output_type == "research_outreach_plan":
        actions.append("Draft outreach text separately for human review; do not send it from this agent.")
    elif desired_output_type == "project_roadmap":
        actions.append("Pick the smallest project milestone that can demonstrate progress without overclaiming.")
    elif desired_output_type == "study_schedule":
        actions.append("Place study blocks into a personal system manually if desired.")
    elif desired_output_type == "coop_prep_plan":
        actions.append("Prepare project stories and role targets manually without submitting applications.")
    elif desired_output_type == "campus_resource_plan":
        actions.append("Confirm resource details manually through official school channels.")
    else:
        actions.append("Use this as a local planning brief only.")
    if high_stakes_context:
        actions.append("Confirm official academic, financial-aid, visa, legal, medical, or employment decisions with official school or professional sources.")
    actions.append("Do not treat this response as live course, portal, registrar, co-op, professor, or graduation verification.")
    return actions[:5]


def _open_questions(
    academic_goal: str,
    robotics_focus: str,
    courses: list[str],
    professors_or_labs: list[str],
    projects: list[str],
    constraints: list[str],
    resources: list[str],
    current_preparation: str,
    term_or_timeline: str,
) -> list[str]:
    questions = []
    if not academic_goal:
        questions.append("What academic goal should anchor the plan?")
    if not robotics_focus:
        questions.append("What robotics focus, subfield, or preparation target matters most?")
    if not courses:
        questions.append("Which courses or course options should be compared from user-provided notes?")
    if not professors_or_labs:
        questions.append("Which professors, labs, or research groups should be considered from user-provided notes?")
    if not projects:
        questions.append("Which projects should support robotics, research, or co-op preparation?")
    if not constraints:
        questions.append("What constraints, deadlines, risk boundaries, or workload limits matter?")
    if not resources:
        questions.append("What campus, program, study, robotics, or career resources should be included?")
    if not current_preparation:
        questions.append("What preparation has already been completed?")
    if not term_or_timeline:
        questions.append("What term, semester, or timeline should the plan use?")
    return questions


def _warnings(thin_input: bool, high_stakes_context: bool) -> list[str]:
    warnings = []
    if thin_input:
        warnings.append("School and robotics input is thin; output is a provisional local planning scaffold.")
    if high_stakes_context:
        warnings.append("Official academic, financial-aid, visa, legal, medical, or employment decisions need official school or professional confirmation.")
    warnings.append("This response uses only request-provided data and does not verify courses, registration, co-op status, professor availability, admissions, graduation, or school records.")
    return warnings


def _limitations(thin_input: bool, high_stakes_context: bool) -> list[str]:
    limitations = [
        "Based only on user-provided school, robotics, research, course, co-op, project, and study-planning inputs.",
        "No Northeastern systems, student portals, registrar data, Handshake, financial-aid accounts, email, calendar, professor websites, live course catalogs, GitHub, files, external services, paid APIs, or connectors were accessed.",
        "No browsing, scraping, course availability verification, email sending, form submission, class registration, job application submission, calendar event creation, task creation, persistence, file access, database write, shell execution, mutation, official academic validation, certification, or guaranteed outcome was performed.",
        "No admission, enrollment, financial-aid, visa, course-registration, co-op, professor-response, research-placement, graduation, employment, project-success, or certification certainty is claimed.",
    ]
    if thin_input:
        limitations.append("Thin input limits specificity; add course notes, robotics focus, timeline, project details, resources, constraints, and current preparation.")
    if high_stakes_context:
        limitations.append("For official academic, financial-aid, visa, legal, medical, or employment decisions, confirm with official school offices or qualified professionals.")
    return limitations
