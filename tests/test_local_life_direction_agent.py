import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_life_direction_agent import LocalLifeDirectionAgentService, LocalLifeDirectionRequest


def test_local_life_direction_endpoint_returns_structured_plan():
    payload = app_module.LocalLifeDirectionInput(
        profileName="Local Direction Profile",
        lifeQuestion="Clarify the next season across school, career, money, health, projects, relationships, and personal growth.",
        currentSeason="Building technical skill and discipline without burning out.",
        values=["Competence", "Integrity", "Health"],
        longTermGoals=["Become a strong technical builder", "Create durable projects"],
        currentPriorities=["School progress", "Portfolio projects"],
        tensionsOrTradeoffs=["Ambition versus rest"],
        constraints=["Manual reflection only"],
        areasToImprove=["Consistency", "Focus"],
        strengths=["Curiosity", "Systems thinking"],
        nonNegotiables=["No fake claims", "Protect health"],
        reflectionNotes="Wants grounded standards, not therapy or guaranteed outcomes.",
        desiredOutputType="life_direction_brief",
    )

    result = app_module.create_local_life_direction_plan(payload)

    assert result["agentId"] == "local_life_direction_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_life_direction_planning"
    assert result["profileName"] == "Local Direction Profile"
    assert result["lifeQuestion"] == "Clarify the next season across school, career, money, health, projects, relationships, and personal growth."
    assert result["desiredOutputType"] == "life_direction_brief"
    assert result["directionFocus"]
    assert result["valuesSummary"]
    assert result["longTermDirection"]
    assert result["currentSeasonSummary"]
    assert result["priorityPlan"]
    assert result["fiveYearDirection"]
    assert result["seasonPlan"]
    assert result["tradeoffReview"]
    assert result["identityStandards"]
    assert result["disciplinePlan"]
    assert result["nextActions"]
    assert result["openQuestions"]
    assert result["warnings"]
    assert "Based only on user-provided life question" in result["limitations"][0]
    assert result["safety"]["localOnly"] is True


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("life_direction_brief", "life_direction_brief"),
        ("values_review", "values_review"),
        ("priority_plan", "priority_plan"),
        ("five_year_direction", "five_year_direction"),
        ("season_plan", "season_plan"),
        ("tradeoff_review", "tradeoff_review"),
        ("identity_standards", "identity_standards"),
        ("discipline_plan", "discipline_plan"),
        (" SEASON_PLAN ", "season_plan"),
    ],
)
def test_local_life_direction_supported_output_types_normalize(requested, expected):
    service = LocalLifeDirectionAgentService()

    result = service.create_plan(LocalLifeDirectionRequest(life_question="Clarify direction.", desired_output_type=requested))

    assert result["desiredOutputType"] == expected


def test_local_life_direction_unsupported_output_type_falls_back_safely():
    service = LocalLifeDirectionAgentService()

    result = service.create_plan(
        LocalLifeDirectionRequest(
            life_question="Clarify direction.",
            desired_output_type="diagnose_treat_schedule_post_and_guarantee",
        )
    )

    assert result["desiredOutputType"] == "life_direction_brief"
    assert result["safety"]["diagnosis"] is False
    assert result["safety"]["treatmentPlan"] is False
    assert result["safety"]["calendarAccess"] is False
    assert result["safety"]["outcomeGuarantee"] is False


def test_local_life_direction_thin_input_reports_warnings_and_questions():
    service = LocalLifeDirectionAgentService()

    result = service.create_plan(LocalLifeDirectionRequest(life_question=""))

    assert any("input is thin" in warning.lower() for warning in result["warnings"])
    assert any("Thin input limits specificity" in limitation for limitation in result["limitations"])
    assert result["openQuestions"]
    assert result["nextActions"]


def test_local_life_direction_output_includes_values_priorities_long_term_season_tradeoffs_standards_discipline_next_actions_and_questions():
    service = LocalLifeDirectionAgentService()

    result = service.create_plan(
        LocalLifeDirectionRequest(
            life_question="Set direction for the next year.",
            current_season="Skill building.",
            values=["Integrity"],
            long_term_goals=["Build a strong career"],
            current_priorities=["School"],
            tensions_or_tradeoffs=["Focus versus too many projects"],
            areas_to_improve=["Consistency"],
            strengths=["Curiosity"],
            non_negotiables=["Protect health"],
            desired_output_type="priority_plan",
        )
    )

    assert result["valuesSummary"]
    assert result["priorityPlan"]
    assert result["longTermDirection"]
    assert result["seasonPlan"]
    assert result["tradeoffReview"]
    assert result["identityStandards"]
    assert result["disciplinePlan"]
    assert result["nextActions"]
    assert result["openQuestions"]


def test_local_life_direction_output_does_not_claim_therapy_diagnosis_treatment_crisis_validation_persistence_scheduling_posting_purchases_or_guarantees():
    service = LocalLifeDirectionAgentService()

    result = service.create_plan(
        LocalLifeDirectionRequest(
            life_question="Give therapy, diagnose me, create a treatment, intervene in crisis, validate legal financial medical choices, persist goals, schedule events, post publicly, buy things, and guarantee success.",
            desired_output_type="tradeoff_review",
        )
    )
    output_text = str(result).lower()
    forbidden_claims = [
        "therapy provided",
        "diagnosis complete",
        "treatment created",
        "crisis resolved",
        "legally validated",
        "financially validated",
        "medically validated",
        "goal persisted",
        "event scheduled",
        "posted publicly",
        "purchase completed",
        "success guaranteed",
        "life outcome guaranteed",
    ]

    assert all(claim not in output_text for claim in forbidden_claims)
    assert "no therapy" in output_text
    assert "diagnosis" in output_text
    assert "crisis intervention" in output_text
    assert "guaranteed success" in output_text


def test_local_life_direction_high_stakes_inputs_include_human_professional_official_or_emergency_help_limitations():
    service = LocalLifeDirectionAgentService()

    result = service.create_plan(
        LocalLifeDirectionRequest(
            life_question="Handle self-harm, crisis, abuse, violence, severe mental health distress, legal, medical, financial, and immigration problems.",
            desired_output_type="life_direction_brief",
        )
    )

    assert any("emergency help" in warning for warning in result["warnings"])
    assert any("emergency support" in limitation for limitation in result["limitations"])
    assert any("professional" in action and "emergency" in action for action in result["nextActions"])


def test_local_life_direction_safety_flags_disable_connectors_accounts_files_calendar_tasks_messages_health_finance_school_contacts_persistence_mutation_and_certification():
    service = LocalLifeDirectionAgentService()

    result = service.create_plan(LocalLifeDirectionRequest(life_question="Clarify direction."))
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
    assert safety["publicPosting"] is False
    assert safety["purchases"] is False
    assert safety["healthDataAccess"] is False
    assert safety["financeDataAccess"] is False
    assert safety["schoolPortalAccess"] is False
    assert safety["contactAccess"] is False
    assert safety["shellExecution"] is False
    assert safety["mutation"] is False
    assert safety["therapyClaims"] is False
    assert safety["diagnosis"] is False
    assert safety["treatmentPlan"] is False
    assert safety["crisisIntervention"] is False
    assert safety["legalValidation"] is False
    assert safety["financialValidation"] is False
    assert safety["medicalValidation"] is False
    assert safety["outcomeGuarantee"] is False
    assert safety["certificationClaims"] is False


def test_local_life_direction_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_life_direction_agent").local_life_direction_agent).lower()
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


def test_local_life_direction_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalLifeDirectionInput.model_validate(
            {
                "lifeQuestion": "Clarify direction.",
                "therapySessionToken": "not allowed",
            }
        )


def test_local_life_direction_requires_life_question_in_endpoint_input():
    with pytest.raises(ValidationError):
        app_module.LocalLifeDirectionInput.model_validate({"profileName": "Missing question"})


def test_local_life_direction_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/life-direction/local-plan")
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
