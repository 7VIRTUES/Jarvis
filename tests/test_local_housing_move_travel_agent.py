import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_housing_move_travel_agent import LocalHousingMoveTravelAgentService, LocalHousingMoveTravelRequest


def test_local_housing_move_travel_endpoint_returns_structured_plan():
    payload = app_module.LocalHousingMoveTravelInput(
        planName="Boston Move Plan",
        destination="Boston campus area",
        housingGoal="Compare user-provided housing options and prepare a manual move checklist.",
        timeline="Move before the fall term starts.",
        budgetNotes="Estimate rent, deposit, utilities, moving supplies, travel, and emergency buffer manually.",
        housingOptions=["Shared apartment near transit", "Student housing option from user notes"],
        moveItems=["Laptop and chargers", "Clothes", "Bedding", "Important documents"],
        transportationNotes="Compare driving with shipped boxes against flying with checked bags.",
        commuteNotes="Review walking, transit, and backup commute assumptions from user notes.",
        utilitySetupNotes="Internet, mail forwarding, renter insurance, and move-in inspection need manual confirmation.",
        constraints=["Manual planning only"],
        priorities=["Protect budget buffer", "Keep commute reliable"],
        desiredOutputType="move_brief",
    )

    result = app_module.create_local_housing_move_travel_plan(payload)

    assert result["agentId"] == "local_housing_move_travel_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_housing_move_travel_planning"
    assert result["planName"] == "Boston Move Plan"
    assert result["destination"] == "Boston campus area"
    assert result["housingGoal"] == "Compare user-provided housing options and prepare a manual move checklist."
    assert result["desiredOutputType"] == "move_brief"
    assert result["moveFocus"]
    assert result["housingSummary"]
    assert result["housingComparison"]
    assert result["movePlan"]
    assert result["packingPlan"]
    assert result["driveVsFlyPlan"]
    assert result["commuteReview"]
    assert result["setupChecklist"]
    assert result["travelPrepPlan"]
    assert result["budgetNotes"]
    assert result["nextActions"]
    assert result["openQuestions"]
    assert result["warnings"]
    assert "Based only on user-provided housing" in result["limitations"][0]
    assert result["safety"]["localOnly"] is True


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("move_brief", "move_brief"),
        ("housing_comparison", "housing_comparison"),
        ("move_plan", "move_plan"),
        ("packing_plan", "packing_plan"),
        ("drive_vs_fly_plan", "drive_vs_fly_plan"),
        ("commute_review", "commute_review"),
        ("setup_checklist", "setup_checklist"),
        ("travel_prep_plan", "travel_prep_plan"),
        (" COMMUTE_REVIEW ", "commute_review"),
    ],
)
def test_local_housing_move_travel_supported_output_types_normalize(requested, expected):
    service = LocalHousingMoveTravelAgentService()

    result = service.create_plan(
        LocalHousingMoveTravelRequest(
            housing_goal="Prepare a manual move and commute plan.",
            desired_output_type=requested,
        )
    )

    assert result["desiredOutputType"] == expected


def test_local_housing_move_travel_unsupported_output_type_falls_back_safely():
    service = LocalHousingMoveTravelAgentService()

    result = service.create_plan(
        LocalHousingMoveTravelRequest(
            housing_goal="Prepare a move plan.",
            desired_output_type="book_sign_pay_and_reserve",
        )
    )

    assert result["desiredOutputType"] == "move_brief"
    assert result["safety"]["bookingActions"] is False
    assert result["safety"]["leaseActions"] is False
    assert result["safety"]["paymentActions"] is False


def test_local_housing_move_travel_thin_input_reports_warnings_and_questions():
    service = LocalHousingMoveTravelAgentService()

    result = service.create_plan(LocalHousingMoveTravelRequest(housing_goal=""))

    assert any("input is thin" in warning.lower() for warning in result["warnings"])
    assert any("Thin input limits specificity" in limitation for limitation in result["limitations"])
    assert result["openQuestions"]
    assert result["nextActions"]


def test_local_housing_move_travel_output_includes_housing_move_packing_commute_setup_and_travel_sections():
    service = LocalHousingMoveTravelAgentService()

    result = service.create_plan(
        LocalHousingMoveTravelRequest(
            housing_goal="Compare housing options and prepare for move-in.",
            destination="Boston campus area",
            timeline="August move-in",
            budget_notes="Rent, deposit, utilities, and travel estimates.",
            housing_options=["Apartment option", "Student housing option"],
            move_items=["Bedding", "Laptop", "Documents"],
            transportation_notes="Drive versus fly notes.",
            commute_notes="Transit and walking notes.",
            utility_setup_notes="Internet and renter insurance notes.",
            desired_output_type="housing_comparison",
        )
    )

    assert result["housingSummary"]
    assert result["housingComparison"]
    assert result["movePlan"]
    assert result["packingPlan"]
    assert result["driveVsFlyPlan"]
    assert result["commuteReview"]
    assert result["setupChecklist"]
    assert result["travelPrepPlan"]


def test_local_housing_move_travel_output_does_not_claim_live_listings_bookings_payments_or_validation():
    service = LocalHousingMoveTravelAgentService()

    result = service.create_plan(
        LocalHousingMoveTravelRequest(
            housing_goal="Find live listings, book travel, pay deposit, apply, sign lease, and verify commute time.",
            desired_output_type="housing_comparison",
        )
    )
    output_text = str(result).lower()
    forbidden_claims = [
        "listing verified",
        "booking completed",
        "reservation completed",
        "payment completed",
        "application submitted",
        "lease signed",
        "landlord messaged",
        "tour scheduled",
        "ticket purchased",
        "location accessed",
        "price verified",
        "housing approved",
        "commute time guaranteed",
        "safety validated",
    ]

    assert all(claim not in output_text for claim in forbidden_claims)
    assert "no maps" in output_text
    assert "no browsing" in output_text
    assert "no live availability" in output_text
    assert "no live availability, current price" in output_text


def test_local_housing_move_travel_high_stakes_inputs_include_official_or_professional_confirmation_limitations():
    service = LocalHousingMoveTravelAgentService()

    result = service.create_plan(
        LocalHousingMoveTravelRequest(
            housing_goal="Review lease, deposit, school housing, insurance, legal terms, and neighborhood safety.",
            desired_output_type="move_brief",
        )
    )

    assert any("official confirmation" in warning for warning in result["warnings"])
    assert any("qualified professionals" in limitation for limitation in result["limitations"])
    assert any("official sources or qualified professionals" in action for action in result["nextActions"])


def test_local_housing_move_travel_safety_flags_disable_connectors_location_bookings_payments_persistence_mutation_and_certification():
    service = LocalHousingMoveTravelAgentService()

    result = service.create_plan(LocalHousingMoveTravelRequest(housing_goal="Prepare a move plan."))
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
    assert safety["mapAccess"] is False
    assert safety["locationAccess"] is False
    assert safety["bookingActions"] is False
    assert safety["leaseActions"] is False
    assert safety["applicationSubmission"] is False
    assert safety["paymentActions"] is False
    assert safety["emailSending"] is False
    assert safety["calendarAccess"] is False
    assert safety["contactAccess"] is False
    assert safety["fileReads"] is False
    assert safety["fileWrites"] is False
    assert safety["dbWrites"] is False
    assert safety["taskPersistence"] is False
    assert safety["shellExecution"] is False
    assert safety["mutation"] is False
    assert safety["legalValidation"] is False
    assert safety["safetyValidation"] is False
    assert safety["priceAvailabilityValidation"] is False
    assert safety["certificationClaims"] is False


def test_local_housing_move_travel_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_housing_move_travel_agent").local_housing_move_travel_agent).lower()
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


def test_local_housing_move_travel_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalHousingMoveTravelInput.model_validate(
            {
                "housingGoal": "Prepare a move plan.",
                "bookingPassword": "not allowed",
            }
        )


def test_local_housing_move_travel_requires_housing_goal_in_endpoint_input():
    with pytest.raises(ValidationError):
        app_module.LocalHousingMoveTravelInput.model_validate({"planName": "Missing goal"})


def test_local_housing_move_travel_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(
        route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/housing-move-travel/local-plan"
    )
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
