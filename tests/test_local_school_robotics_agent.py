import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_school_robotics_agent import LocalSchoolRoboticsAgentService, LocalSchoolRoboticsRequest


def test_local_school_robotics_endpoint_returns_structured_plan():
    payload = app_module.LocalSchoolRoboticsInput(
        studentName="Local Student",
        schoolName="Northeastern",
        programName="Robotics-focused engineering plan",
        termOrTimeline="Next two academic terms",
        academicGoal="Prepare for robotics research, Vascular-Twin planning, and a stronger co-op search.",
        roboticsFocus="Robot perception, controls, simulation, and applied health robotics.",
        courses=["Robotics foundations", "Computer vision", "Control systems"],
        professorsOrLabs=["User-provided robotics lab note"],
        projects=["Vascular-Twin planning prototype"],
        constraints=["Manual planning only"],
        resources=["Advisor notes", "Campus career center notes"],
        currentPreparation="Completed introductory programming and early robotics reading.",
        desiredOutputType="school_brief",
    )

    result = app_module.create_local_school_robotics_plan(payload)

    assert result["agentId"] == "local_school_robotics_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_school_robotics_planning"
    assert result["studentName"] == "Local Student"
    assert result["schoolName"] == "Northeastern"
    assert result["programName"] == "Robotics-focused engineering plan"
    assert result["desiredOutputType"] == "school_brief"
    assert result["academicFocus"]
    assert result["roboticsFocus"]
    assert result["timelineSummary"]
    assert result["coursePlan"]
    assert result["roboticsPrepPlan"]
    assert result["researchOutreachPlan"]
    assert result["projectRoadmap"]
    assert result["studySchedule"]
    assert result["coopPrepPlan"]
    assert result["campusResourcePlan"]
    assert result["nextActions"]
    assert result["openQuestions"]
    assert result["warnings"]
    assert "Based only on user-provided school, robotics" in result["limitations"][0]
    assert result["safety"]["localOnly"] is True


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("school_brief", "school_brief"),
        ("course_plan", "course_plan"),
        ("robotics_prep_plan", "robotics_prep_plan"),
        ("research_outreach_plan", "research_outreach_plan"),
        ("project_roadmap", "project_roadmap"),
        ("study_schedule", "study_schedule"),
        ("coop_prep_plan", "coop_prep_plan"),
        ("campus_resource_plan", "campus_resource_plan"),
        (" STUDY_SCHEDULE ", "study_schedule"),
    ],
)
def test_local_school_robotics_supported_output_types_normalize(requested, expected):
    service = LocalSchoolRoboticsAgentService()

    result = service.create_plan(
        LocalSchoolRoboticsRequest(
            academic_goal="Prepare for robotics coursework and project planning.",
            desired_output_type=requested,
        )
    )

    assert result["desiredOutputType"] == expected


def test_local_school_robotics_unsupported_output_type_falls_back_safely():
    service = LocalSchoolRoboticsAgentService()

    result = service.create_plan(
        LocalSchoolRoboticsRequest(
            academic_goal="Plan robotics coursework.",
            desired_output_type="auto_register_and_apply",
        )
    )

    assert result["desiredOutputType"] == "school_brief"
    assert result["safety"]["registrarAccess"] is False
    assert result["safety"]["emailSending"] is False
    assert result["safety"]["jobApplicationSubmission"] is False


def test_local_school_robotics_thin_input_reports_warnings_and_questions():
    service = LocalSchoolRoboticsAgentService()

    result = service.create_plan(LocalSchoolRoboticsRequest(academic_goal=""))

    assert any("input is thin" in warning.lower() for warning in result["warnings"])
    assert any("Thin input limits specificity" in limitation for limitation in result["limitations"])
    assert result["openQuestions"]
    assert result["nextActions"]


def test_local_school_robotics_output_includes_school_robotics_research_project_study_and_coop_sections():
    service = LocalSchoolRoboticsAgentService()

    result = service.create_plan(
        LocalSchoolRoboticsRequest(
            academic_goal="Prepare for robotics research and co-op.",
            robotics_focus="Robot perception and controls",
            courses=["Computer vision", "Controls"],
            professors_or_labs=["User-provided robotics lab note"],
            projects=["Vascular-Twin planning prototype"],
            resources=["Career center notes"],
            desired_output_type="robotics_prep_plan",
        )
    )

    assert result["coursePlan"]
    assert result["roboticsPrepPlan"]
    assert result["researchOutreachPlan"]
    assert result["projectRoadmap"]
    assert result["studySchedule"]
    assert result["coopPrepPlan"]
    assert result["campusResourcePlan"]


def test_local_school_robotics_output_does_not_claim_school_actions_or_validation():
    service = LocalSchoolRoboticsAgentService()

    result = service.create_plan(
        LocalSchoolRoboticsRequest(
            academic_goal="Plan course registration, professor outreach, research placement, and co-op prep.",
            desired_output_type="research_outreach_plan",
        )
    )
    output_text = str(result).lower()
    forbidden_claims = [
        "portal accessed",
        "course availability verified",
        "email sent",
        "class registered",
        "job submitted",
        "official academic validation complete",
        "admission guaranteed",
        "graduation guaranteed",
        "professor response guaranteed",
    ]

    assert all(claim not in output_text for claim in forbidden_claims)
    assert "no northeastern systems" in output_text
    assert "no browsing" in output_text
    assert "no admission" in output_text
    assert "no registration" in output_text


def test_local_school_robotics_high_stakes_inputs_include_official_confirmation_limitations():
    service = LocalSchoolRoboticsAgentService()

    result = service.create_plan(
        LocalSchoolRoboticsRequest(
            academic_goal="Plan graduation, financial aid, visa, legal, medical, and employment steps.",
            desired_output_type="campus_resource_plan",
        )
    )

    assert any("official school or professional confirmation" in warning for warning in result["warnings"])
    assert any("official school offices or qualified professionals" in limitation for limitation in result["limitations"])
    assert any("official school or professional sources" in action for action in result["nextActions"])


def test_local_school_robotics_safety_flags_disable_connectors_accounts_persistence_mutation_and_certification():
    service = LocalSchoolRoboticsAgentService()

    result = service.create_plan(LocalSchoolRoboticsRequest(academic_goal="Plan robotics coursework."))
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
    assert safety["schoolPortalAccess"] is False
    assert safety["emailSending"] is False
    assert safety["calendarAccess"] is False
    assert safety["registrarAccess"] is False
    assert safety["financialAidAccess"] is False
    assert safety["jobApplicationSubmission"] is False
    assert safety["fileReads"] is False
    assert safety["fileWrites"] is False
    assert safety["dbWrites"] is False
    assert safety["taskPersistence"] is False
    assert safety["shellExecution"] is False
    assert safety["mutation"] is False
    assert safety["officialAcademicValidation"] is False
    assert safety["certificationClaims"] is False


def test_local_school_robotics_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_school_robotics_agent").local_school_robotics_agent).lower()
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


def test_local_school_robotics_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalSchoolRoboticsInput.model_validate(
            {
                "academicGoal": "Plan robotics coursework.",
                "portalPassword": "not allowed",
            }
        )


def test_local_school_robotics_requires_academic_goal_in_endpoint_input():
    with pytest.raises(ValidationError):
        app_module.LocalSchoolRoboticsInput.model_validate({"studentName": "Missing goal"})


def test_local_school_robotics_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/school-robotics/local-plan")
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
