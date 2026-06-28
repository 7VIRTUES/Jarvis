import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_learning_study_agent import LocalLearningStudyAgentService, LocalLearningStudyRequest


def test_local_learning_study_endpoint_returns_structured_plan():
    payload = app_module.LocalLearningStudyInput(
        learnerName="Local Learner",
        learningGoal="Build a steady study plan for robotics controls and computer vision foundations.",
        topics=["PID control", "State estimation", "Image filtering", "Camera calibration"],
        currentLevel="Comfortable with programming basics; weaker on math-heavy explanations.",
        timeline="Prepare over the next six weeks before project work intensifies.",
        availableTime="Four 45-minute blocks during the week and one weekend review block.",
        resources=["Class notes", "Practice problem set", "User-provided project notes"],
        weakAreas=["Deriving equations", "Explaining assumptions", "Remembering formulas"],
        preferredMethods=["Active recall", "Practice problems", "Feynman explanations"],
        constraints=["Manual planning only"],
        motivationNotes="Connect each study block to stronger robotics project confidence.",
        desiredOutputType="learning_brief",
    )

    result = app_module.create_local_learning_study_plan(payload)

    assert result["agentId"] == "local_learning_study_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_learning_study_planning"
    assert result["learnerName"] == "Local Learner"
    assert result["learningGoal"] == "Build a steady study plan for robotics controls and computer vision foundations."
    assert result["desiredOutputType"] == "learning_brief"
    assert result["learningFocus"]
    assert result["baselineSummary"]
    assert result["topicMap"]
    assert result["studyPlan"]
    assert result["learningRoadmap"]
    assert result["activeRecallPlan"]
    assert result["feynmanDrills"]
    assert result["spacedRepetitionPlan"]
    assert result["weeklyReview"]
    assert result["bossTest"]
    assert result["progressChecklist"]
    assert result["nextActions"]
    assert result["openQuestions"]
    assert result["warnings"]
    assert "Based only on user-provided learning" in result["limitations"][0]
    assert result["safety"]["localOnly"] is True


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("learning_brief", "learning_brief"),
        ("study_plan", "study_plan"),
        ("learning_roadmap", "learning_roadmap"),
        ("active_recall_plan", "active_recall_plan"),
        ("feynman_drills", "feynman_drills"),
        ("spaced_repetition_plan", "spaced_repetition_plan"),
        ("weekly_review", "weekly_review"),
        ("boss_test", "boss_test"),
        (" WEEKLY_REVIEW ", "weekly_review"),
    ],
)
def test_local_learning_study_supported_output_types_normalize(requested, expected):
    service = LocalLearningStudyAgentService()

    result = service.create_plan(
        LocalLearningStudyRequest(
            learning_goal="Prepare a manual study plan.",
            desired_output_type=requested,
        )
    )

    assert result["desiredOutputType"] == expected


def test_local_learning_study_unsupported_output_type_falls_back_safely():
    service = LocalLearningStudyAgentService()

    result = service.create_plan(
        LocalLearningStudyRequest(
            learning_goal="Prepare study notes.",
            desired_output_type="submit_sync_schedule_and_certify",
        )
    )

    assert result["desiredOutputType"] == "learning_brief"
    assert result["safety"]["assignmentSubmission"] is False
    assert result["safety"]["externalAppWrites"] is False
    assert result["safety"]["masteryCertification"] is False


def test_local_learning_study_thin_input_reports_warnings_and_questions():
    service = LocalLearningStudyAgentService()

    result = service.create_plan(LocalLearningStudyRequest(learning_goal=""))

    assert any("input is thin" in warning.lower() for warning in result["warnings"])
    assert any("Thin input limits specificity" in limitation for limitation in result["limitations"])
    assert result["openQuestions"]
    assert result["nextActions"]


def test_local_learning_study_output_includes_roadmap_study_recall_feynman_spaced_review_and_boss_sections():
    service = LocalLearningStudyAgentService()

    result = service.create_plan(
        LocalLearningStudyRequest(
            learning_goal="Prepare for controls and vision coursework.",
            topics=["PID control", "Camera calibration"],
            current_level="Beginner-intermediate.",
            resources=["Class notes"],
            weak_areas=["Formula recall"],
            desired_output_type="study_plan",
        )
    )

    assert result["studyPlan"]
    assert result["learningRoadmap"]
    assert result["activeRecallPlan"]
    assert result["feynmanDrills"]
    assert result["spacedRepetitionPlan"]
    assert result["weeklyReview"]
    assert result["bossTest"]
    assert result["progressChecklist"]


def test_local_learning_study_output_does_not_claim_portal_lms_file_app_access_assignment_submission_or_guarantees():
    service = LocalLearningStudyAgentService()

    result = service.create_plan(
        LocalLearningStudyRequest(
            learning_goal="Access LMS, read files, create tasks, submit assignment, guarantee grade, and certify mastery.",
            desired_output_type="boss_test",
        )
    )
    output_text = str(result).lower()
    forbidden_claims = [
        "portal accessed",
        "lms accessed",
        "file contents read",
        "anki card created",
        "calendar event created",
        "task created",
        "assignment submitted",
        "study record persisted",
        "officially validated",
        "grade guaranteed",
        "exam score guaranteed",
        "mastery certified",
    ]

    assert all(claim not in output_text for claim in forbidden_claims)
    assert "no school portal" in output_text
    assert "no school portals" in output_text
    assert "no official tutoring" in output_text
    assert "no cards are created" in output_text


def test_local_learning_study_high_stakes_inputs_include_official_or_professional_confirmation_limitations():
    service = LocalLearningStudyAgentService()

    result = service.create_plan(
        LocalLearningStudyRequest(
            learning_goal="Prepare for exam grades, accommodations, health concerns, certification, and official requirements.",
            desired_output_type="learning_brief",
        )
    )

    assert any("official or professional confirmation" in warning for warning in result["warnings"])
    assert any("official sources or qualified professionals" in limitation for limitation in result["limitations"])
    assert any("official academic" in action for action in result["nextActions"])


def test_local_learning_study_safety_flags_disable_connectors_accounts_browsing_school_lms_files_persistence_app_writes_mutation_and_certification():
    service = LocalLearningStudyAgentService()

    result = service.create_plan(LocalLearningStudyRequest(learning_goal="Prepare a study plan."))
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
    assert safety["schoolPortalAccess"] is False
    assert safety["lmsAccess"] is False
    assert safety["calendarAccess"] is False
    assert safety["taskPersistence"] is False
    assert safety["fileReads"] is False
    assert safety["fileWrites"] is False
    assert safety["dbWrites"] is False
    assert safety["externalAppWrites"] is False
    assert safety["assignmentSubmission"] is False
    assert safety["shellExecution"] is False
    assert safety["mutation"] is False
    assert safety["officialAcademicValidation"] is False
    assert safety["gradeGuarantee"] is False
    assert safety["examScoreGuarantee"] is False
    assert safety["masteryCertification"] is False
    assert safety["certificationClaims"] is False


def test_local_learning_study_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_learning_study_agent").local_learning_study_agent).lower()
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


def test_local_learning_study_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalLearningStudyInput.model_validate(
            {
                "learningGoal": "Prepare a study plan.",
                "schoolPortalPassword": "not allowed",
            }
        )


def test_local_learning_study_requires_learning_goal_in_endpoint_input():
    with pytest.raises(ValidationError):
        app_module.LocalLearningStudyInput.model_validate({"learnerName": "Missing goal"})


def test_local_learning_study_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/learning-study/local-plan")
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
