import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_life_dashboard_coordinator_agent import (
    LocalLifeDashboardCoordinatorAgentService,
    LocalLifeDashboardCoordinatorRequest,
)


def test_local_life_dashboard_coordinator_endpoint_returns_structured_plan_with_suggested_agents_only():
    payload = app_module.LocalLifeDashboardCoordinatorInput(
        request="Coordinate school, robotics, fitness, money, and social goals into one dashboard.",
        promptText="Keep it compact and manual.",
        outputType="life_dashboard",
        lifeAreas=["School", "Robotics", "Fitness", "Money", "Social"],
        currentGoals=["Keep classes on track", "Prepare the robotics build", "Restart workouts"],
        currentProjects=["Robotics competition", "Semester assignments"],
        urgentItems=["Math quiz Friday", "Robot drivetrain test"],
        timeHorizon="Next 7 days",
        availableTime="Two evenings and Saturday morning",
        energyLevel="Medium",
        constraintsOrNotes="No calendar, task, reminder, file, connector, or account access.",
        priorityPreference="Balance deadlines with recovery.",
        domainsToCoordinate=["school", "robotics", "fitness", "money", "relationships"],
        existingAgentOutputsOrNotes=["Study plan needs a short review block"],
        decisionContext="Choose where limited evening focus goes.",
        weeklyFocus="Protect school deadlines while making visible robotics progress.",
        riskOrStressFlags=["Overcommitting"],
        desiredDashboardStyle="Compact weekly dashboard",
    )

    result = app_module.create_local_life_dashboard_coordinator_plan(payload)

    assert result["agent_id"] == "local_life_dashboard_cross_agent_coordinator"
    assert result["agentId"] == "local_life_dashboard_cross_agent_coordinator"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_life_dashboard_cross_agent_coordination"
    assert result["output_type"] == "life_dashboard"
    assert result["dashboard_sections"]
    assert result["life_area_snapshot"]
    assert result["priority_order"]
    assert result["cross_agent_plan"]
    assert result["next_actions"]
    assert result["weekly_focus"]
    assert result["recommended_agents"]
    for recommended_agent in result["recommended_agents"]:
        assert recommended_agent["suggested_only"] is True
        assert recommended_agent["invoked"] is False
        assert recommended_agent["handoff_created"] is False

    safety = result["safety"]
    assert safety["localOnly"] is True
    assert safety["responseOnly"] is True
    assert safety["manualInputOnly"] is True
    assert safety["automaticSubAgentExecution"] is False
    assert safety["agentInvocation"] is False
    assert safety["agentHandoffs"] is False
    assert safety["taskCreation"] is False
    assert safety["reminderCreation"] is False
    assert safety["accountAccess"] is False
    assert safety["connectors"] is False
    assert safety["externalServices"] is False
    assert safety["fileWrites"] is False
    assert safety["mutation"] is False


@pytest.mark.parametrize(
    "output_type",
    [
        "life_dashboard",
        "cross_agent_plan",
        "agent_routing_plan",
        "priority_map",
        "weekly_operating_plan",
        "daily_focus_plan",
        "decision_map",
        "project_life_alignment",
        "risk_review",
        "next_action_stack",
        "checklist",
        "summary",
        " WEEKLY_OPERATING_PLAN ",
    ],
)
def test_local_life_dashboard_coordinator_supported_output_types_normalize(output_type):
    service = LocalLifeDashboardCoordinatorAgentService()

    result = service.create_plan(LocalLifeDashboardCoordinatorRequest(request="Coordinate the week.", output_type=output_type))

    assert result["output_type"] == output_type.strip().lower()


def test_local_life_dashboard_coordinator_unsupported_output_type_falls_back_safely():
    service = LocalLifeDashboardCoordinatorAgentService()

    result = service.create_plan(
        LocalLifeDashboardCoordinatorRequest(
            request="Run all agents, create tasks, schedule reminders, submit forms, and pay bills.",
            output_type="automation_handoff_runner",
        )
    )

    assert result["output_type"] == "summary"
    assert result["safety"]["automaticSubAgentExecution"] is False
    assert result["safety"]["taskCreation"] is False
    assert result["safety"]["reminderCreation"] is False
    assert result["safety"]["submissions"] is False
    assert result["safety"]["financialTransactions"] is False


def test_local_life_dashboard_coordinator_high_stakes_and_immediate_danger_stay_manual_and_route_to_humans():
    service = LocalLifeDashboardCoordinatorAgentService()

    result = service.create_plan(
        LocalLifeDashboardCoordinatorRequest(
            request="Coordinate medical emergency, gas leak, debt, legal deadline, and immigration risk.",
            output_type="risk_review",
            risk_or_stress_flags=["gas leak", "medical emergency", "legal deadline", "debt"],
        )
    )
    output_text = str(result).lower()

    assert "qualified professionals or official sources" in output_text
    assert "contact local emergency services" in output_text
    assert result["safety"]["emergencyCalls"] is False
    assert result["safety"]["medicalDecisions"] is False
    assert result["safety"]["financialTransactions"] is False
    assert result["safety"]["officialFilings"] is False


def test_local_life_dashboard_coordinator_source_has_no_network_file_shell_api_persistence_or_agent_invocation_calls():
    source = inspect.getsource(__import__("jarvis_core.local_life_dashboard_coordinator_agent").local_life_dashboard_coordinator_agent).lower()
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
        ".create_plan(",
        "fetch(",
    ]

    assert all(token not in source for token in forbidden)


def test_local_life_dashboard_coordinator_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalLifeDashboardCoordinatorInput.model_validate(
            {
                "request": "Coordinate the week.",
                "calendarOauthToken": "not allowed",
            }
        )


def test_local_life_dashboard_coordinator_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/life-dashboard-coordinator/local-plan")
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
