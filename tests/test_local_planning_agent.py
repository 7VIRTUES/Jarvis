import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_planning_agent import LocalPlanningAgentService, LocalPlanningRequest


def test_local_planning_endpoint_returns_structured_local_plan():
    payload = app_module.LocalPlanningInput(
        goal="Prepare a local alpha checklist",
        contextNotes="The work must stay local and reviewable. Dashboard status should be clear.",
        constraints=["No external services", "Keep scope narrow"],
        resources=["Existing README and docs"],
        blockers=["Need final review"],
        timeframe="This week",
        desiredOutputType="project_plan",
    )

    result = app_module.create_local_plan(payload)

    assert result["agentId"] == "local_planning_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_planning"
    assert result["goal"] == "Prepare a local alpha checklist"
    assert result["desiredOutputType"] == "project_plan"
    assert result["planningFocus"]
    assert result["assumptions"]
    assert result["phases"]
    assert result["checklist"]
    assert result["nextActions"]
    assert result["risks"]
    assert result["blockers"] == ["Need final review"]
    assert result["reviewQuestions"]
    assert "Based only on user-provided planning inputs." in result["limitations"]


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("project_plan", "project_plan"),
        ("study_plan", "study_plan"),
        ("checklist", "checklist"),
        ("weekly_plan", "weekly_plan"),
        (" STUDY_PLAN ", "study_plan"),
    ],
)
def test_local_planning_supported_output_types_normalize(requested, expected):
    service = LocalPlanningAgentService()

    result = service.create_plan(LocalPlanningRequest(goal="Learn local testing", desired_output_type=requested))

    assert result["desiredOutputType"] == expected


def test_local_planning_unsupported_output_type_falls_back_safely():
    service = LocalPlanningAgentService()

    result = service.create_plan(LocalPlanningRequest(goal="Plan safely", desired_output_type="calendar_schedule"))

    assert result["desiredOutputType"] == "project_plan"
    assert result["safety"]["calendarEmailIntegration"] is False
    assert result["safety"]["taskPersistence"] is False


def test_local_planning_thin_context_reports_warnings_and_limitations():
    service = LocalPlanningAgentService()

    result = service.create_plan(LocalPlanningRequest(goal="Organize the project"))

    assert "Clarify and sequence" in result["planningFocus"]
    assert result["warnings"] == ["Planning context is thin; output is a provisional local planning scaffold."]
    assert any("Thin context limits specificity" in limitation for limitation in result["limitations"])
    assert "No blockers were provided." in result["blockers"]
    assert any("Add context notes" in action for action in result["nextActions"])


def test_local_planning_safety_flags_disable_external_persistence_and_mutation_behavior():
    service = LocalPlanningAgentService()

    result = service.create_plan(
        LocalPlanningRequest(
            goal="Local planning safety",
            context_notes="Use only the request body.",
            constraints=["No persistence"],
        )
    )
    safety = result["safety"]

    assert safety["localOnly"] is True
    assert safety["responseOnly"] is True
    assert safety["externalServices"] is False
    assert safety["paidApis"] is False
    assert safety["webBrowsing"] is False
    assert safety["connectorExecution"] is False
    assert safety["oauth"] is False
    assert safety["accountAccess"] is False
    assert safety["postingOrSending"] is False
    assert safety["calendarEmailIntegration"] is False
    assert safety["taskPersistence"] is False
    assert safety["reminders"] is False
    assert safety["fileReads"] is False
    assert safety["fileWrites"] is False
    assert safety["shellExecution"] is False
    assert safety["uploads"] is False
    assert safety["mutation"] is False


def test_local_planning_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_planning_agent").local_planning_agent).lower()
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
        "google_calendar",
        "smtp.",
        "imap.",
        "openai",
        "anthropic",
        "gemini",
    ]

    assert all(token not in source for token in forbidden)


def test_local_planning_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalPlanningInput.model_validate({"goal": "Plan", "projectName": "Jarvis"})


def test_local_planning_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/planning/local-plan")
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
