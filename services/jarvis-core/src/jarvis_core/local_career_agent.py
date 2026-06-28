from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_career_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_career_planning"
SUPPORTED_OUTPUT_TYPES = (
    "career_brief",
    "resume_positioning",
    "job_search_plan",
    "networking_plan",
    "interview_prep",
    "skill_gap_plan",
    "application_checklist",
    "project_pitch_plan",
)


@dataclass(frozen=True)
class LocalCareerRequest:
    career_goal: str
    profile_name: str = ""
    target_roles: list[str] = field(default_factory=list)
    target_industries: list[str] = field(default_factory=list)
    current_experience: str = ""
    education_notes: str = ""
    skills: list[str] = field(default_factory=list)
    projects: list[str] = field(default_factory=list)
    resume_notes: str = ""
    job_search_notes: str = ""
    networking_notes: str = ""
    constraints: list[str] = field(default_factory=list)
    desired_output_type: str = "career_brief"


class LocalCareerAgentService:
    def create_plan(self, request: LocalCareerRequest) -> dict[str, Any]:
        profile_name = _clean_text(request.profile_name) or "Local career profile"
        career_goal = _clean_text(request.career_goal)
        target_roles = _clean_list(request.target_roles)
        target_industries = _clean_list(request.target_industries)
        current_experience = _clean_text(request.current_experience)
        education_notes = _clean_text(request.education_notes)
        skills = _clean_list(request.skills)
        projects = _clean_list(request.projects)
        resume_notes = _clean_text(request.resume_notes)
        job_search_notes = _clean_text(request.job_search_notes)
        networking_notes = _clean_text(request.networking_notes)
        constraints = _clean_list(request.constraints)
        desired_output_type = _normalize_output_type(request.desired_output_type)
        thin_input = _thin_input(
            career_goal,
            target_roles,
            target_industries,
            current_experience,
            education_notes,
            skills,
            projects,
            resume_notes,
            job_search_notes,
            networking_notes,
            constraints,
        )
        high_stakes_context = _high_stakes_context(career_goal, job_search_notes, constraints, resume_notes)

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "profileName": profile_name,
            "careerGoal": career_goal,
            "desiredOutputType": desired_output_type,
            "careerFocus": _career_focus(career_goal, target_roles, desired_output_type, thin_input),
            "targetRoleSummary": _target_role_summary(target_roles, target_industries, constraints),
            "experienceSummary": _experience_summary(current_experience, education_notes, skills, projects, thin_input),
            "resumePositioning": _resume_positioning(career_goal, target_roles, skills, projects, resume_notes, constraints),
            "jobSearchPlan": _job_search_plan(career_goal, target_roles, target_industries, job_search_notes, constraints),
            "networkingPlan": _networking_plan(target_roles, target_industries, networking_notes, constraints),
            "interviewPrep": _interview_prep(career_goal, target_roles, current_experience, skills, projects, constraints),
            "skillGapPlan": _skill_gap_plan(career_goal, target_roles, skills, projects, education_notes, constraints),
            "applicationChecklist": _application_checklist(career_goal, resume_notes, job_search_notes, constraints),
            "projectPitchPlan": _project_pitch_plan(projects, career_goal, target_roles, skills, constraints),
            "nextActions": _next_actions(desired_output_type, thin_input, high_stakes_context),
            "openQuestions": _open_questions(
                career_goal,
                target_roles,
                target_industries,
                current_experience,
                education_notes,
                skills,
                projects,
                resume_notes,
                job_search_notes,
                networking_notes,
                constraints,
            ),
            "warnings": _warnings(thin_input, high_stakes_context),
            "limitations": _limitations(thin_input, high_stakes_context),
            "safety": local_career_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_career_dashboard_summary()


def local_career_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Career / Job Search Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/career/local-plan",
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
        "jobBoardAccess": False,
        "schoolPortalAccess": False,
        "emailSending": False,
        "calendarAccess": False,
        "contactAccess": False,
        "jobApplicationSubmission": False,
        "resumeUpload": False,
        "messaging": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "mutation": False,
        "officialCareerValidation": False,
        "legalValidation": False,
        "certificationClaims": False,
        "limitations": ["based only on user-provided career and job-search planning inputs"],
    }


def local_career_safety() -> dict[str, bool]:
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
        "jobBoardAccess": False,
        "schoolPortalAccess": False,
        "emailSending": False,
        "calendarAccess": False,
        "contactAccess": False,
        "jobApplicationSubmission": False,
        "resumeUpload": False,
        "messaging": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "mutation": False,
        "officialCareerValidation": False,
        "legalValidation": False,
        "certificationClaims": False,
    }


def _normalize_output_type(value: str) -> str:
    normalized = (value or "career_brief").strip().lower()
    return normalized if normalized in SUPPORTED_OUTPUT_TYPES else "career_brief"


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
    career_goal: str,
    target_roles: list[str],
    target_industries: list[str],
    current_experience: str,
    education_notes: str,
    skills: list[str],
    projects: list[str],
    resume_notes: str,
    job_search_notes: str,
    networking_notes: str,
    constraints: list[str],
) -> bool:
    return not any(
        [
            career_goal,
            target_roles,
            target_industries,
            current_experience,
            education_notes,
            skills,
            projects,
            resume_notes,
            job_search_notes,
            networking_notes,
            constraints,
        ]
    )


def _high_stakes_context(career_goal: str, job_search_notes: str, constraints: list[str], resume_notes: str) -> bool:
    text = " ".join([career_goal, job_search_notes, " ".join(constraints), resume_notes]).lower()
    terms = (
        "visa",
        "immigration",
        "legal",
        "employment law",
        "contract",
        "salary negotiation",
        "severance",
        "noncompete",
        "relocation",
        "sponsorship",
        "work authorization",
    )
    return any(term in text for term in terms)


def _career_focus(career_goal: str, target_roles: list[str], desired_output_type: str, thin_input: bool) -> str:
    if thin_input:
        return "Clarify the career goal, target roles, experience, skills, projects, and constraints before relying on this plan."
    if desired_output_type == "resume_positioning":
        return "Position the resume from supplied experience, skills, projects, and role targets without uploading or parsing files."
    if desired_output_type == "job_search_plan":
        return "Shape a manual job-search strategy from supplied targets and constraints without searching job boards."
    if desired_output_type == "networking_plan":
        return "Draft networking preparation from supplied notes without sending messages or accessing contacts."
    if desired_output_type == "interview_prep":
        return "Prepare interview practice prompts from supplied background without scheduling interviews."
    if desired_output_type == "skill_gap_plan":
        return "Identify skill gaps from supplied roles, skills, projects, and education notes."
    if desired_output_type == "application_checklist":
        return "Create a manual application checklist without submitting forms, uploading resumes, or creating tasks."
    if desired_output_type == "project_pitch_plan":
        return "Turn supplied projects into role-relevant pitch notes for manual review."
    if target_roles:
        return f"Prepare for {target_roles[0]} opportunities using only user-provided career notes."
    return f"Prepare a local career brief for: {career_goal}."


def _target_role_summary(target_roles: list[str], target_industries: list[str], constraints: list[str]) -> list[str]:
    summary = []
    summary.append(f"Target roles from user notes: {', '.join(target_roles[:5])}." if target_roles else "Target roles are not yet specified.")
    if target_industries:
        summary.append(f"Target industries from user notes: {', '.join(target_industries[:5])}.")
    if constraints:
        summary.append(f"First constraint to respect manually: {constraints[0]}.")
    summary.append("No LinkedIn, Handshake, job boards, company sites, school portals, or external services were accessed.")
    return summary


def _experience_summary(
    current_experience: str,
    education_notes: str,
    skills: list[str],
    projects: list[str],
    thin_input: bool,
) -> list[str]:
    summary = []
    summary.append(f"Experience note: {current_experience}." if current_experience else "Current experience is not specified.")
    if education_notes:
        summary.append(f"Education note: {education_notes}.")
    if skills:
        summary.append(f"Skills named by user: {', '.join(skills[:6])}.")
    if projects:
        summary.append(f"Project evidence named by user: {projects[0]}.")
    if thin_input:
        summary.append("Input is thin; add role targets, experience, education, skills, projects, resume notes, job-search notes, networking notes, and constraints.")
    return summary


def _resume_positioning(
    career_goal: str,
    target_roles: list[str],
    skills: list[str],
    projects: list[str],
    resume_notes: str,
    constraints: list[str],
) -> list[str]:
    positioning = [
        f"Lead with the career goal: {career_goal}." if career_goal else "Define the career goal before positioning the resume.",
        f"Tailor summary language toward: {target_roles[0]}." if target_roles else "Name at least one target role before tailoring resume language.",
    ]
    if skills:
        positioning.append(f"Group strongest supplied skills around the role: {', '.join(skills[:4])}.")
    if projects:
        positioning.append(f"Use project proof point: {projects[0]}.")
    if resume_notes:
        positioning.append(f"Respect resume note: {resume_notes}.")
    if constraints:
        positioning.append(f"Constraint: {constraints[0]}.")
    positioning.append("No resume file was read, created, uploaded, or submitted.")
    return positioning


def _job_search_plan(
    career_goal: str,
    target_roles: list[str],
    target_industries: list[str],
    job_search_notes: str,
    constraints: list[str],
) -> list[str]:
    plan = [
        "Define a small manual target list from user-provided role and industry notes.",
        "Track opportunities outside this agent if desired; this response does not create persistent records.",
    ]
    if career_goal:
        plan.append(f"Keep search choices aligned with: {career_goal}.")
    if target_roles:
        plan.append(f"Prioritize role family: {target_roles[0]}.")
    if target_industries:
        plan.append(f"Industry context: {target_industries[0]}.")
    if job_search_notes:
        plan.append(f"User-provided search note: {job_search_notes}.")
    if constraints:
        plan.append(f"Constraint: {constraints[0]}.")
    plan.append("No job boards, company sites, live listings, accounts, forms, or applications were accessed.")
    return plan[:8]


def _networking_plan(target_roles: list[str], target_industries: list[str], networking_notes: str, constraints: list[str]) -> list[dict[str, str]]:
    contexts = target_roles[:3] or target_industries[:3] or ["career conversation"]
    plan = []
    for context in contexts:
        plan.append(
            {
                "context": context,
                "scriptSeed": _networking_script_seed(context, networking_notes, constraints),
                "boundary": "Drafting aid only; no contacts, email, LinkedIn, messages, calendar, or account systems were accessed.",
            }
        )
    return plan


def _networking_script_seed(context: str, networking_notes: str, constraints: list[str]) -> str:
    parts = [f"Ask for a short informational conversation about {context} using respectful, specific context."]
    if networking_notes:
        parts.append(f"Use supplied networking note: {networking_notes}.")
    if constraints:
        parts.append(f"Respect: {constraints[0]}.")
    return " ".join(parts)


def _interview_prep(
    career_goal: str,
    target_roles: list[str],
    current_experience: str,
    skills: list[str],
    projects: list[str],
    constraints: list[str],
) -> list[dict[str, str]]:
    prompts = [
        ("career_story", career_goal or "the target career goal"),
        ("role_fit", target_roles[0] if target_roles else "the target role"),
        ("project_depth", projects[0] if projects else "a relevant project"),
    ]
    prep = []
    for prompt_type, subject in prompts:
        note_parts = ["Practice manually; no interview was scheduled or recorded."]
        if current_experience:
            note_parts.append(f"Experience context: {current_experience}.")
        if skills:
            note_parts.append(f"Skills to weave in: {', '.join(skills[:3])}.")
        if constraints:
            note_parts.append(f"Constraint: {constraints[0]}.")
        prep.append({"promptType": prompt_type, "subject": subject, "practiceNote": " ".join(note_parts)})
    return prep


def _skill_gap_plan(
    career_goal: str,
    target_roles: list[str],
    skills: list[str],
    projects: list[str],
    education_notes: str,
    constraints: list[str],
) -> list[str]:
    plan = [
        f"Compare supplied skills against {target_roles[0]} expectations manually." if target_roles else "Name a target role before ranking skill gaps.",
        f"Use career goal as the filter: {career_goal}." if career_goal else "Clarify the career goal before choosing skill gaps.",
    ]
    if skills:
        plan.append(f"Existing supplied skills to preserve: {', '.join(skills[:5])}.")
    if projects:
        plan.append(f"Use project work to demonstrate gaps or strengths: {projects[0]}.")
    if education_notes:
        plan.append(f"Education context: {education_notes}.")
    if constraints:
        plan.append(f"Constraint: {constraints[0]}.")
    plan.append("No live job-market verification, course lookup, or certification validation was performed.")
    return plan


def _application_checklist(career_goal: str, resume_notes: str, job_search_notes: str, constraints: list[str]) -> list[str]:
    checklist = [
        "Review role fit manually before deciding whether to apply elsewhere.",
        "Check resume positioning and project evidence manually.",
        "Prepare tailored answers for why the role fits the career goal.",
    ]
    if career_goal:
        checklist.append(f"Career goal to keep visible: {career_goal}.")
    if resume_notes:
        checklist.append(f"Resume note to review manually: {resume_notes}.")
    if job_search_notes:
        checklist.append(f"Search note to consider manually: {job_search_notes}.")
    if constraints:
        checklist.append(f"Constraint: {constraints[0]}.")
    checklist.append("No application, form, message, resume upload, calendar event, task, or record was created.")
    return checklist[:8]


def _project_pitch_plan(projects: list[str], career_goal: str, target_roles: list[str], skills: list[str], constraints: list[str]) -> list[dict[str, str]]:
    project_list = projects or ["Project not yet supplied"]
    pitches = []
    for project in project_list[:4]:
        pitch_parts = [f"Describe {project} with problem, action, technical choices, and outcome caveats."]
        if career_goal:
            pitch_parts.append(f"Connect to career goal: {career_goal}.")
        if target_roles:
            pitch_parts.append(f"Role relevance: {target_roles[0]}.")
        if skills:
            pitch_parts.append(f"Skills to mention: {', '.join(skills[:3])}.")
        if constraints:
            pitch_parts.append(f"Constraint: {constraints[0]}.")
        pitches.append({"project": project, "pitchNote": " ".join(pitch_parts), "boundary": "Manual pitch note only; no portfolio, GitHub, file, or application system was accessed."})
    return pitches


def _next_actions(desired_output_type: str, thin_input: bool, high_stakes_context: bool) -> list[str]:
    actions = []
    if thin_input:
        actions.append("Add career goal detail, target roles, industries, experience, education, skills, projects, resume notes, search notes, networking notes, and constraints.")
    if desired_output_type == "resume_positioning":
        actions.append("Manually revise resume bullets and summary language outside this agent.")
    elif desired_output_type == "job_search_plan":
        actions.append("Build a small target list manually without treating this as live job-market verification.")
    elif desired_output_type == "networking_plan":
        actions.append("Review networking scripts manually; do not send them from this agent.")
    elif desired_output_type == "interview_prep":
        actions.append("Practice answers manually and verify any claims before using them.")
    elif desired_output_type == "skill_gap_plan":
        actions.append("Choose one skill gap to work on manually before adding more targets.")
    elif desired_output_type == "application_checklist":
        actions.append("Use the checklist manually; do not treat it as application submission or task creation.")
    elif desired_output_type == "project_pitch_plan":
        actions.append("Draft project stories manually and avoid unsupported outcome claims.")
    else:
        actions.append("Use this as local career planning and job-search preparation only.")
    if high_stakes_context:
        actions.append("Confirm legal, immigration, visa, salary-negotiation, employment-contract, or other high-stakes career decisions with official or qualified professional sources.")
    actions.append("Do not treat this response as job placement, interview, hiring, salary, legal, visa, or live job-market validation.")
    return actions[:5]


def _open_questions(
    career_goal: str,
    target_roles: list[str],
    target_industries: list[str],
    current_experience: str,
    education_notes: str,
    skills: list[str],
    projects: list[str],
    resume_notes: str,
    job_search_notes: str,
    networking_notes: str,
    constraints: list[str],
) -> list[str]:
    questions = []
    if not career_goal:
        questions.append("What career goal should anchor the plan?")
    if not target_roles:
        questions.append("Which roles should the plan target?")
    if not target_industries:
        questions.append("Which industries or contexts should be prioritized?")
    if not current_experience:
        questions.append("What experience should be positioned?")
    if not education_notes:
        questions.append("What education or training context should be included?")
    if not skills:
        questions.append("Which skills should be highlighted?")
    if not projects:
        questions.append("Which projects should support the career story?")
    if not resume_notes:
        questions.append("What resume notes, gaps, or bullets need review?")
    if not job_search_notes:
        questions.append("What job-search strategy notes should be considered?")
    if not networking_notes:
        questions.append("What networking context or scripts should be drafted?")
    if not constraints:
        questions.append("What constraints, risks, timing, location, eligibility, or workload limits matter?")
    return questions


def _warnings(thin_input: bool, high_stakes_context: bool) -> list[str]:
    warnings = []
    if thin_input:
        warnings.append("Career input is thin; output is a provisional local planning scaffold.")
    if high_stakes_context:
        warnings.append("Legal, immigration, visa, salary-negotiation, employment-contract, or high-stakes career decisions need official or qualified professional confirmation.")
    warnings.append("This response uses only request-provided data and does not verify live jobs, accounts, contacts, applications, interviews, salaries, hiring status, or market conditions.")
    return warnings


def _limitations(thin_input: bool, high_stakes_context: bool) -> list[str]:
    limitations = [
        "Based only on user-provided career goals, resume notes, job targets, co-op or internship plans, interview prep, networking notes, skills, projects, and constraints.",
        "No LinkedIn, Handshake, Indeed, company sites, Gmail, Calendar, contacts, school portals, job boards, GitHub, files, external services, paid APIs, accounts, or connectors were accessed.",
        "No browsing, scraping, job application submission, form submission, message sending, interview scheduling, task creation, record persistence, resume upload, file access, database write, shell execution, mutation, official career validation, legal validation, or certification was performed.",
        "No job placement, interview guarantee, hiring certainty, salary certainty, visa or legal validation, employment-law advice, live job-market verification, application outcome, networking response, or certification claim is made.",
    ]
    if thin_input:
        limitations.append("Thin input limits specificity; add role targets, industry notes, experience, education, skills, projects, resume notes, search notes, networking notes, and constraints.")
    if high_stakes_context:
        limitations.append("For legal, immigration, visa, salary-negotiation, employment-contract, or high-stakes career decisions, confirm with official sources or qualified professionals.")
    return limitations
