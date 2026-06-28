from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_projects_portfolio_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_projects_portfolio_planning"
SUPPORTED_OUTPUT_TYPES = (
    "portfolio_brief",
    "project_inventory",
    "project_roadmap",
    "github_profile_plan",
    "resume_project_pitch",
    "case_study_outline",
    "portfolio_website_copy",
    "proof_of_work_plan",
)


@dataclass(frozen=True)
class LocalProjectsPortfolioRequest:
    portfolio_goal: str
    profile_name: str = ""
    target_audience: str = ""
    target_roles: list[str] = field(default_factory=list)
    project_notes: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    proof_artifacts: list[str] = field(default_factory=list)
    current_status: str = ""
    constraints: list[str] = field(default_factory=list)
    priorities: list[str] = field(default_factory=list)
    timeline: str = ""
    desired_output_type: str = "portfolio_brief"


class LocalProjectsPortfolioAgentService:
    def create_plan(self, request: LocalProjectsPortfolioRequest) -> dict[str, Any]:
        profile_name = _clean_text(request.profile_name) or "Local projects portfolio"
        portfolio_goal = _clean_text(request.portfolio_goal)
        target_audience = _clean_text(request.target_audience)
        target_roles = _clean_list(request.target_roles)
        project_notes = _clean_list(request.project_notes, limit=12)
        skills = _clean_list(request.skills, limit=12)
        proof_artifacts = _clean_list(request.proof_artifacts, limit=12)
        current_status = _clean_text(request.current_status)
        constraints = _clean_list(request.constraints)
        priorities = _clean_list(request.priorities)
        timeline = _clean_text(request.timeline)
        desired_output_type = _normalize_output_type(request.desired_output_type)
        thin_input = _thin_input(
            portfolio_goal,
            target_audience,
            target_roles,
            project_notes,
            skills,
            proof_artifacts,
            current_status,
            constraints,
            priorities,
            timeline,
        )
        high_stakes_context = _high_stakes_context(portfolio_goal, target_audience, project_notes, constraints, priorities)

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "profileName": profile_name,
            "portfolioGoal": portfolio_goal,
            "desiredOutputType": desired_output_type,
            "portfolioFocus": _portfolio_focus(portfolio_goal, target_audience, target_roles, desired_output_type, thin_input),
            "audienceSummary": _audience_summary(target_audience, target_roles, priorities, thin_input),
            "projectInventory": _project_inventory(project_notes, skills, proof_artifacts, current_status),
            "projectRoadmap": _project_roadmap(portfolio_goal, project_notes, current_status, constraints, priorities, timeline),
            "githubProfilePlan": _github_profile_plan(portfolio_goal, target_roles, skills, proof_artifacts, constraints),
            "resumeProjectPitch": _resume_project_pitch(project_notes, skills, target_roles, priorities),
            "caseStudyOutline": _case_study_outline(project_notes, skills, proof_artifacts, constraints),
            "portfolioWebsiteCopy": _portfolio_website_copy(profile_name, portfolio_goal, target_audience, project_notes, skills),
            "proofOfWorkPlan": _proof_of_work_plan(project_notes, proof_artifacts, skills, timeline, constraints),
            "prioritizationNotes": _prioritization_notes(project_notes, priorities, constraints, timeline),
            "nextActions": _next_actions(desired_output_type, thin_input, high_stakes_context),
            "openQuestions": _open_questions(
                portfolio_goal,
                target_audience,
                target_roles,
                project_notes,
                skills,
                proof_artifacts,
                current_status,
                constraints,
                priorities,
                timeline,
            ),
            "warnings": _warnings(thin_input, high_stakes_context),
            "limitations": _limitations(thin_input, high_stakes_context),
            "safety": local_projects_portfolio_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_projects_portfolio_dashboard_summary()


def local_projects_portfolio_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Projects / Portfolio Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/projects-portfolio/local-plan",
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
        "githubAccess": False,
        "repoInspection": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "commitActions": False,
        "pushActions": False,
        "publishingActions": False,
        "uploadActions": False,
        "mutation": False,
        "officialValidation": False,
        "codeReviewValidation": False,
        "hiringOutcomeGuarantee": False,
        "certificationClaims": False,
        "limitations": ["based only on user-provided project and portfolio notes"],
    }


def local_projects_portfolio_safety() -> dict[str, bool]:
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
        "githubAccess": False,
        "repoInspection": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "commitActions": False,
        "pushActions": False,
        "publishingActions": False,
        "uploadActions": False,
        "mutation": False,
        "officialValidation": False,
        "codeReviewValidation": False,
        "hiringOutcomeGuarantee": False,
        "certificationClaims": False,
    }


def _normalize_output_type(value: str) -> str:
    normalized = (value or "portfolio_brief").strip().lower()
    return normalized if normalized in SUPPORTED_OUTPUT_TYPES else "portfolio_brief"


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
    portfolio_goal: str,
    target_audience: str,
    target_roles: list[str],
    project_notes: list[str],
    skills: list[str],
    proof_artifacts: list[str],
    current_status: str,
    constraints: list[str],
    priorities: list[str],
    timeline: str,
) -> bool:
    return not any(
        [
            portfolio_goal,
            target_audience,
            target_roles,
            project_notes,
            skills,
            proof_artifacts,
            current_status,
            constraints,
            priorities,
            timeline,
        ]
    )


def _high_stakes_context(
    portfolio_goal: str,
    target_audience: str,
    project_notes: list[str],
    constraints: list[str],
    priorities: list[str],
) -> bool:
    text = " ".join([portfolio_goal, target_audience, " ".join(project_notes), " ".join(constraints), " ".join(priorities)]).lower()
    terms = (
        "employment",
        "hiring",
        "legal",
        "copyright",
        "license",
        "ip",
        "patent",
        "academic",
        "public claim",
        "confidential",
        "nda",
        "client",
        "official",
    )
    return any(term in text for term in terms)


def _portfolio_focus(
    portfolio_goal: str,
    target_audience: str,
    target_roles: list[str],
    desired_output_type: str,
    thin_input: bool,
) -> list[str]:
    if thin_input:
        return [
            "Capture the portfolio goal, audience, target roles, projects, skills, proof artifacts, constraints, and timeline before making positioning choices.",
            "Keep the result as manual planning and drafting only because no GitHub, repo, file, account, website, or analytics source is inspected.",
        ]
    focus = [f"Primary request: {portfolio_goal}.", f"Requested output shape: {desired_output_type}."]
    if target_audience:
        focus.append(f"Audience from user input: {target_audience}.")
    if target_roles:
        focus.append("Target roles to support: " + "; ".join(target_roles) + ".")
    focus.append("Use this as a manual positioning aid, not live verification, code review, hiring prediction, or certification.")
    return focus


def _audience_summary(target_audience: str, target_roles: list[str], priorities: list[str], thin_input: bool) -> list[str]:
    if thin_input:
        return ["Audience summary is limited until the user provides target readers, roles, and priorities."]
    summary = []
    if target_audience:
        summary.append(f"Primary audience: {target_audience}.")
    if target_roles:
        summary.append("Role lens: " + "; ".join(target_roles) + ".")
    if priorities:
        summary.append("Priority lens: " + "; ".join(priorities) + ".")
    if not summary:
        summary.append("Define the intended reader before choosing project order or project pitch emphasis.")
    return summary


def _project_inventory(
    project_notes: list[str],
    skills: list[str],
    proof_artifacts: list[str],
    current_status: str,
) -> list[dict[str, str]]:
    projects = project_notes or ["Project to define manually"]
    inventory: list[dict[str, str]] = []
    for index, project in enumerate(projects[:8], start=1):
        inventory.append(
            {
                "project": project,
                "positioning": "Describe the problem, user, contribution, outcome, and evidence from user-provided notes.",
                "skillsToHighlight": "; ".join(skills) if skills else "Add skills demonstrated by this project manually.",
                "proofArtifacts": "; ".join(proof_artifacts) if proof_artifacts else "Add screenshots, demos, writeups, links, metrics, or notes manually.",
                "status": current_status or f"Project {index} needs a user-provided status.",
                "manualChecks": "Confirm public claims, ownership, confidentiality, and technical accuracy outside Jarvis before publishing.",
            }
        )
    return inventory


def _project_roadmap(
    portfolio_goal: str,
    project_notes: list[str],
    current_status: str,
    constraints: list[str],
    priorities: list[str],
    timeline: str,
) -> list[str]:
    roadmap = [
        "Choose the smallest set of projects that directly supports the portfolio goal.",
        "For each selected project, prepare a problem statement, contribution summary, evidence list, and next polishing step.",
        "Separate ready-to-present work from work that still needs cleanup, screenshots, writeups, demos, or human review.",
    ]
    if portfolio_goal:
        roadmap.insert(0, f"Roadmap anchor: {portfolio_goal}.")
    if project_notes:
        roadmap.append("Candidate projects from user input: " + "; ".join(project_notes[:6]) + ".")
    if current_status:
        roadmap.append(f"Current status from user input: {current_status}.")
    if priorities:
        roadmap.append("Priorities to protect: " + "; ".join(priorities) + ".")
    if constraints:
        roadmap.append("Constraints to respect: " + "; ".join(constraints) + ".")
    if timeline:
        roadmap.append(f"Timeline to use manually: {timeline}.")
    return roadmap


def _github_profile_plan(
    portfolio_goal: str,
    target_roles: list[str],
    skills: list[str],
    proof_artifacts: list[str],
    constraints: list[str],
) -> list[str]:
    return [
        "Draft a profile headline that states the user's focus without claiming verified activity or inspected repository quality.",
        f"Positioning goal: {portfolio_goal or 'Add a portfolio positioning goal manually.'}",
        "Target role angle: " + ("; ".join(target_roles) if target_roles else "Add target roles manually."),
        "Skills to surface: " + ("; ".join(skills) if skills else "Add skills from user-provided notes manually."),
        "Proof to reference: " + ("; ".join(proof_artifacts) if proof_artifacts else "Add proof artifacts manually; no links or repositories are checked."),
        "Constraint check: " + ("; ".join(constraints) if constraints else "Review confidential, academic, client, IP, and public-claim limits manually."),
    ]


def _resume_project_pitch(
    project_notes: list[str],
    skills: list[str],
    target_roles: list[str],
    priorities: list[str],
) -> list[dict[str, str]]:
    projects = project_notes or ["Project to pitch manually"]
    pitches: list[dict[str, str]] = []
    for project in projects[:5]:
        pitches.append(
            {
                "project": project,
                "resumeAngle": "Frame the project as problem, action, tool or skill, and result based only on user-provided facts.",
                "roleFit": "; ".join(target_roles) if target_roles else "Add the role this pitch should support.",
                "skills": "; ".join(skills) if skills else "Add concrete skills demonstrated by the project.",
                "priority": "; ".join(priorities) if priorities else "Emphasize clarity, evidence, and honest scope.",
            }
        )
    return pitches


def _case_study_outline(
    project_notes: list[str],
    skills: list[str],
    proof_artifacts: list[str],
    constraints: list[str],
) -> list[dict[str, list[str] | str]]:
    projects = project_notes or ["Project case study to define manually"]
    outlines: list[dict[str, list[str] | str]] = []
    for project in projects[:4]:
        outlines.append(
            {
                "project": project,
                "sections": [
                    "Context and user problem",
                    "Goal and constraints",
                    "Personal contribution",
                    "Technical or design choices",
                    "Evidence and result",
                    "What changed after review",
                    "What to improve next",
                ],
                "skillsToName": skills or ["Add skills from user notes"],
                "proofToGather": proof_artifacts or ["Add proof artifacts manually"],
                "manualReviewNeeded": "Check confidentiality, IP/copyright, academic rules, public claims, and technical accuracy before sharing.",
                "constraints": "; ".join(constraints) if constraints else "No constraints provided.",
            }
        )
    return outlines


def _portfolio_website_copy(
    profile_name: str,
    portfolio_goal: str,
    target_audience: str,
    project_notes: list[str],
    skills: list[str],
) -> dict[str, list[str] | str]:
    return {
        "heroDraft": f"{profile_name}: {portfolio_goal or 'project portfolio focused on clear proof of work'}.",
        "audienceLine": target_audience or "For reviewers who want concise project context, honest scope, and visible evidence.",
        "projectSectionIntro": "Selected projects from user-provided notes: " + ("; ".join(project_notes[:5]) if project_notes else "add selected projects manually."),
        "skillsLine": "Skills to highlight: " + ("; ".join(skills) if skills else "add skills manually."),
        "copyNotes": [
            "Keep claims specific and traceable to user-provided facts.",
            "Avoid claiming repository quality, live verification, hiring outcomes, or project completion unless a human has confirmed the claim.",
            "Use short project summaries that link goal, contribution, evidence, and next step.",
        ],
    }


def _proof_of_work_plan(
    project_notes: list[str],
    proof_artifacts: list[str],
    skills: list[str],
    timeline: str,
    constraints: list[str],
) -> list[str]:
    plan = [
        "Map each project to one visible proof item such as a short demo note, screenshot list, case study, README summary, or project pitch.",
        "Prioritize proof that shows the user's contribution, constraints, process, and result.",
        "Keep proof truthful and human-reviewed before sharing publicly.",
    ]
    if project_notes:
        plan.append("Projects to cover: " + "; ".join(project_notes[:6]) + ".")
    if proof_artifacts:
        plan.append("Existing proof artifacts from user input: " + "; ".join(proof_artifacts) + ".")
    if skills:
        plan.append("Skills to demonstrate: " + "; ".join(skills) + ".")
    if timeline:
        plan.append(f"Timeline for manual polish: {timeline}.")
    if constraints:
        plan.append("Proof constraints to respect: " + "; ".join(constraints) + ".")
    return plan


def _prioritization_notes(project_notes: list[str], priorities: list[str], constraints: list[str], timeline: str) -> list[str]:
    notes = [
        "Prefer projects with clear user value, visible contribution, explainable tradeoffs, and safe public evidence.",
        "Down-rank projects that need sensitive material, unconfirmed claims, unclear ownership, or major unfinished work.",
    ]
    if project_notes:
        notes.append("Start with a manual ranking of: " + "; ".join(project_notes[:8]) + ".")
    if priorities:
        notes.append("Priority criteria: " + "; ".join(priorities) + ".")
    if constraints:
        notes.append("Constraint criteria: " + "; ".join(constraints) + ".")
    if timeline:
        notes.append(f"Timeline pressure: {timeline}.")
    return notes


def _next_actions(desired_output_type: str, thin_input: bool, high_stakes_context: bool) -> list[str]:
    actions = [
        f"Review the {desired_output_type} response and mark which claims need human confirmation.",
        "Add missing manual notes for audience, target roles, projects, skills, proof artifacts, constraints, priorities, and timeline.",
        "Confirm project ownership, public-claim accuracy, technical correctness, confidentiality, and employment relevance outside Jarvis.",
    ]
    if thin_input:
        actions.insert(0, "Add enough manual project and portfolio context before using this for a resume, profile, or public page.")
    if high_stakes_context:
        actions.append("Ask appropriate human, professional, academic, legal, or reviewer sources to confirm high-stakes employment, IP/copyright, academic, or public-claim details.")
    return actions


def _open_questions(
    portfolio_goal: str,
    target_audience: str,
    target_roles: list[str],
    project_notes: list[str],
    skills: list[str],
    proof_artifacts: list[str],
    current_status: str,
    constraints: list[str],
    priorities: list[str],
    timeline: str,
) -> list[str]:
    questions = []
    if not portfolio_goal:
        questions.append("What portfolio outcome should this plan support?")
    if not target_audience:
        questions.append("Who is the intended reader: recruiter, hiring manager, collaborator, professor, client, or general audience?")
    if not target_roles:
        questions.append("Which roles or opportunity types should the projects support?")
    if not project_notes:
        questions.append("Which projects should be included, and what did the user contribute to each?")
    if not skills:
        questions.append("Which skills should each project demonstrate?")
    if not proof_artifacts:
        questions.append("What proof artifacts are available from user-provided notes?")
    if not current_status:
        questions.append("Which projects are ready, rough, paused, private, or still in progress?")
    if not constraints:
        questions.append("What confidentiality, academic, IP/copyright, employer, or public-claim limits apply?")
    if not priorities:
        questions.append("Which priority matters most: clarity, technical depth, role fit, polish, speed, or proof?")
    if not timeline:
        questions.append("What timeline should guide project cleanup and portfolio updates?")
    return questions[:8]


def _warnings(thin_input: bool, high_stakes_context: bool) -> list[str]:
    warnings = [
        "No GitHub, local repos, files, project registry, source code, commits, branches, websites, analytics, resumes, accounts, or external services are inspected.",
        "The response does not verify project quality, technical correctness, live GitHub state, portfolio quality, hiring outcomes, project completion, code review status, or official validation.",
    ]
    if thin_input:
        warnings.insert(0, "The project and portfolio input is thin; results are a planning scaffold rather than a specific portfolio recommendation.")
    if high_stakes_context:
        warnings.append("Employment, legal, IP/copyright, academic, and public-claim concerns need appropriate human or professional review.")
    return warnings


def _limitations(thin_input: bool, high_stakes_context: bool) -> list[str]:
    limitations = [
        "Based only on user-provided project, portfolio, skill, proof, audience, role, constraint, priority, and timeline notes.",
        "No GitHub access, repo inspection, file reads, file writes, account access, browsing, scraping, commits, pushes, uploads, publishing, persistence, shell execution, or mutation.",
        "No live GitHub verification, portfolio quality certification, hiring outcome certainty, project completion claim, technical correctness validation, code review validation, official validation, or certification claim.",
    ]
    if thin_input:
        limitations.append("Thin input limits specificity until the user supplies concrete projects, skills, proof artifacts, audience, and constraints.")
    if high_stakes_context:
        limitations.append("Employment, legal, IP/copyright, academic, and public-claim details should be confirmed by appropriate humans or qualified professionals.")
    return limitations
