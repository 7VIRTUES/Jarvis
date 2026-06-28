import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_projects_portfolio_agent import LocalProjectsPortfolioAgentService, LocalProjectsPortfolioRequest


def test_local_projects_portfolio_endpoint_returns_structured_plan():
    payload = app_module.LocalProjectsPortfolioInput(
        profileName="Local Portfolio Profile",
        portfolioGoal="Prepare a project portfolio plan for robotics software internship conversations.",
        targetAudience="Recruiters and technical reviewers reading user-provided portfolio notes.",
        targetRoles=["Robotics software intern", "Computer vision intern"],
        projectNotes=["Vascular-Twin planning prototype", "Robot perception demo", "Local Jarvis response-agent work"],
        skills=["Python", "C++", "Computer vision", "Technical writing"],
        proofArtifacts=["Case study draft", "Demo outline", "Screenshot checklist"],
        currentStatus="Projects need clearer summaries and manually reviewed proof artifacts.",
        constraints=["Manual planning only"],
        priorities=["Show technical depth", "Keep claims human-reviewed"],
        timeline="Prepare a first portfolio pass before internship outreach.",
        desiredOutputType="portfolio_brief",
    )

    result = app_module.create_local_projects_portfolio_plan(payload)

    assert result["agentId"] == "local_projects_portfolio_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_projects_portfolio_planning"
    assert result["profileName"] == "Local Portfolio Profile"
    assert result["portfolioGoal"] == "Prepare a project portfolio plan for robotics software internship conversations."
    assert result["desiredOutputType"] == "portfolio_brief"
    assert result["portfolioFocus"]
    assert result["audienceSummary"]
    assert result["projectInventory"]
    assert result["projectRoadmap"]
    assert result["githubProfilePlan"]
    assert result["resumeProjectPitch"]
    assert result["caseStudyOutline"]
    assert result["portfolioWebsiteCopy"]
    assert result["proofOfWorkPlan"]
    assert result["prioritizationNotes"]
    assert result["nextActions"]
    assert result["openQuestions"]
    assert result["warnings"]
    assert "Based only on user-provided project" in result["limitations"][0]
    assert result["safety"]["localOnly"] is True


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("portfolio_brief", "portfolio_brief"),
        ("project_inventory", "project_inventory"),
        ("project_roadmap", "project_roadmap"),
        ("github_profile_plan", "github_profile_plan"),
        ("resume_project_pitch", "resume_project_pitch"),
        ("case_study_outline", "case_study_outline"),
        ("portfolio_website_copy", "portfolio_website_copy"),
        ("proof_of_work_plan", "proof_of_work_plan"),
        (" CASE_STUDY_OUTLINE ", "case_study_outline"),
    ],
)
def test_local_projects_portfolio_supported_output_types_normalize(requested, expected):
    service = LocalProjectsPortfolioAgentService()

    result = service.create_plan(
        LocalProjectsPortfolioRequest(
            portfolio_goal="Prepare a manual projects portfolio plan.",
            desired_output_type=requested,
        )
    )

    assert result["desiredOutputType"] == expected


def test_local_projects_portfolio_unsupported_output_type_falls_back_safely():
    service = LocalProjectsPortfolioAgentService()

    result = service.create_plan(
        LocalProjectsPortfolioRequest(
            portfolio_goal="Prepare portfolio notes.",
            desired_output_type="commit_push_upload_and_publish",
        )
    )

    assert result["desiredOutputType"] == "portfolio_brief"
    assert result["safety"]["githubAccess"] is False
    assert result["safety"]["commitActions"] is False
    assert result["safety"]["publishingActions"] is False


def test_local_projects_portfolio_thin_input_reports_warnings_and_questions():
    service = LocalProjectsPortfolioAgentService()

    result = service.create_plan(LocalProjectsPortfolioRequest(portfolio_goal=""))

    assert any("input is thin" in warning.lower() for warning in result["warnings"])
    assert any("Thin input limits specificity" in limitation for limitation in result["limitations"])
    assert result["openQuestions"]
    assert result["nextActions"]


def test_local_projects_portfolio_output_includes_inventory_roadmap_profile_pitch_case_study_website_and_proof_sections():
    service = LocalProjectsPortfolioAgentService()

    result = service.create_plan(
        LocalProjectsPortfolioRequest(
            portfolio_goal="Position robotics projects for internship review.",
            target_audience="Technical reviewers",
            target_roles=["Robotics intern"],
            project_notes=["Robot perception demo", "Portfolio website plan"],
            skills=["Python", "Computer vision"],
            proof_artifacts=["Case study", "Demo outline"],
            current_status="Manual polish needed.",
            desired_output_type="project_roadmap",
        )
    )

    assert result["projectInventory"]
    assert result["projectRoadmap"]
    assert result["githubProfilePlan"]
    assert result["resumeProjectPitch"]
    assert result["caseStudyOutline"]
    assert result["portfolioWebsiteCopy"]
    assert result["proofOfWorkPlan"]
    assert result["prioritizationNotes"]


def test_local_projects_portfolio_output_does_not_claim_repo_access_file_reads_github_verification_or_publishing():
    service = LocalProjectsPortfolioAgentService()

    result = service.create_plan(
        LocalProjectsPortfolioRequest(
            portfolio_goal="Inspect GitHub, read repos, commit, push, upload, publish, validate code, and guarantee hiring.",
            desired_output_type="github_profile_plan",
        )
    )
    output_text = str(result).lower()
    forbidden_claims = [
        "repo accessed",
        "file contents read",
        "github verified",
        "commit created",
        "push completed",
        "uploaded",
        "published",
        "code review passed",
        "project completed",
        "hiring guaranteed",
        "portfolio certified",
    ]

    assert all(claim not in output_text for claim in forbidden_claims)
    assert "no github" in output_text
    assert "no file reads" in output_text
    assert "no live github verification" in output_text
    assert "no github access" in output_text


def test_local_projects_portfolio_high_stakes_inputs_include_human_or_professional_review_limitations():
    service = LocalProjectsPortfolioAgentService()

    result = service.create_plan(
        LocalProjectsPortfolioRequest(
            portfolio_goal="Prepare employment, legal, IP, copyright, academic, and public claim project notes.",
            desired_output_type="portfolio_brief",
        )
    )

    assert any("professional review" in warning for warning in result["warnings"])
    assert any("qualified professionals" in limitation for limitation in result["limitations"])
    assert any("professional" in action for action in result["nextActions"])


def test_local_projects_portfolio_safety_flags_disable_connectors_accounts_browsing_github_repo_files_persistence_mutation_and_certification():
    service = LocalProjectsPortfolioAgentService()

    result = service.create_plan(LocalProjectsPortfolioRequest(portfolio_goal="Prepare a portfolio plan."))
    safety = result["safety"]

    assert safety["localOnly"] is True
    assert safety["responseOnly"] is True
    assert safety["manualInputOnly"] is True
    assert safety["externalServices"] is False
    assert safety["connectors"] is False
    assert safety["oauth"] is False
    assert safety["OAuth"] is False
    assert safety["accountAccess"] is False
    assert safety["webBrowsing"] is False
    assert safety["paidApis"] is False
    assert safety["githubAccess"] is False
    assert safety["repoInspection"] is False
    assert safety["fileReads"] is False
    assert safety["fileWrites"] is False
    assert safety["dbWrites"] is False
    assert safety["taskPersistence"] is False
    assert safety["shellExecution"] is False
    assert safety["commitActions"] is False
    assert safety["pushActions"] is False
    assert safety["publishingActions"] is False
    assert safety["uploadActions"] is False
    assert safety["mutation"] is False
    assert safety["officialValidation"] is False
    assert safety["codeReviewValidation"] is False
    assert safety["hiringOutcomeGuarantee"] is False
    assert safety["certificationClaims"] is False


def test_local_projects_portfolio_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_projects_portfolio_agent").local_projects_portfolio_agent).lower()
    forbidden = [
        "requests",
        "httpx",
        "urllib.request",
        "socket",
        "subprocess",
        "open(",
        "read_text",
        "read_bytes",
        "write_text",
        ".write(",
        "sqlite",
        "taskqueue",
        "gmail.",
        "google_calendar",
        "smtp.",
        "imap.",
        "openai",
        "anthropic",
        "gemini",
    ]

    assert all(token not in source for token in forbidden)


def test_local_projects_portfolio_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalProjectsPortfolioInput.model_validate(
            {
                "portfolioGoal": "Prepare a portfolio plan.",
                "githubToken": "not allowed",
            }
        )


def test_local_projects_portfolio_requires_portfolio_goal_in_endpoint_input():
    with pytest.raises(ValidationError):
        app_module.LocalProjectsPortfolioInput.model_validate({"profileName": "Missing goal"})


def test_local_projects_portfolio_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(
        route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/projects-portfolio/local-plan"
    )
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
