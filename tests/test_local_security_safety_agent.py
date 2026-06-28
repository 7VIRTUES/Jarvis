import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_security_safety_agent import (
    LocalSecuritySafetyAgentService,
    LocalSecuritySafetyRequest,
)


def test_local_security_safety_endpoint_returns_structured_review():
    payload = app_module.LocalSecuritySafetyInput(
        reviewName="Local Account Hygiene Review",
        situation="Prepare a manual safety review for a personal account and shared device after a suspicious message.",
        assetsOrAccounts=["Personal email account", "Shared laptop"],
        concerns=["Suspicious message", "Unclear recovery settings"],
        currentControls=["Two-step sign-in is believed to be enabled"],
        constraints=["No account access from Jarvis", "No scans or downloads"],
        riskTolerance="Cautious",
        environmentNotes="Use only user-provided notes for a local checklist.",
        incidentNotes="No active emergency reported; prepare notes for manual review.",
        desiredOutputType="safety_brief",
    )

    result = app_module.create_local_security_safety_review(payload)

    assert result["agentId"] == "local_security_safety_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_security_safety_review"
    assert result["reviewName"] == "Local Account Hygiene Review"
    assert result["situation"].startswith("Prepare a manual safety review")
    assert result["desiredOutputType"] == "safety_brief"
    assert result["safetyFocus"]
    assert result["situationSummary"]
    assert result["riskSummary"]
    assert result["privacyChecklist"]
    assert result["accountHygienePlan"]
    assert result["deviceSafetyChecklist"]
    assert result["phishingScamReview"]
    assert result["travelSafetyPlan"]
    assert result["incidentPrepPlan"]
    assert result["nextActions"]
    assert result["openQuestions"]
    assert result["warnings"]
    assert "Based only on user-provided safety and security review inputs." in result["limitations"]
    assert result["safety"]["localOnly"] is True


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("safety_brief", "safety_brief"),
        ("risk_review", "risk_review"),
        ("privacy_checklist", "privacy_checklist"),
        ("account_hygiene_plan", "account_hygiene_plan"),
        ("device_safety_checklist", "device_safety_checklist"),
        ("phishing_scam_review", "phishing_scam_review"),
        ("travel_safety_plan", "travel_safety_plan"),
        ("incident_prep_plan", "incident_prep_plan"),
        (" RISK_REVIEW ", "risk_review"),
    ],
)
def test_local_security_safety_supported_output_types_normalize(requested, expected):
    service = LocalSecuritySafetyAgentService()

    result = service.create_review(
        LocalSecuritySafetyRequest(
            review_name="Local review",
            situation="Prepare a defensive checklist.",
            desired_output_type=requested,
        )
    )

    assert result["desiredOutputType"] == expected


def test_local_security_safety_unsupported_output_type_falls_back_safely():
    service = LocalSecuritySafetyAgentService()

    result = service.create_review(
        LocalSecuritySafetyRequest(
            review_name="Local review",
            situation="Prepare a defensive checklist.",
            desired_output_type="automated_scan_and_fix",
        )
    )

    assert result["desiredOutputType"] == "safety_brief"
    assert result["safety"]["networkScanning"] is False
    assert result["safety"]["remediation"] is False
    assert result["safety"]["securityCertification"] is False


def test_local_security_safety_thin_input_reports_warnings_and_questions():
    service = LocalSecuritySafetyAgentService()

    result = service.create_review(LocalSecuritySafetyRequest(situation=""))

    assert any("Security/safety input is thin" in warning for warning in result["warnings"])
    assert any("Thin input limits specificity" in limitation for limitation in result["limitations"])
    assert result["openQuestions"]
    assert result["nextActions"]


def test_local_security_safety_output_includes_risk_checklists_and_next_actions():
    service = LocalSecuritySafetyAgentService()

    result = service.create_review(
        LocalSecuritySafetyRequest(
            review_name="Local privacy review",
            situation="Prepare a privacy checklist before changing settings manually.",
            assets_or_accounts=["Personal account", "Shared device"],
            concerns=["Public information exposure"],
            current_controls=["Manual review habit"],
            constraints=["No account access"],
            desired_output_type="privacy_checklist",
        )
    )

    assert result["riskSummary"]
    assert result["privacyChecklist"]
    assert result["accountHygienePlan"]
    assert result["deviceSafetyChecklist"]
    assert result["phishingScamReview"]
    assert result["travelSafetyPlan"]
    assert result["incidentPrepPlan"]
    assert result["nextActions"]
    assert result["openQuestions"]


def test_local_security_safety_high_impact_inputs_include_human_help_limitations():
    service = LocalSecuritySafetyAgentService()

    result = service.create_review(
        LocalSecuritySafetyRequest(
            review_name="Urgent review",
            situation="Possible compromise, extortion, financial fraud, and legal exposure.",
            concerns=["Active threat"],
            desired_output_type="incident_prep_plan",
        )
    )

    assert any("Emergency, active threat" in warning for warning in result["warnings"])
    assert any("appropriate human, professional, emergency" in limitation for limitation in result["limitations"])
    assert any("appropriate human, professional, emergency" in action for action in result["nextActions"])


def test_local_security_safety_misuse_inputs_are_defensive_only():
    service = LocalSecuritySafetyAgentService()

    result = service.create_review(
        LocalSecuritySafetyRequest(
            review_name="Defensive review",
            situation="Someone asked for hacking, exploit, malware, evasion, and unauthorized access help.",
            desired_output_type="risk_review",
        )
    )
    output_text = str(result).lower()

    assert "defensive" in output_text
    assert "no hacking" in output_text or "will not provide hacking" in output_text
    assert "unauthorized-access instructions" in output_text
    assert "credential theft" in output_text


def test_local_security_safety_output_does_not_claim_scans_access_remediation_or_certification():
    service = LocalSecuritySafetyAgentService()

    result = service.create_review(
        LocalSecuritySafetyRequest(
            review_name="Local review",
            situation="Prepare a manual safety checklist for a suspicious message.",
            desired_output_type="phishing_scam_review",
        )
    )
    output_text = str(result).lower()
    forbidden_claims = [
        "scan completed",
        "account accessed",
        "file inspected",
        "secret read",
        "remediation completed",
        "forensic validation completed",
        "compliance certified",
        "security certified",
        "vulnerability confirmed",
        "incident resolved",
        "system is secure",
    ]

    assert all(claim not in output_text for claim in forbidden_claims)
    assert "no device" in output_text
    assert "no forensic validation" in output_text
    assert "no scans" in output_text


def test_local_security_safety_safety_flags_disable_external_access_and_validation_claims():
    service = LocalSecuritySafetyAgentService()

    result = service.create_review(
        LocalSecuritySafetyRequest(
            review_name="Local review",
            situation="Prepare a manual safety checklist.",
        )
    )
    safety = result["safety"]

    assert safety["localOnly"] is True
    assert safety["responseOnly"] is True
    assert safety["manualInputOnly"] is True
    assert safety["externalServices"] is False
    assert safety["connectors"] is False
    assert safety["oauth"] is False
    assert safety["accountAccess"] is False
    assert safety["fileReads"] is False
    assert safety["secretReads"] is False
    assert safety["browserCookieAccess"] is False
    assert safety["passwordManagerAccess"] is False
    assert safety["networkScanning"] is False
    assert safety["vulnerabilityScanning"] is False
    assert safety["malwareScanning"] is False
    assert safety["shellExecution"] is False
    assert safety["downloads"] is False
    assert safety["remediation"] is False
    assert safety["accountRecovery"] is False
    assert safety["emailSending"] is False
    assert safety["publicPosting"] is False
    assert safety["purchases"] is False
    assert safety["dbWrites"] is False
    assert safety["taskPersistence"] is False
    assert safety["mutation"] is False
    assert safety["forensicValidation"] is False
    assert safety["legalValidation"] is False
    assert safety["complianceCertification"] is False
    assert safety["securityCertification"] is False


def test_local_security_safety_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_security_safety_agent").local_security_safety_agent).lower()
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


def test_local_security_safety_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalSecuritySafetyInput.model_validate(
            {
                "situation": "Prepare a manual checklist.",
                "scanTarget": "not allowed",
            }
        )


def test_local_security_safety_requires_situation_in_endpoint_input():
    with pytest.raises(ValidationError):
        app_module.LocalSecuritySafetyInput.model_validate({"reviewName": "Missing situation"})


def test_local_security_safety_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(
        route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/security-safety/local-review"
    )
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
