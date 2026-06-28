import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_career_agent import LocalCareerAgentService, LocalCareerRequest


def test_local_career_endpoint_returns_structured_plan():
    payload = app_module.LocalCareerInput(
        profileName="Local Career Profile",
        careerGoal="Prepare for robotics software internships and co-op conversations.",
        targetRoles=["Robotics software intern", "Computer vision intern"],
        targetIndustries=["Robotics", "Health technology"],
        currentExperience="Course projects and local planning work in robotics and software.",
        educationNotes="Engineering student building robotics and applied software experience.",
        skills=["Python", "C++", "Computer vision"],
        projects=["Vascular-Twin planning prototype", "Robot perception demo"],
        resumeNotes="Emphasize project evidence and manual review wording.",
        jobSearchNotes="Focus on a small manually reviewed target list.",
        networkingNotes="Prepare respectful informational conversation scripts.",
        constraints=["Manual planning only"],
        desiredOutputType="career_brief",
    )

    result = app_module.create_local_career_plan(payload)

    assert result["agentId"] == "local_career_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_career_planning"
    assert result["profileName"] == "Local Career Profile"
    assert result["careerGoal"] == "Prepare for robotics software internships and co-op conversations."
    assert result["desiredOutputType"] == "career_brief"
    assert result["careerFocus"]
    assert result["targetRoleSummary"]
    assert result["experienceSummary"]
    assert result["resumePositioning"]
    assert result["jobSearchPlan"]
    assert result["networkingPlan"]
    assert result["interviewPrep"]
    assert result["skillGapPlan"]
    assert result["applicationChecklist"]
    assert result["projectPitchPlan"]
    assert result["nextActions"]
    assert result["openQuestions"]
    assert result["warnings"]
    assert "Based only on user-provided career goals" in result["limitations"][0]
    assert result["safety"]["localOnly"] is True


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("career_brief", "career_brief"),
        ("resume_positioning", "resume_positioning"),
        ("job_search_plan", "job_search_plan"),
        ("networking_plan", "networking_plan"),
        ("interview_prep", "interview_prep"),
        ("skill_gap_plan", "skill_gap_plan"),
        ("application_checklist", "application_checklist"),
        ("project_pitch_plan", "project_pitch_plan"),
        (" INTERVIEW_PREP ", "interview_prep"),
    ],
)
def test_local_career_supported_output_types_normalize(requested, expected):
    service = LocalCareerAgentService()

    result = service.create_plan(
        LocalCareerRequest(
            career_goal="Prepare for robotics internships.",
            desired_output_type=requested,
        )
    )

    assert result["desiredOutputType"] == expected


def test_local_career_unsupported_output_type_falls_back_safely():
    service = LocalCareerAgentService()

    result = service.create_plan(
        LocalCareerRequest(
            career_goal="Prepare for internships.",
            desired_output_type="auto_apply_and_message",
        )
    )

    assert result["desiredOutputType"] == "career_brief"
    assert result["safety"]["jobApplicationSubmission"] is False
    assert result["safety"]["messaging"] is False
    assert result["safety"]["resumeUpload"] is False


def test_local_career_thin_input_reports_warnings_and_questions():
    service = LocalCareerAgentService()

    result = service.create_plan(LocalCareerRequest(career_goal=""))

    assert any("input is thin" in warning.lower() for warning in result["warnings"])
    assert any("Thin input limits specificity" in limitation for limitation in result["limitations"])
    assert result["openQuestions"]
    assert result["nextActions"]


def test_local_career_output_includes_resume_job_search_networking_interview_skill_and_project_sections():
    service = LocalCareerAgentService()

    result = service.create_plan(
        LocalCareerRequest(
            career_goal="Prepare for software internships.",
            target_roles=["Software intern"],
            target_industries=["Robotics"],
            current_experience="Project work and coursework.",
            skills=["Python", "Testing"],
            projects=["Robot perception demo"],
            desired_output_type="job_search_plan",
        )
    )

    assert result["resumePositioning"]
    assert result["jobSearchPlan"]
    assert result["networkingPlan"]
    assert result["interviewPrep"]
    assert result["skillGapPlan"]
    assert result["applicationChecklist"]
    assert result["projectPitchPlan"]


def test_local_career_output_does_not_claim_account_actions_live_verification_or_outcomes():
    service = LocalCareerAgentService()

    result = service.create_plan(
        LocalCareerRequest(
            career_goal="Apply to jobs, network, schedule interviews, upload resume, and verify live job market.",
            desired_output_type="application_checklist",
        )
    )
    output_text = str(result).lower()
    forbidden_claims = [
        "account accessed",
        "live job verified",
        "application submitted",
        "message sent",
        "interview scheduled",
        "resume uploaded",
        "job placement guaranteed",
        "interview guaranteed",
        "hiring guaranteed",
        "salary guaranteed",
    ]

    assert all(claim not in output_text for claim in forbidden_claims)
    assert "no linkedin" in output_text
    assert "no browsing" in output_text
    assert "no job placement" in output_text
    assert "no job boards" in output_text


def test_local_career_high_stakes_inputs_include_professional_confirmation_limitations():
    service = LocalCareerAgentService()

    result = service.create_plan(
        LocalCareerRequest(
            career_goal="Plan visa, legal, salary negotiation, employment contract, and work authorization decisions.",
            desired_output_type="career_brief",
        )
    )

    assert any("qualified professional confirmation" in warning for warning in result["warnings"])
    assert any("qualified professionals" in limitation for limitation in result["limitations"])
    assert any("qualified professional sources" in action for action in result["nextActions"])


def test_local_career_safety_flags_disable_connectors_accounts_browsing_uploads_persistence_mutation_and_certification():
    service = LocalCareerAgentService()

    result = service.create_plan(LocalCareerRequest(career_goal="Prepare for internships."))
    safety = result["safety"]

    assert safety["localOnly"] is True
    assert safety["responseOnly"] is True
    assert safety["manualInputOnly"] is True
    assert safety["externalServices"] is False
    assert safety["connectors"] is False
    assert safety["oauth"] is False
    assert safety["accountAccess"] is False
    assert safety["webBrowsing"] is False
    assert safety["paidApis"] is False
    assert safety["jobBoardAccess"] is False
    assert safety["schoolPortalAccess"] is False
    assert safety["emailSending"] is False
    assert safety["calendarAccess"] is False
    assert safety["contactAccess"] is False
    assert safety["jobApplicationSubmission"] is False
    assert safety["resumeUpload"] is False
    assert safety["messaging"] is False
    assert safety["fileReads"] is False
    assert safety["fileWrites"] is False
    assert safety["dbWrites"] is False
    assert safety["taskPersistence"] is False
    assert safety["shellExecution"] is False
    assert safety["mutation"] is False
    assert safety["officialCareerValidation"] is False
    assert safety["legalValidation"] is False
    assert safety["certificationClaims"] is False


def test_local_career_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_career_agent").local_career_agent).lower()
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


def test_local_career_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalCareerInput.model_validate(
            {
                "careerGoal": "Prepare for internships.",
                "linkedinToken": "not allowed",
            }
        )


def test_local_career_requires_career_goal_in_endpoint_input():
    with pytest.raises(ValidationError):
        app_module.LocalCareerInput.model_validate({"profileName": "Missing goal"})


def test_local_career_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/career/local-plan")
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
