import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_business_agent import LocalBusinessAgentService, LocalBusinessRequest


def test_local_business_endpoint_returns_structured_local_business_response():
    payload = app_module.LocalBusinessInput(
        businessName="Neighborhood Meal Prep Studio",
        businessIdea="Offer small-batch weekly meal prep kits for busy local households.",
        targetCustomer="Busy families who want simple weeknight meals",
        problem="Weeknight cooking feels rushed and planning takes too much time.",
        offer="Pre-portioned local meal prep kits with simple instructions.",
        pricingNotes="Pilot a simple per-kit price and review customer feedback manually.",
        operationsNotes="Start with a small menu, local pickup window, and manual order tracking.",
        marketingNotes="Explain convenience, freshness, and predictable weekly planning.",
        constraints=["Manual local pilot only"],
        resources=["Local supplier list"],
        risks=["Demand may be uncertain"],
        goals=["Prepare a small launch checklist"],
        desiredOutputType="business_brief",
    )

    result = app_module.create_local_business_brief(payload)

    assert result["agentId"] == "local_business_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_business_planning"
    assert result["businessName"] == "Neighborhood Meal Prep Studio"
    assert result["businessIdea"] == "Offer small-batch weekly meal prep kits for busy local households."
    assert result["desiredOutputType"] == "business_brief"
    assert result["businessFocus"]
    assert result["customerAssumptions"]
    assert result["problemSummary"]
    assert result["offerSummary"]
    assert result["valueProposition"]
    assert result["revenueNotes"]
    assert result["operationsNotes"]
    assert result["marketingAngles"]
    assert result["swot"]
    assert result["leanCanvas"]
    assert result["launchChecklist"]
    assert result["risks"]
    assert result["nextActions"]
    assert result["openQuestions"]
    assert "Based only on user-provided business planning inputs." in result["limitations"]


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("business_brief", "business_brief"),
        ("lean_canvas", "lean_canvas"),
        ("swot", "swot"),
        ("offer_plan", "offer_plan"),
        ("marketing_plan", "marketing_plan"),
        ("operations_plan", "operations_plan"),
        ("risk_review", "risk_review"),
        ("launch_checklist", "launch_checklist"),
        (" SWOT ", "swot"),
    ],
)
def test_local_business_supported_output_types_normalize(requested, expected):
    service = LocalBusinessAgentService()

    result = service.create_brief(
        LocalBusinessRequest(
            business_idea="Offer a local service for manual business planning.",
            target_customer="Local founders",
            desired_output_type=requested,
        )
    )

    assert result["desiredOutputType"] == expected


def test_local_business_unsupported_output_type_falls_back_safely():
    service = LocalBusinessAgentService()

    result = service.create_brief(
        LocalBusinessRequest(
            business_idea="Offer a local planning worksheet.",
            target_customer="Local founders",
            desired_output_type="market_validated_plan",
        )
    )

    assert result["desiredOutputType"] == "business_brief"
    assert result["safety"]["externalServices"] is False
    assert result["safety"]["professionalAdviceValidation"] is False
    assert result["safety"]["complianceCertification"] is False


def test_local_business_thin_input_reports_warnings_open_questions_and_limitations():
    service = LocalBusinessAgentService()

    result = service.create_brief(LocalBusinessRequest(business_idea="Start a local business."))

    assert any("Business planning input is thin" in warning for warning in result["warnings"])
    assert any("Thin input limits specificity" in limitation for limitation in result["limitations"])
    assert len(result["openQuestions"]) >= 5
    assert any("Add missing customer" in item for item in result["launchChecklist"])


def test_local_business_output_does_not_claim_external_validation_or_business_outcomes():
    service = LocalBusinessAgentService()

    result = service.create_brief(
        LocalBusinessRequest(
            business_idea="Offer a local workshop for small business planning.",
            target_customer="First-time local founders",
            problem="They need a simple starting plan.",
            offer="A manual planning session.",
            pricing_notes="Review simple pricing manually.",
            operations_notes="Use a limited pilot format.",
            marketing_notes="Invite feedback manually.",
            risks=["Demand may be unclear"],
        )
    )
    output_text = str(result).lower()
    forbidden_claims = [
        "market validated",
        "revenue validated",
        "profitability proven",
        "market size proven",
        "demand proven",
        "compliance certified",
        "tax advice provided",
        "legal advice provided",
        "financial advice provided",
        "accounting advice provided",
        "investment advice provided",
        "payments processed",
        "email sent",
        "post published",
        "crm accessed",
    ]

    assert all(claim not in output_text for claim in forbidden_claims)
    assert "no external market validation" in output_text
    assert "no profitability" in output_text
    assert "qualified human or professional review" in output_text


def test_local_business_launch_checklist_stays_manual_only():
    service = LocalBusinessAgentService()

    result = service.create_brief(
        LocalBusinessRequest(
            business_idea="Offer local planning help.",
            target_customer="Solo founders",
            offer="Manual planning review",
            desired_output_type="launch_checklist",
        )
    )
    checklist_text = " ".join(result["launchChecklist"]).lower()

    assert "do not create tasks" in checklist_text
    assert "calendar events" in checklist_text
    assert "emails" in checklist_text
    assert "posts" in checklist_text
    assert "purchases" in checklist_text
    assert "invoices" in checklist_text
    assert "files" in checklist_text
    assert "records" in checklist_text


def test_local_business_safety_flags_disable_external_persistence_and_mutation_behavior():
    service = LocalBusinessAgentService()

    result = service.create_brief(
        LocalBusinessRequest(
            business_idea="Offer a local-only business planning worksheet.",
            target_customer="Local founders",
        )
    )
    safety = result["safety"]

    assert safety["localOnly"] is True
    assert safety["responseOnly"] is True
    assert safety["manualInputOnly"] is True
    assert safety["externalServices"] is False
    assert safety["paidApis"] is False
    assert safety["webBrowsing"] is False
    assert safety["connectorExecution"] is False
    assert safety["oauth"] is False
    assert safety["accountAccess"] is False
    assert safety["financeConnectorAccess"] is False
    assert safety["paymentActions"] is False
    assert safety["purchases"] is False
    assert safety["emailSending"] is False
    assert safety["publicPosting"] is False
    assert safety["crmAccess"] is False
    assert safety["fileReads"] is False
    assert safety["fileWrites"] is False
    assert safety["dbWrites"] is False
    assert safety["taskPersistence"] is False
    assert safety["shellExecution"] is False
    assert safety["mutation"] is False
    assert safety["professionalAdviceValidation"] is False
    assert safety["complianceCertification"] is False


def test_local_business_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_business_agent").local_business_agent).lower()
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


def test_local_business_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalBusinessInput.model_validate(
            {
                "businessIdea": "Offer local planning help.",
                "extraField": "not allowed",
            }
        )


def test_local_business_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(
        route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/business/local-brief"
    )
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
