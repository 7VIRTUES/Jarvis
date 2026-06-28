import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_emergency_preparedness_agent import LocalEmergencyPreparednessAgentService, LocalEmergencyPreparednessRequest
from jarvis_core.local_home_room_living_space_agent import LocalHomeRoomLivingSpaceAgentService, LocalHomeRoomLivingSpaceRequest
from jarvis_core.local_legal_immigration_official_agent import (
    LocalLegalImmigrationOfficialAgentService,
    LocalLegalImmigrationOfficialRequest,
)


def test_local_home_room_living_space_endpoint_returns_structured_plan():
    payload = app_module.LocalHomeRoomLivingSpaceInput(
        request="Make a small apartment room setup plan for study, sleep, storage, and exercise.",
        outputType="room_setup_plan",
        roomType="small apartment bedroom",
        livingSituation="Shared apartment",
        spaceGoal="Create zones for study, sleep, storage, and exercise.",
        currentItems=["Bed", "Desk"],
        itemsToBuyOrConsider=["Desk lamp"],
        budgetLevel="low",
        roomDimensionsOrConstraints="Small room with one window.",
        storageConstraints="Limited closet.",
        cleaningOrMaintenanceNeeds=["Weekly floor reset"],
        aestheticPreferences=["Calm"],
        productivityOrSleepGoals=["Better study focus"],
        safetyOrAccessibilityNotes="Keep walkway clear.",
        timeline="This weekend",
    )

    result = app_module.create_local_home_room_living_space_plan(payload)

    assert result["agent_id"] == "local_home_room_living_space"
    assert result["agentId"] == "local_home_room_living_space"
    assert result["status"] == "local_only"
    assert result["output_type"] == "room_setup_plan"
    for field in ["title", "summary", "assumptions", "recommended_plan", "room_zones", "item_suggestions", "step_by_step", "checklist", "budget_notes", "timeline", "safety_notes", "limitations", "follow_up_questions"]:
        assert result[field]
    assert result["safety"]["localOnly"] is True
    assert result["safety"]["smartHomeAccess"] is False
    assert result["safety"]["landlordPortalAccess"] is False
    assert result["safety"]["paymentAccess"] is False


def test_local_legal_immigration_official_endpoint_returns_structured_plan():
    payload = app_module.LocalLegalImmigrationOfficialInput(
        request="Make a document checklist for an immigration appointment based only on this summary.",
        outputType="document_checklist",
        matterType="immigration appointment preparation",
        jurisdictionOrCountryIfUserProvided="User-provided country context",
        currentStatus="Upcoming appointment.",
        documentList=["Passport", "Appointment notice"],
        deadlinesOrDates=["Appointment date from user notes"],
        officeOrAgencyNameIfUserProvided="User-provided office",
        userQuestions=["What should I ask a qualified professional?"],
        desiredOutcome="Arrive prepared.",
        riskLevelOrUrgency="Careful review needed.",
    )

    result = app_module.create_local_legal_immigration_official_plan(payload)

    assert result["agent_id"] == "local_legal_immigration_official_matters"
    assert result["agentId"] == "local_legal_immigration_official_matters"
    assert result["status"] == "local_only"
    assert result["output_type"] == "document_checklist"
    for field in ["title", "summary", "assumptions", "non_legal_information", "recommended_plan", "document_checklist", "questions_to_ask", "deadlines_or_timeline", "risk_flags", "draft_outline", "limitations", "professional_help_reminder", "follow_up_questions"]:
        assert result[field]
    assert result["safety"]["legalAdvice"] is False
    assert result["safety"]["governmentPortalAccess"] is False
    assert result["safety"]["applicationFiling"] is False


def test_local_emergency_preparedness_endpoint_returns_structured_plan():
    payload = app_module.LocalEmergencyPreparednessInput(
        request="Make a basic car emergency kit checklist for winter driving.",
        outputType="car_emergency_kit",
        scenarioType="winter driving preparedness",
        householdSize="1 driver",
        currentSupplies=["Blanket", "Flashlight"],
        vehicleOrTravelContext="Commutes by car during winter.",
        budgetLevel="low",
        timeHorizon="Before the next cold-weather trip.",
        communicationContactsSummary="User will keep contact list manually.",
    )

    result = app_module.create_local_emergency_preparedness_plan(payload)

    assert result["agent_id"] == "local_emergency_preparedness"
    assert result["agentId"] == "local_emergency_preparedness"
    assert result["status"] == "local_only"
    assert result["output_type"] == "car_emergency_kit"
    for field in ["title", "summary", "assumptions", "recommended_plan", "priority_actions", "supply_checklist", "communication_steps", "timeline", "budget_notes", "safety_notes", "urgent_warning", "limitations", "follow_up_questions"]:
        assert result[field]
    assert result["safety"]["emergencyServicesAccess"] is False
    assert result["safety"]["emergencyCalling"] is False
    assert result["safety"]["weatherServiceAccess"] is False


@pytest.mark.parametrize(
    ("service", "request", "field", "values"),
    [
        (
            LocalHomeRoomLivingSpaceAgentService(),
            LocalHomeRoomLivingSpaceRequest(request="Plan a room."),
            "output_type",
            [
                "room_setup_plan",
                "cleaning_plan",
                "storage_plan",
                "furniture_layout",
                "move_in_plan",
                "maintenance_checklist",
                "small_space_plan",
                "comfort_upgrade_plan",
                "study_or_work_zone_plan",
                "comparison",
                "checklist",
                "summary",
            ],
        ),
        (
            LocalLegalImmigrationOfficialAgentService(),
            LocalLegalImmigrationOfficialRequest(request="Plan official paperwork."),
            "output_type",
            [
                "document_checklist",
                "appointment_prep",
                "question_list",
                "deadline_tracker",
                "plain_language_summary",
                "official_task_plan",
                "form_prep_outline",
                "call_script",
                "email_draft_outline",
                "risk_flags",
                "comparison",
                "checklist",
                "summary",
            ],
        ),
        (
            LocalEmergencyPreparednessAgentService(),
            LocalEmergencyPreparednessRequest(request="Plan supplies."),
            "output_type",
            [
                "go_bag_checklist",
                "emergency_plan",
                "severe_weather_plan",
                "power_outage_plan",
                "car_emergency_kit",
                "evacuation_prep",
                "communication_plan",
                "supply_gap_analysis",
                "pet_preparedness_plan",
                "post_event_checklist",
                "comparison",
                "checklist",
                "summary",
            ],
        ),
    ],
)
def test_new_local_agents_supported_output_types_normalize(service, request, field, values):
    for value in values:
        result = service.create_plan(request.__class__(request="Manual local planning.", output_type=value.upper()))
        assert result[field] == value


def test_new_local_agents_include_manual_local_limitations_and_no_prohibited_capabilities():
    home = LocalHomeRoomLivingSpaceAgentService().create_plan(LocalHomeRoomLivingSpaceRequest(request="Plan a room."))
    legal = LocalLegalImmigrationOfficialAgentService().create_plan(LocalLegalImmigrationOfficialRequest(request="Plan forms."))
    emergency = LocalEmergencyPreparednessAgentService().create_plan(LocalEmergencyPreparednessRequest(request="Plan a go bag."))

    for result in [home, legal, emergency]:
        output_text = str(result).lower()
        assert result["safety"]["localOnly"] is True
        assert result["safety"]["responseOnly"] is True
        assert result["safety"]["manualInputOnly"] is True
        assert result["safety"]["externalServices"] is False
        assert result["safety"]["connectors"] is False
        assert result["safety"]["accountAccess"] is False
        assert result["safety"]["fileWrites"] is False
        assert result["safety"]["taskPersistence"] is False
        assert result["safety"]["mutation"] is False
        assert "based only on user-provided" in output_text or "based only on user-provided" in output_text

    assert home["safety"]["deviceControl"] is False
    assert home["safety"]["purchases"] is False
    assert "no smart-home device" in str(home).lower()
    assert legal["safety"]["legalAdvice"] is False
    assert legal["safety"]["emailSending"] is False
    assert "not legal advice or immigration advice" in str(legal).lower()
    assert "qualified attorney" in str(legal).lower()
    assert emergency["safety"]["emergencyCalling"] is False
    assert emergency["safety"]["alertSending"] is False
    assert "contact local emergency services" in str(emergency).lower()


def test_legal_agent_escalates_urgent_official_risk_flags_without_legal_advice():
    result = LocalLegalImmigrationOfficialAgentService().create_plan(
        LocalLegalImmigrationOfficialRequest(
            request="I have a removal notice, court date, and missed deadline.",
            output_type="risk_flags",
        )
    )
    output_text = str(result).lower()

    assert "removal" in output_text
    assert "court date" in output_text
    assert "deadline" in output_text
    assert "qualified help" in output_text
    assert "no legal advice" in output_text


def test_emergency_agent_warns_for_immediate_danger_without_calling_services():
    result = LocalEmergencyPreparednessAgentService().create_plan(
        LocalEmergencyPreparednessRequest(
            request="There is a gas leak and carbon monoxide symptoms right now.",
            output_type="emergency_plan",
        )
    )
    output_text = str(result).lower()

    assert "immediate danger" in output_text
    assert "contact local emergency services" in output_text
    assert "leave the area if safe" in output_text
    assert result["safety"]["emergencyCalling"] is False


def test_new_local_agent_requests_reject_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalHomeRoomLivingSpaceInput.model_validate({"request": "Plan room.", "storeAccount": "not allowed"})
    with pytest.raises(ValidationError):
        app_module.LocalLegalImmigrationOfficialInput.model_validate({"request": "Plan forms.", "portalLogin": "not allowed"})
    with pytest.raises(ValidationError):
        app_module.LocalEmergencyPreparednessInput.model_validate({"request": "Plan bag.", "contactPhone": "not allowed"})


def test_new_local_agent_endpoints_are_guarded_by_dashboard_lan_guard():
    paths = {
        "/agents/home-room-living-space/local-plan",
        "/agents/legal-immigration-official/local-plan",
        "/agents/emergency-preparedness/local-plan",
    }

    for path in paths:
        route = next(route for route in app_module.app.routes if getattr(route, "path", None) == path)
        dependency_calls = {dependency.call for dependency in route.dependant.dependencies}
        assert require_dashboard_lan_access in dependency_calls


def test_new_local_agent_sources_have_no_network_file_shell_api_or_persistence_calls():
    modules = [
        __import__("jarvis_core.local_home_room_living_space_agent").local_home_room_living_space_agent,
        __import__("jarvis_core.local_legal_immigration_official_agent").local_legal_immigration_official_agent,
        __import__("jarvis_core.local_emergency_preparedness_agent").local_emergency_preparedness_agent,
    ]
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
        "smtp.",
        "imap.",
        "openai",
        "anthropic",
        "gemini",
    ]

    for module in modules:
        source = inspect.getsource(module).lower()
        assert all(token not in source for token in forbidden)
