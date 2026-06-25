import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_troubleshooting_agent import LocalTroubleshootingAgentService, LocalTroubleshootingRequest


def test_local_troubleshooting_endpoint_returns_structured_local_triage_response():
    payload = app_module.LocalTroubleshootingInput(
        problem="Build fails after dependency update",
        symptoms=["Build stops before packaging"],
        errorMessages=["ModuleNotFoundError: No module named example"],
        environmentNotes="Windows local development environment. The error started after a dependency update.",
        attemptedFixes=["Restarted the terminal"],
        constraints=["No installs until reviewed"],
        urgency="normal",
        troubleshootingType="build_error",
    )

    result = app_module.create_local_troubleshooting_triage(payload)

    assert result["agentId"] == "local_troubleshooting_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_troubleshooting"
    assert result["problem"] == "Build fails after dependency update"
    assert result["troubleshootingType"] == "build_error"
    assert result["urgency"] == "normal"
    assert result["triageFocus"]
    assert result["observedSignals"]
    assert result["likelyCauses"]
    assert result["safeChecks"]
    assert result["nextSteps"]
    assert result["escalationTriggers"]
    assert result["informationNeeded"]
    assert result["avoidedActions"]
    assert "Based only on user-provided troubleshooting inputs." in result["limitations"]


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("general", "general"),
        ("pc_issue", "pc_issue"),
        ("app_issue", "app_issue"),
        ("build_error", "build_error"),
        ("workflow_issue", "workflow_issue"),
        ("network_issue", "network_issue"),
        (" NETWORK_ISSUE ", "network_issue"),
    ],
)
def test_local_troubleshooting_supported_types_normalize(requested, expected):
    service = LocalTroubleshootingAgentService()

    result = service.create_triage(
        LocalTroubleshootingRequest(
            problem="Local issue",
            symptoms=["The app hangs on startup"],
            troubleshooting_type=requested,
        )
    )

    assert result["troubleshootingType"] == expected


def test_local_troubleshooting_unsupported_type_falls_back_safely():
    service = LocalTroubleshootingAgentService()

    result = service.create_triage(
        LocalTroubleshootingRequest(
            problem="Local issue",
            symptoms=["The app hangs on startup"],
            troubleshooting_type="remote_repair",
        )
    )

    assert result["troubleshootingType"] == "general"
    assert result["safety"]["shellExecution"] is False
    assert result["safety"]["externalServices"] is False


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("low", "low"),
        ("normal", "normal"),
        ("high", "high"),
        (" HIGH ", "high"),
    ],
)
def test_local_troubleshooting_supported_urgency_values_normalize(requested, expected):
    service = LocalTroubleshootingAgentService()

    result = service.create_triage(
        LocalTroubleshootingRequest(
            problem="Local issue",
            symptoms=["The app hangs on startup"],
            urgency=requested,
        )
    )

    assert result["urgency"] == expected


def test_local_troubleshooting_unsupported_urgency_falls_back_safely():
    service = LocalTroubleshootingAgentService()

    result = service.create_triage(
        LocalTroubleshootingRequest(
            problem="Local issue",
            symptoms=["The app hangs on startup"],
            urgency="emergency_auto_fix",
        )
    )

    assert result["urgency"] == "normal"
    assert result["safety"]["mutation"] is False
    assert result["safety"]["settingsMutation"] is False


def test_local_troubleshooting_thin_input_reports_warnings_and_limitations():
    service = LocalTroubleshootingAgentService()

    result = service.create_triage(LocalTroubleshootingRequest(problem="It broke"))

    assert any("Troubleshooting input is thin" in warning for warning in result["warnings"])
    assert any("Thin input limits specificity" in limitation for limitation in result["limitations"])
    assert any("more symptoms" in result["triageFocus"].lower() for _ in [result])


def test_local_troubleshooting_safe_checks_are_manual_user_performed_not_executed():
    service = LocalTroubleshootingAgentService()

    result = service.create_triage(
        LocalTroubleshootingRequest(
            problem="Network is flaky",
            symptoms=["Connection drops after login"],
            troubleshooting_type="network_issue",
        )
    )

    checks_text = " ".join(result["safeChecks"]).lower()
    assert "user-performed manual check" in checks_text
    assert "jarvis will" not in checks_text
    assert "jarvis executed" not in checks_text
    assert "run command" not in checks_text
    assert "disable" not in checks_text


def test_local_troubleshooting_output_does_not_claim_validation_execution_or_access():
    service = LocalTroubleshootingAgentService()

    result = service.create_triage(
        LocalTroubleshootingRequest(
            problem="Build failed",
            symptoms=["Build stops early"],
            error_messages=["example error line"],
            environment_notes="Local Windows development environment.",
            attempted_fixes=["Restarted app"],
            troubleshooting_type="build_error",
        )
    )
    output_text = str(result).lower()

    forbidden_claims = [
        "commands executed",
        "command executed",
        "executed command",
        "files inspected",
        "file inspected",
        "logs read",
        "repo inspected",
        "repository inspected",
        "tests passed",
        "test results",
        "externally verified",
        "sources validated",
        "fix validated",
    ]

    assert all(claim not in output_text for claim in forbidden_claims)
    assert "jarvis did not execute commands" in output_text
    assert "inspect files" in output_text
    assert "read logs" in output_text


def test_local_troubleshooting_output_avoids_destructive_actions():
    service = LocalTroubleshootingAgentService()

    result = service.create_triage(
        LocalTroubleshootingRequest(
            problem="PC behaves strangely",
            symptoms=["Slow startup"],
            troubleshooting_type="pc_issue",
            urgency="high",
        )
    )
    output_text = str(result).lower()
    destructive_instructions = [
        "delete files",
        "wipe disk",
        "disable security",
        "delete registry",
        "registry deletion",
        "run unknown downloaded script",
        "git reset --hard",
        "force push",
    ]

    assert all(instruction not in output_text for instruction in destructive_instructions)
    assert any("no files should be deleted or wiped" in action.lower() for action in result["avoidedActions"])
    assert any("no security tools should be disabled" in action.lower() for action in result["avoidedActions"])


def test_local_troubleshooting_safety_flags_disable_external_persistence_and_mutation_behavior():
    service = LocalTroubleshootingAgentService()

    result = service.create_triage(
        LocalTroubleshootingRequest(
            problem="Local triage safety",
            symptoms=["Request body only"],
        )
    )
    safety = result["safety"]

    assert safety["localOnly"] is True
    assert safety["responseOnly"] is True
    assert safety["ticketPersistence"] is False
    assert safety["externalServices"] is False
    assert safety["paidApis"] is False
    assert safety["webBrowsing"] is False
    assert safety["connectorExecution"] is False
    assert safety["oauth"] is False
    assert safety["accountAccess"] is False
    assert safety["gmailAccess"] is False
    assert safety["calendarAccess"] is False
    assert safety["socialAccess"] is False
    assert safety["postingOrSending"] is False
    assert safety["emailSending"] is False
    assert safety["publicPosting"] is False
    assert safety["purchases"] is False
    assert safety["taskPersistence"] is False
    assert safety["dbWrites"] is False
    assert safety["fileReads"] is False
    assert safety["fileWrites"] is False
    assert safety["shellExecution"] is False
    assert safety["downloads"] is False
    assert safety["uploads"] is False
    assert safety["mutation"] is False
    assert safety["repoInspection"] is False
    assert safety["testExecution"] is False
    assert safety["sourceValidation"] is False
    assert safety["externalVerification"] is False
    assert safety["fixValidation"] is False
    assert safety["logReading"] is False
    assert safety["destructiveRepair"] is False
    assert safety["settingsMutation"] is False


def test_local_troubleshooting_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_troubleshooting_agent").local_troubleshooting_agent).lower()
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


def test_local_troubleshooting_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalTroubleshootingInput.model_validate(
            {
                "problem": "Triage",
                "symptoms": ["Local notes."],
                "repoPath": "C:/dev/Jarvis",
            }
        )


def test_local_troubleshooting_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(
        route
        for route in app_module.app.routes
        if getattr(route, "path", None) == "/agents/troubleshooting/local-triage"
    )
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
