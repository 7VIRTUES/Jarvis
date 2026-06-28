import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_vehicle_devices_gear_agent import LocalVehicleDevicesGearAgentService, LocalVehicleDevicesGearRequest


def test_local_vehicle_devices_gear_endpoint_returns_structured_plan():
    payload = app_module.LocalVehicleDevicesGearInput(
        profileName="Local Gear Profile",
        gearGoal="Prepare a manual readiness checklist for a campus project day with laptop, scooter, and drone gear.",
        vehicleNotes="Car may be used for transport; confirm tire pressure and fuel manually before leaving.",
        deviceNotes="Laptop, phone, chargers, portable battery, and camera need a pre-trip check.",
        droneScooterNotes="Drone and scooter should be reviewed after checking local rules and battery condition manually.",
        inventoryItems=["Laptop", "Phone", "Chargers", "Portable battery", "Drone case"],
        maintenanceConcerns=["Battery condition", "Tire pressure"],
        troubleshootingNotes="Phone battery has drained quickly recently.",
        packingNotes="Pack light but include backup charging and safety gear.",
        constraints=["Manual planning only"],
        priorities=["Safety", "Battery readiness"],
        desiredOutputType="gear_brief",
    )

    result = app_module.create_local_vehicle_devices_gear_plan(payload)

    assert result["agentId"] == "local_vehicle_devices_gear_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_vehicle_devices_gear_planning"
    assert result["profileName"] == "Local Gear Profile"
    assert result["gearGoal"] == "Prepare a manual readiness checklist for a campus project day with laptop, scooter, and drone gear."
    assert result["desiredOutputType"] == "gear_brief"
    assert result["gearFocus"]
    assert result["vehicleMaintenancePlan"]
    assert result["deviceTroubleshootingPlan"]
    assert result["droneScooterPrep"]
    assert result["gearInventory"]
    assert result["packingPlan"]
    assert result["setupChecklist"]
    assert result["riskReview"]
    assert result["nextActions"]
    assert result["openQuestions"]
    assert result["warnings"]
    assert "Based only on user-provided vehicle" in result["limitations"][0]
    assert result["safety"]["localOnly"] is True


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("gear_brief", "gear_brief"),
        ("vehicle_maintenance_plan", "vehicle_maintenance_plan"),
        ("device_troubleshooting_plan", "device_troubleshooting_plan"),
        ("drone_scooter_prep", "drone_scooter_prep"),
        ("gear_inventory", "gear_inventory"),
        ("packing_plan", "packing_plan"),
        ("setup_checklist", "setup_checklist"),
        ("risk_review", "risk_review"),
        (" SETUP_CHECKLIST ", "setup_checklist"),
    ],
)
def test_local_vehicle_devices_gear_supported_output_types_normalize(requested, expected):
    service = LocalVehicleDevicesGearAgentService()

    result = service.create_plan(LocalVehicleDevicesGearRequest(gear_goal="Prepare gear.", desired_output_type=requested))

    assert result["desiredOutputType"] == expected


def test_local_vehicle_devices_gear_unsupported_output_type_falls_back_safely():
    service = LocalVehicleDevicesGearAgentService()

    result = service.create_plan(
        LocalVehicleDevicesGearRequest(
            gear_goal="Prepare gear.",
            desired_output_type="diagnose_control_repair_purchase_and_fly",
        )
    )

    assert result["desiredOutputType"] == "gear_brief"
    assert result["safety"]["deviceDiagnostics"] is False
    assert result["safety"]["deviceControl"] is False
    assert result["safety"]["repairActions"] is False
    assert result["safety"]["flightActions"] is False


def test_local_vehicle_devices_gear_thin_input_reports_warnings_and_questions():
    service = LocalVehicleDevicesGearAgentService()

    result = service.create_plan(LocalVehicleDevicesGearRequest(gear_goal=""))

    assert any("input is thin" in warning.lower() for warning in result["warnings"])
    assert any("Thin input limits specificity" in limitation for limitation in result["limitations"])
    assert result["openQuestions"]
    assert result["nextActions"]


def test_local_vehicle_devices_gear_output_includes_vehicle_device_drone_inventory_packing_setup_and_risk_sections():
    service = LocalVehicleDevicesGearAgentService()

    result = service.create_plan(
        LocalVehicleDevicesGearRequest(
            gear_goal="Prepare a field kit.",
            vehicle_notes="Use car for transport.",
            device_notes="Laptop and phone.",
            drone_scooter_notes="Scooter helmet and drone case.",
            inventory_items=["Laptop", "Helmet"],
            maintenance_concerns=["Battery condition"],
            packing_notes="Bring chargers.",
            desired_output_type="risk_review",
        )
    )

    assert result["vehicleMaintenancePlan"]
    assert result["deviceTroubleshootingPlan"]
    assert result["droneScooterPrep"]
    assert result["gearInventory"]
    assert result["packingPlan"]
    assert result["setupChecklist"]
    assert result["riskReview"]


def test_local_vehicle_devices_gear_output_does_not_claim_diagnostics_control_repairs_updates_resets_purchases_bookings_flights_or_live_verification():
    service = LocalVehicleDevicesGearAgentService()

    result = service.create_plan(
        LocalVehicleDevicesGearRequest(
            gear_goal="Run diagnostics, control the car and phone, read files, repair the device, update firmware, reset it, buy parts, book service, fly the drone, and verify live maps.",
            desired_output_type="risk_review",
        )
    )
    output_text = str(result).lower()
    forbidden_claims = [
        "diagnostics completed",
        "device controlled",
        "vehicle controlled",
        "files read",
        "repair completed",
        "update installed",
        "reset completed",
        "purchase completed",
        "booking completed",
        "flight completed",
        "live map verified",
        "repair guaranteed",
        "data recovery guaranteed",
    ]

    assert all(claim not in output_text for claim in forbidden_claims)
    assert "does not run diagnostics" in output_text
    assert "no device access" in output_text
    assert "no mechanic validation" in output_text


def test_local_vehicle_devices_gear_high_risk_inputs_include_official_manual_or_professional_confirmation_limitations():
    service = LocalVehicleDevicesGearAgentService()

    result = service.create_plan(
        LocalVehicleDevicesGearRequest(
            gear_goal="Review brake, battery, electrical, drone flight, airspace, warranty, water damage, and data loss concerns.",
            desired_output_type="risk_review",
        )
    )

    assert any("official, manual, or professional confirmation" in warning for warning in result["warnings"])
    assert any("qualified professional" in limitation for limitation in result["limitations"])
    assert any("qualified professional confirmation" in action for action in result["nextActions"])


def test_local_vehicle_devices_gear_safety_flags_disable_connectors_accounts_files_diagnostics_controls_location_maps_persistence_mutation_and_certification():
    service = LocalVehicleDevicesGearAgentService()

    result = service.create_plan(LocalVehicleDevicesGearRequest(gear_goal="Prepare gear."))
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
    assert safety["shellExecution"] is False
    assert safety["deviceDiagnostics"] is False
    assert safety["deviceControl"] is False
    assert safety["vehicleDiagnostics"] is False
    assert safety["vehicleControl"] is False
    assert safety["obdAccess"] is False
    assert safety["bluetoothAccess"] is False
    assert safety["networkScanning"] is False
    assert safety["locationAccess"] is False
    assert safety["mapAccess"] is False
    assert safety["droneControl"] is False
    assert safety["flightActions"] is False
    assert safety["repairActions"] is False
    assert safety["updateActions"] is False
    assert safety["resetActions"] is False
    assert safety["downloadActions"] is False
    assert safety["purchaseActions"] is False
    assert safety["bookingActions"] is False
    assert safety["mutation"] is False
    assert safety["professionalValidation"] is False
    assert safety["legalValidation"] is False
    assert safety["warrantyValidation"] is False
    assert safety["airspaceValidation"] is False
    assert safety["certificationClaims"] is False


def test_local_vehicle_devices_gear_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_vehicle_devices_gear_agent").local_vehicle_devices_gear_agent).lower()
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


def test_local_vehicle_devices_gear_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalVehicleDevicesGearInput.model_validate(
            {
                "gearGoal": "Prepare gear.",
                "devicePassword": "not allowed",
            }
        )


def test_local_vehicle_devices_gear_requires_gear_goal_in_endpoint_input():
    with pytest.raises(ValidationError):
        app_module.LocalVehicleDevicesGearInput.model_validate({"profileName": "Missing goal"})


def test_local_vehicle_devices_gear_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/vehicle-devices-gear/local-plan")
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
