import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_everyday_life_agent import LocalEverydayLifeAgentService, LocalEverydayLifeRequest


def test_local_everyday_life_endpoint_returns_structured_plan():
    payload = app_module.LocalEverydayLifeInput(
        lifeArea="Household reset",
        situation="Prepare for a busy week with chores, errands, and personal admin.",
        goals=["Reduce clutter", "Batch errands"],
        constraints=["Keep the plan manual"],
        scheduleNotes="Two short evening blocks and one weekend planning block.",
        householdNotes="Shared spaces need a quick reset.",
        errands=["Return library books", "Pick up basic groceries"],
        peopleInvolved=["Household members"],
        resources=["Existing checklist"],
        energyNotes="Energy is lower after work.",
        budgetNotes="Use items already on hand where possible.",
        desiredOutputType="life_brief",
    )

    result = app_module.create_local_everyday_life_plan(payload)

    assert result["agentId"] == "local_everyday_life_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_everyday_life_planning"
    assert result["lifeArea"] == "Household reset"
    assert result["situation"] == "Prepare for a busy week with chores, errands, and personal admin."
    assert result["desiredOutputType"] == "life_brief"
    assert result["lifeFocus"]
    assert result["situationSummary"]
    assert result["prioritySummary"]
    assert result["dailyPlan"]
    assert result["weeklyPlan"]
    assert result["routinePlan"]
    assert result["errandPlan"]
    assert result["householdPlan"]
    assert result["preparationChecklist"]
    assert result["nextActions"]
    assert result["openQuestions"]
    assert result["warnings"]
    assert "Based only on user-provided everyday-life planning inputs." in result["limitations"]
    assert result["safety"]["localOnly"] is True


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("life_brief", "life_brief"),
        ("daily_plan", "daily_plan"),
        ("weekly_plan", "weekly_plan"),
        ("routine_plan", "routine_plan"),
        ("errand_plan", "errand_plan"),
        ("household_plan", "household_plan"),
        ("preparation_checklist", "preparation_checklist"),
        ("priority_review", "priority_review"),
        (" DAILY_PLAN ", "daily_plan"),
    ],
)
def test_local_everyday_life_supported_output_types_normalize(requested, expected):
    service = LocalEverydayLifeAgentService()

    result = service.create_plan(
        LocalEverydayLifeRequest(
            situation="Plan a simple evening reset.",
            desired_output_type=requested,
        )
    )

    assert result["desiredOutputType"] == expected


def test_local_everyday_life_unsupported_output_type_falls_back_safely():
    service = LocalEverydayLifeAgentService()

    result = service.create_plan(
        LocalEverydayLifeRequest(
            situation="Plan chores.",
            desired_output_type="automated_calendar_plan",
        )
    )

    assert result["desiredOutputType"] == "life_brief"
    assert result["safety"]["calendarAccess"] is False
    assert result["safety"]["taskPersistence"] is False
    assert result["safety"]["mutation"] is False


def test_local_everyday_life_thin_input_reports_warnings_and_questions():
    service = LocalEverydayLifeAgentService()

    result = service.create_plan(LocalEverydayLifeRequest(situation="Need to get organized."))

    assert any("Everyday-life input is thin" in warning for warning in result["warnings"])
    assert any("Thin input limits specificity" in limitation for limitation in result["limitations"])
    assert result["openQuestions"]
    assert result["nextActions"]


def test_local_everyday_life_output_includes_plans_checklists_and_next_actions():
    service = LocalEverydayLifeAgentService()

    result = service.create_plan(
        LocalEverydayLifeRequest(
            life_area="Errands",
            situation="Prepare for a weekend reset.",
            goals=["Finish household basics"],
            errands=["Library return", "Grocery pickup"],
            resources=["Reusable bags"],
            desired_output_type="errand_plan",
        )
    )

    assert result["dailyPlan"]
    assert result["weeklyPlan"]
    assert result["routinePlan"]
    assert result["errandPlan"]
    assert result["householdPlan"]
    assert result["preparationChecklist"]
    assert result["nextActions"]
    assert result["openQuestions"]


def test_local_everyday_life_high_stakes_inputs_include_human_help_limitations():
    service = LocalEverydayLifeAgentService()

    result = service.create_plan(
        LocalEverydayLifeRequest(
            situation="Emergency safety issue and legal deadline at home.",
            goals=["Figure out what to do"],
            desired_output_type="priority_review",
        )
    )

    assert any("Potentially high-stakes wording detected" in warning for warning in result["warnings"])
    assert any("human, professional, emergency, or local authority help" in limitation for limitation in result["limitations"])
    assert any("high-stakes concerns" in action for action in result["nextActions"])


def test_local_everyday_life_output_does_not_claim_execution_or_account_actions():
    service = LocalEverydayLifeAgentService()

    result = service.create_plan(
        LocalEverydayLifeRequest(
            situation="Plan a household reset.",
            goals=["Handle chores"],
            schedule_notes="Use a short block tonight.",
            errands=["Pick up groceries"],
        )
    )
    output_text = str(result).lower()
    forbidden_claims = [
        "task created",
        "calendar event created",
        "email sent",
        "file written",
        "purchase completed",
        "post published",
        "account accessed",
        "route planned using maps",
        "smart home controlled",
        "schedule confirmed",
        "delivery scheduled",
        "execution completed",
    ]

    assert all(claim not in output_text for claim in forbidden_claims)
    assert "no gmail" in output_text
    assert "no scheduling" in output_text
    assert "no maps" in output_text
    assert "no tasks" in output_text or "no calendar event" in output_text


def test_local_everyday_life_safety_flags_disable_connectors_persistence_and_mutation():
    service = LocalEverydayLifeAgentService()

    result = service.create_plan(LocalEverydayLifeRequest(situation="Plan a simple routine."))
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
    assert safety["calendarAccess"] is False
    assert safety["emailSending"] is False
    assert safety["publicPosting"] is False
    assert safety["purchases"] is False
    assert safety["fileReads"] is False
    assert safety["fileWrites"] is False
    assert safety["dbWrites"] is False
    assert safety["taskPersistence"] is False
    assert safety["shellExecution"] is False
    assert safety["smartHomeControl"] is False
    assert safety["locationAccess"] is False
    assert safety["mutation"] is False
    assert safety["certificationClaims"] is False


def test_local_everyday_life_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_everyday_life_agent").local_everyday_life_agent).lower()
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


def test_local_everyday_life_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalEverydayLifeInput.model_validate(
            {
                "situation": "Plan errands.",
                "calendarAccount": "not allowed",
            }
        )


def test_local_everyday_life_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(
        route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/everyday-life/local-plan"
    )
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
