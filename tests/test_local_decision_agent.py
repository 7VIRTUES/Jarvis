import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_decision_agent import LocalDecisionAgentService, LocalDecisionRequest


def test_local_decision_endpoint_returns_structured_local_decision_response():
    payload = app_module.LocalDecisionInput(
        decision="Choose private alpha support path",
        options=["Short manual checklist", "Long guided worksheet"],
        criteria=["Clear for first-time testers"],
        constraints=["No external services"],
        priorities=["Fast to use"],
        contextNotes="The flow must stay local-only and easy to review before private alpha handoff.",
        decisionStyle="balanced",
    )

    result = app_module.create_local_decision(payload)

    assert result["agentId"] == "local_decision_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_decision_support"
    assert result["decision"] == "Choose private alpha support path"
    assert result["decisionStyle"] == "balanced"
    assert result["optionsConsidered"] == ["Short manual checklist", "Long guided worksheet"]
    assert result["decisionFocus"]
    assert result["comparisonMatrix"]
    assert result["tradeoffs"]
    assert result["suggestedDirection"]
    assert result["confidence"]
    assert result["assumptions"]
    assert result["risks"]
    assert result["missingInformation"]
    assert result["nextActions"]
    assert result["reviewQuestions"]
    assert "Based only on user-provided decision inputs." in result["limitations"]


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("balanced", "balanced"),
        ("safest", "safest"),
        ("fastest", "fastest"),
        ("cheapest", "cheapest"),
        ("highest_upside", "highest_upside"),
        (" SAFEST ", "safest"),
    ],
)
def test_local_decision_supported_decision_styles_normalize(requested, expected):
    service = LocalDecisionAgentService()

    result = service.compare_options(
        LocalDecisionRequest(
            decision="Pick a path",
            options=["Option A", "Option B"],
            criteria=["Clarity"],
            decision_style=requested,
        )
    )

    assert result["decisionStyle"] == expected


def test_local_decision_unsupported_decision_style_falls_back_safely():
    service = LocalDecisionAgentService()

    result = service.compare_options(
        LocalDecisionRequest(
            decision="Pick a path",
            options=["Option A", "Option B"],
            criteria=["Clarity"],
            decision_style="externally_verified",
        )
    )

    assert result["decisionStyle"] == "balanced"
    assert result["safety"]["externalVerification"] is False
    assert result["safety"]["externalServices"] is False


def test_local_decision_fewer_than_two_options_reports_honest_warning_and_limitation():
    service = LocalDecisionAgentService()

    result = service.compare_options(LocalDecisionRequest(decision="Choose one", options=["Only option"]))

    assert result["confidence"] == "low"
    assert result["comparisonMatrix"][0]["fit"] == "not_comparable"
    assert any("Fewer than two usable options" in warning for warning in result["warnings"])
    assert any("Fewer than two usable options prevents a full comparison." == limitation for limitation in result["limitations"])
    assert result["suggestedDirection"]["certainty"] == "low"


def test_local_decision_thin_context_reports_warnings_and_limitations():
    service = LocalDecisionAgentService()

    result = service.compare_options(LocalDecisionRequest(decision="Pick", options=["A", "B"]))

    assert any("Decision context is thin" in warning for warning in result["warnings"])
    assert any("Thin context limits specificity" in limitation for limitation in result["limitations"])
    assert result["confidence"] == "low"


def test_local_decision_output_does_not_claim_external_validation_or_access():
    service = LocalDecisionAgentService()

    result = service.compare_options(
        LocalDecisionRequest(
            decision="Choose a local workflow",
            options=["Manual checklist", "Guided worksheet"],
            criteria=["Clear boundaries"],
            constraints=["No external checks"],
            priorities=["Reviewable"],
            context_notes="The decision support should stay local and response-only.",
        )
    )
    output_text = str(result).lower()

    forbidden_claims = [
        "externally verified",
        "web verified",
        "tests passed",
        "test results",
        "repo inspected",
        "repository inspected",
        "citations validated",
        "sources validated",
        "accounts accessed",
        "files read",
        "professional advice provided",
    ]

    assert all(claim not in output_text for claim in forbidden_claims)
    assert "no external verification" in output_text
    assert "no files" in output_text


def test_local_decision_high_stakes_subjects_include_local_only_professional_verification_limitations():
    service = LocalDecisionAgentService()

    result = service.compare_options(
        LocalDecisionRequest(
            decision="Choose medical treatment option",
            options=["Treatment A", "Treatment B"],
            criteria=["Safety"],
            context_notes="This is a medical decision with health consequences.",
        )
    )

    assert any("Potentially high-stakes" in warning for warning in result["warnings"])
    assert any("local decision support only" in limitation for limitation in result["limitations"])
    assert any("professional verification" in limitation for limitation in result["limitations"])


def test_local_decision_safety_flags_disable_external_persistence_and_mutation_behavior():
    service = LocalDecisionAgentService()

    result = service.compare_options(
        LocalDecisionRequest(
            decision="Local decision safety",
            options=["Option A", "Option B"],
            context_notes="Use only the request body and return decision support text only.",
        )
    )
    safety = result["safety"]

    assert safety["localOnly"] is True
    assert safety["responseOnly"] is True
    assert safety["decisionPersistence"] is False
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
    assert safety["uploads"] is False
    assert safety["mutation"] is False
    assert safety["repoInspection"] is False
    assert safety["testExecution"] is False
    assert safety["sourceValidation"] is False
    assert safety["citationValidation"] is False
    assert safety["externalVerification"] is False
    assert safety["professionalAdvice"] is False


def test_local_decision_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_decision_agent").local_decision_agent).lower()
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


def test_local_decision_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalDecisionInput.model_validate(
            {
                "decision": "Choose",
                "options": ["A", "B"],
                "repoPath": "C:/dev/Jarvis",
            }
        )


def test_local_decision_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(
        route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/decision/local-decision"
    )
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
