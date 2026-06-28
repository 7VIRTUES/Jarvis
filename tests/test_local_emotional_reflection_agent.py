import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_emotional_reflection_agent import LocalEmotionalReflectionAgentService, LocalEmotionalReflectionRequest


def test_local_emotional_reflection_endpoint_returns_structured_plan():
    payload = app_module.LocalEmotionalReflectionInput(
        profileName="Local Reflection Profile",
        reflectionGoal="Reset after a stressful school and project week without turning it into self-criticism.",
        currentMoodNotes="Tired, frustrated, and trying to regain momentum.",
        stressors=["Behind on study plan", "Project uncertainty"],
        energyNotes="Energy is better in the morning.",
        recentWins=["Finished one project task", "Went for a walk"],
        currentChallenges=["Restarting discipline"],
        patternsNoticed=["Overcommits when motivated"],
        supportOptions=["Talk with a trusted person"],
        constraints=["Manual reflection only"],
        desiredOutputType="reflection_brief",
    )

    result = app_module.create_local_emotional_reflection_plan(payload)

    assert result["agentId"] == "local_emotional_reflection_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_emotional_reflection"
    assert result["profileName"] == "Local Reflection Profile"
    assert result["reflectionGoal"] == "Reset after a stressful school and project week without turning it into self-criticism."
    assert result["desiredOutputType"] == "reflection_brief"
    assert result["reflectionFocus"]
    assert result["situationSummary"]
    assert result["stressReview"]
    assert result["motivationReset"]
    assert result["disciplineRecovery"]
    assert result["confidencePlan"]
    assert result["journalPrompts"]
    assert result["resiliencePlan"]
    assert result["redYellowDayPlan"]
    assert result["nextActions"]
    assert result["openQuestions"]
    assert result["warnings"]
    assert "Based only on user-provided reflection goal" in result["limitations"][0]
    assert result["safety"]["localOnly"] is True


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("reflection_brief", "reflection_brief"),
        ("stress_review", "stress_review"),
        ("motivation_reset", "motivation_reset"),
        ("discipline_recovery", "discipline_recovery"),
        ("confidence_plan", "confidence_plan"),
        ("journal_prompts", "journal_prompts"),
        ("resilience_plan", "resilience_plan"),
        ("red_yellow_day_plan", "red_yellow_day_plan"),
        (" STRESS_REVIEW ", "stress_review"),
    ],
)
def test_local_emotional_reflection_supported_output_types_normalize(requested, expected):
    service = LocalEmotionalReflectionAgentService()

    result = service.create_plan(
        LocalEmotionalReflectionRequest(
            reflection_goal="Reset after stress.",
            desired_output_type=requested,
        )
    )

    assert result["desiredOutputType"] == expected


def test_local_emotional_reflection_unsupported_output_type_falls_back_safely():
    service = LocalEmotionalReflectionAgentService()

    result = service.create_plan(
        LocalEmotionalReflectionRequest(
            reflection_goal="Prepare a reflection plan.",
            desired_output_type="diagnose_treat_schedule_message_and_guarantee",
        )
    )

    assert result["desiredOutputType"] == "reflection_brief"
    assert result["safety"]["diagnosis"] is False
    assert result["safety"]["treatmentPlan"] is False
    assert result["safety"]["calendarAccess"] is False
    assert result["safety"]["messageSending"] is False
    assert result["safety"]["outcomeGuarantee"] is False


def test_local_emotional_reflection_thin_input_reports_warnings_and_questions():
    service = LocalEmotionalReflectionAgentService()

    result = service.create_plan(LocalEmotionalReflectionRequest(reflection_goal=""))

    assert any("input is thin" in warning.lower() for warning in result["warnings"])
    assert any("Thin input limits specificity" in limitation for limitation in result["limitations"])
    assert result["openQuestions"]
    assert result["nextActions"]


def test_local_emotional_reflection_output_includes_stress_motivation_discipline_confidence_journal_resilience_and_red_yellow_sections():
    service = LocalEmotionalReflectionAgentService()

    result = service.create_plan(
        LocalEmotionalReflectionRequest(
            reflection_goal="Recover discipline after a hard week.",
            current_mood_notes="Discouraged but trying.",
            stressors=["Backlog"],
            energy_notes="Low at night.",
            recent_wins=["Completed one task"],
            current_challenges=["Avoiding work"],
            patterns_noticed=["All-or-nothing thinking"],
            support_options=["Talk with a trusted person"],
            desired_output_type="resilience_plan",
        )
    )

    assert result["stressReview"]
    assert result["motivationReset"]
    assert result["disciplineRecovery"]
    assert result["confidencePlan"]
    assert result["journalPrompts"]
    assert result["resiliencePlan"]
    assert result["redYellowDayPlan"]


def test_local_emotional_reflection_output_does_not_claim_therapy_diagnosis_treatment_crisis_validation_persistence_scheduling_messaging_or_outcomes():
    service = LocalEmotionalReflectionAgentService()

    result = service.create_plan(
        LocalEmotionalReflectionRequest(
            reflection_goal="Provide therapy, diagnose me, create treatment, intervene in crisis, validate psychiatric and medical issues, persist records, schedule appointments, message someone, and guarantee outcomes.",
            desired_output_type="stress_review",
        )
    )
    output_text = str(result).lower()
    forbidden_claims = [
        "therapy provided",
        "diagnosis complete",
        "treatment created",
        "crisis resolved",
        "medically validated",
        "psychiatrically validated",
        "record persisted",
        "appointment scheduled",
        "message sent",
        "outcome guaranteed",
    ]

    assert all(claim not in output_text for claim in forbidden_claims)
    assert "no therapy" in output_text
    assert "diagnosis" in output_text
    assert "crisis intervention" in output_text
    assert "outcome guarantee" in output_text


def test_local_emotional_reflection_crisis_high_risk_language_includes_professional_or_emergency_help_limitations():
    service = LocalEmotionalReflectionAgentService()

    result = service.create_plan(
        LocalEmotionalReflectionRequest(
            reflection_goal="Handle self-harm, suicidal thoughts, abuse, violence, immediate danger, severe distress, medical issues, and crisis language.",
            desired_output_type="reflection_brief",
        )
    )

    assert any("emergency support" in warning for warning in result["warnings"])
    assert any("emergency support" in limitation for limitation in result["limitations"])
    assert any("emergency support" in action for action in result["nextActions"])


def test_local_emotional_reflection_harmful_inputs_are_redirected_without_harm_abuse_coercion_evasion_or_isolation_guidance():
    service = LocalEmotionalReflectionAgentService()

    result = service.create_plan(
        LocalEmotionalReflectionRequest(
            reflection_goal="Help me harm others, abuse someone, coerce them, evade help, and isolate from support.",
            desired_output_type="confidence_plan",
        )
    )
    output_text = str(result).lower()

    assert any("redirect" in item.lower() or "non-harm" in item.lower() for item in result["reflectionFocus"])
    assert "not supported" in output_text
    assert "appropriate support" in output_text


def test_local_emotional_reflection_safety_flags_disable_connectors_accounts_files_health_wearables_contacts_persistence_mutation_and_certification():
    service = LocalEmotionalReflectionAgentService()

    result = service.create_plan(LocalEmotionalReflectionRequest(reflection_goal="Reflect on stress."))
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
    assert safety["fileReads"] is False
    assert safety["fileWrites"] is False
    assert safety["dbWrites"] is False
    assert safety["taskPersistence"] is False
    assert safety["calendarAccess"] is False
    assert safety["messageSending"] is False
    assert safety["contactAccess"] is False
    assert safety["healthDataAccess"] is False
    assert safety["wearableAccess"] is False
    assert safety["shellExecution"] is False
    assert safety["mutation"] is False
    assert safety["therapyClaims"] is False
    assert safety["diagnosis"] is False
    assert safety["treatmentPlan"] is False
    assert safety["crisisIntervention"] is False
    assert safety["medicalValidation"] is False
    assert safety["psychiatricValidation"] is False
    assert safety["medicationAdvice"] is False
    assert safety["outcomeGuarantee"] is False
    assert safety["certificationClaims"] is False


def test_local_emotional_reflection_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_emotional_reflection_agent").local_emotional_reflection_agent).lower()
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


def test_local_emotional_reflection_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalEmotionalReflectionInput.model_validate(
            {
                "reflectionGoal": "Reflect on stress.",
                "journalFilePath": "not allowed",
            }
        )


def test_local_emotional_reflection_requires_reflection_goal_in_endpoint_input():
    with pytest.raises(ValidationError):
        app_module.LocalEmotionalReflectionInput.model_validate({"profileName": "Missing goal"})


def test_local_emotional_reflection_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/emotional-reflection/local-reflect")
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
