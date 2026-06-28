from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_vehicle_devices_gear_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_vehicle_devices_gear_planning"
SUPPORTED_OUTPUT_TYPES = (
    "gear_brief",
    "vehicle_maintenance_plan",
    "device_troubleshooting_plan",
    "drone_scooter_prep",
    "gear_inventory",
    "packing_plan",
    "setup_checklist",
    "risk_review",
)


@dataclass(frozen=True)
class LocalVehicleDevicesGearRequest:
    gear_goal: str
    profile_name: str = ""
    vehicle_notes: str = ""
    device_notes: str = ""
    drone_scooter_notes: str = ""
    inventory_items: list[str] = field(default_factory=list)
    maintenance_concerns: list[str] = field(default_factory=list)
    troubleshooting_notes: str = ""
    packing_notes: str = ""
    constraints: list[str] = field(default_factory=list)
    priorities: list[str] = field(default_factory=list)
    desired_output_type: str = "gear_brief"


class LocalVehicleDevicesGearAgentService:
    def create_plan(self, request: LocalVehicleDevicesGearRequest) -> dict[str, Any]:
        profile_name = _clean_text(request.profile_name) or "Local gear profile"
        gear_goal = _clean_text(request.gear_goal)
        vehicle_notes = _clean_text(request.vehicle_notes)
        device_notes = _clean_text(request.device_notes)
        drone_scooter_notes = _clean_text(request.drone_scooter_notes)
        inventory_items = _clean_list(request.inventory_items, limit=14)
        maintenance_concerns = _clean_list(request.maintenance_concerns)
        troubleshooting_notes = _clean_text(request.troubleshooting_notes)
        packing_notes = _clean_text(request.packing_notes)
        constraints = _clean_list(request.constraints)
        priorities = _clean_list(request.priorities)
        desired_output_type = _normalize_output_type(request.desired_output_type)
        thin_input = _thin_input(
            gear_goal,
            vehicle_notes,
            device_notes,
            drone_scooter_notes,
            inventory_items,
            maintenance_concerns,
            troubleshooting_notes,
            packing_notes,
            constraints,
            priorities,
        )
        high_risk_context = _high_risk_context(
            gear_goal,
            vehicle_notes,
            device_notes,
            drone_scooter_notes,
            maintenance_concerns,
            troubleshooting_notes,
            constraints,
        )

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "profileName": profile_name,
            "gearGoal": gear_goal,
            "desiredOutputType": desired_output_type,
            "gearFocus": _gear_focus(gear_goal, inventory_items, priorities, desired_output_type, thin_input),
            "vehicleMaintenancePlan": _vehicle_maintenance_plan(vehicle_notes, maintenance_concerns, constraints, high_risk_context),
            "deviceTroubleshootingPlan": _device_troubleshooting_plan(device_notes, troubleshooting_notes, constraints, high_risk_context),
            "droneScooterPrep": _drone_scooter_prep(drone_scooter_notes, maintenance_concerns, constraints, high_risk_context),
            "gearInventory": _gear_inventory(inventory_items, priorities, packing_notes),
            "packingPlan": _packing_plan(packing_notes, inventory_items, priorities, constraints),
            "setupChecklist": _setup_checklist(gear_goal, vehicle_notes, device_notes, drone_scooter_notes, inventory_items),
            "riskReview": _risk_review(gear_goal, vehicle_notes, device_notes, drone_scooter_notes, maintenance_concerns, troubleshooting_notes, high_risk_context),
            "nextActions": _next_actions(desired_output_type, thin_input, high_risk_context),
            "openQuestions": _open_questions(
                gear_goal,
                vehicle_notes,
                device_notes,
                drone_scooter_notes,
                inventory_items,
                maintenance_concerns,
                troubleshooting_notes,
                packing_notes,
                constraints,
                priorities,
            ),
            "warnings": _warnings(thin_input, high_risk_context),
            "limitations": _limitations(thin_input, high_risk_context),
            "safety": local_vehicle_devices_gear_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_vehicle_devices_gear_dashboard_summary()


def local_vehicle_devices_gear_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Vehicle / Devices / Gear Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/vehicle-devices-gear/local-plan",
        "outputTypes": list(SUPPORTED_OUTPUT_TYPES),
        "responseOnly": True,
        "manualInputOnly": True,
        "localOnly": True,
        "externalServices": False,
        "connectors": False,
        "oauth": False,
        "OAuth": False,
        "accountAccess": False,
        "webBrowsing": False,
        "paidApis": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "deviceDiagnostics": False,
        "deviceControl": False,
        "vehicleDiagnostics": False,
        "vehicleControl": False,
        "obdAccess": False,
        "bluetoothAccess": False,
        "networkScanning": False,
        "locationAccess": False,
        "mapAccess": False,
        "droneControl": False,
        "flightActions": False,
        "repairActions": False,
        "updateActions": False,
        "resetActions": False,
        "downloadActions": False,
        "purchaseActions": False,
        "bookingActions": False,
        "mutation": False,
        "professionalValidation": False,
        "legalValidation": False,
        "warrantyValidation": False,
        "airspaceValidation": False,
        "certificationClaims": False,
        "limitations": ["based only on user-provided vehicle, device, gear, maintenance, and packing notes"],
    }


def local_vehicle_devices_gear_safety() -> dict[str, bool]:
    return {
        "localOnly": True,
        "responseOnly": True,
        "manualInputOnly": True,
        "externalServices": False,
        "connectors": False,
        "oauth": False,
        "OAuth": False,
        "accountAccess": False,
        "webBrowsing": False,
        "paidApis": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "deviceDiagnostics": False,
        "deviceControl": False,
        "vehicleDiagnostics": False,
        "vehicleControl": False,
        "obdAccess": False,
        "bluetoothAccess": False,
        "networkScanning": False,
        "locationAccess": False,
        "mapAccess": False,
        "droneControl": False,
        "flightActions": False,
        "repairActions": False,
        "updateActions": False,
        "resetActions": False,
        "downloadActions": False,
        "purchaseActions": False,
        "bookingActions": False,
        "mutation": False,
        "professionalValidation": False,
        "legalValidation": False,
        "warrantyValidation": False,
        "airspaceValidation": False,
        "certificationClaims": False,
    }


def _normalize_output_type(value: str) -> str:
    normalized = (value or "gear_brief").strip().lower()
    return normalized if normalized in SUPPORTED_OUTPUT_TYPES else "gear_brief"


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def _clean_list(values: list[str], limit: int = 10) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = _clean_text(value)
        key = item.lower()
        if item and key not in seen:
            cleaned.append(item)
            seen.add(key)
    return cleaned[:limit]


def _thin_input(
    gear_goal: str,
    vehicle_notes: str,
    device_notes: str,
    drone_scooter_notes: str,
    inventory_items: list[str],
    maintenance_concerns: list[str],
    troubleshooting_notes: str,
    packing_notes: str,
    constraints: list[str],
    priorities: list[str],
) -> bool:
    return not any(
        [
            gear_goal,
            vehicle_notes,
            device_notes,
            drone_scooter_notes,
            inventory_items,
            maintenance_concerns,
            troubleshooting_notes,
            packing_notes,
            constraints,
            priorities,
        ]
    )


def _high_risk_context(
    gear_goal: str,
    vehicle_notes: str,
    device_notes: str,
    drone_scooter_notes: str,
    maintenance_concerns: list[str],
    troubleshooting_notes: str,
    constraints: list[str],
) -> bool:
    text = " ".join(
        [
            gear_goal,
            vehicle_notes,
            device_notes,
            drone_scooter_notes,
            " ".join(maintenance_concerns),
            troubleshooting_notes,
            " ".join(constraints),
        ]
    ).lower()
    terms = (
        "brake",
        "tire",
        "battery",
        "electrical",
        "smoke",
        "burning",
        "water damage",
        "data loss",
        "drone",
        "flight",
        "airspace",
        "traffic",
        "warranty",
        "crash",
        "danger",
        "overheat",
    )
    return any(term in text for term in terms)


def _gear_focus(
    gear_goal: str,
    inventory_items: list[str],
    priorities: list[str],
    desired_output_type: str,
    thin_input: bool,
) -> list[str]:
    if thin_input:
        return [
            "Capture the gear goal, vehicle notes, device notes, drone or scooter notes, inventory, maintenance concerns, troubleshooting notes, packing notes, constraints, and priorities before relying on the plan.",
            "Keep the result as manual planning only because no devices, vehicles, files, accounts, locations, maps, controllers, portals, apps, or external services are accessed.",
        ]
    focus = [f"Primary gear goal: {gear_goal}.", f"Requested output shape: {desired_output_type}."]
    if inventory_items:
        focus.append("Inventory items from user input: " + "; ".join(inventory_items[:8]) + ".")
    if priorities:
        focus.append("Priorities: " + "; ".join(priorities) + ".")
    focus.append("Use this as a readiness checklist, not mechanic validation, device diagnosis certainty, repair certainty, flight legality, warranty validation, or data recovery certainty.")
    return focus


def _vehicle_maintenance_plan(vehicle_notes: str, maintenance_concerns: list[str], constraints: list[str], high_risk_context: bool) -> list[str]:
    plan = [
        "List symptoms, dates, mileage or use context, warning lights described by the user, and recent changes.",
        "Separate routine checks from safety-critical concerns.",
        "Use owner manual, qualified mechanic, or official service guidance outside Jarvis for safety-critical or warranty decisions.",
    ]
    if vehicle_notes:
        plan.insert(0, f"Vehicle notes from user input: {vehicle_notes}.")
    if maintenance_concerns:
        plan.append("Maintenance concerns to organize: " + "; ".join(maintenance_concerns) + ".")
    if constraints:
        plan.append("Constraints to respect: " + "; ".join(constraints) + ".")
    if high_risk_context:
        plan.append("Safety-critical vehicle issues need manual inspection by an appropriate professional before driving or repair decisions.")
    return plan


def _device_troubleshooting_plan(device_notes: str, troubleshooting_notes: str, constraints: list[str], high_risk_context: bool) -> list[str]:
    plan = [
        "Write down the device model, visible symptoms, recent changes, and user-observed error wording.",
        "Try only non-destructive manual checks such as confirming power, cable seating, storage space, and known-good accessories.",
        "Avoid resets, updates, downloads, repairs, or data-recovery attempts until important data and warranty constraints are reviewed outside Jarvis.",
    ]
    if device_notes:
        plan.insert(0, f"Device notes from user input: {device_notes}.")
    if troubleshooting_notes:
        plan.append(f"Troubleshooting notes to organize: {troubleshooting_notes}.")
    if constraints:
        plan.append("Device constraints: " + "; ".join(constraints) + ".")
    if high_risk_context:
        plan.append("Electrical, battery, overheating, water damage, or data loss concerns need official, manual, or professional confirmation.")
    return plan


def _drone_scooter_prep(drone_scooter_notes: str, maintenance_concerns: list[str], constraints: list[str], high_risk_context: bool) -> list[str]:
    prep = [
        "Confirm legal, traffic, airspace, and site rules manually before any ride or flight.",
        "Check visible condition, charge level, fasteners, tires or propellers, weather, lighting, and safe operating area manually.",
        "Keep all control, calibration, flight, ride, update, and repair actions outside Jarvis.",
    ]
    if drone_scooter_notes:
        prep.insert(0, f"Drone or scooter notes from user input: {drone_scooter_notes}.")
    if maintenance_concerns:
        prep.append("Concerns to review before operation: " + "; ".join(maintenance_concerns) + ".")
    if constraints:
        prep.append("Constraints to apply: " + "; ".join(constraints) + ".")
    if high_risk_context:
        prep.append("Battery, traffic, crash, airspace, or dangerous hardware concerns require official or professional confirmation before operation.")
    return prep


def _gear_inventory(inventory_items: list[str], priorities: list[str], packing_notes: str) -> list[dict[str, str]]:
    items = inventory_items or ["Gear item to identify manually"]
    inventory: list[dict[str, str]] = []
    for item in items[:10]:
        inventory.append(
            {
                "item": item,
                "statusCheck": "Confirm present, charged or fueled if applicable, clean, labeled, and packed manually.",
                "readinessNote": "; ".join(priorities) if priorities else "Assign priority, condition, and replacement need manually.",
                "boundary": "No files, device state, vehicle system, location, map, account, or external service is checked by Jarvis.",
            }
        )
    if packing_notes:
        inventory.append({"item": "Packing notes", "statusCheck": packing_notes, "readinessNote": "Use as user-provided context only.", "boundary": "No packing list is persisted."})
    return inventory


def _packing_plan(packing_notes: str, inventory_items: list[str], priorities: list[str], constraints: list[str]) -> list[str]:
    plan = [
        "Group gear by must-have, backup, charging or fuel, safety, cleaning, and documentation categories.",
        "Pack fragile, battery, or weather-sensitive items where they are protected and easy to inspect manually.",
        "Use a final manual count before leaving; Jarvis does not create tasks, reminders, or stored records.",
    ]
    if packing_notes:
        plan.insert(0, f"Packing notes from user input: {packing_notes}.")
    if inventory_items:
        plan.append("Items to pack or review: " + "; ".join(inventory_items[:10]) + ".")
    if priorities:
        plan.append("Packing priorities: " + "; ".join(priorities) + ".")
    if constraints:
        plan.append("Packing constraints: " + "; ".join(constraints) + ".")
    return plan


def _setup_checklist(
    gear_goal: str,
    vehicle_notes: str,
    device_notes: str,
    drone_scooter_notes: str,
    inventory_items: list[str],
) -> list[str]:
    checklist = [
        "Confirm the purpose, environment, power needs, safety needs, and failure backup before setup.",
        "Inspect visible condition manually before turning on, mounting, driving, riding, or flying anything.",
        "Keep diagnostics, device control, vehicle control, flight actions, updates, resets, downloads, and repairs outside Jarvis.",
    ]
    if gear_goal:
        checklist.append(f"Setup should support: {gear_goal}.")
    if vehicle_notes:
        checklist.append(f"Vehicle setup context: {vehicle_notes}.")
    if device_notes:
        checklist.append(f"Device setup context: {device_notes}.")
    if drone_scooter_notes:
        checklist.append(f"Drone or scooter setup context: {drone_scooter_notes}.")
    if inventory_items:
        checklist.append("Setup items: " + "; ".join(inventory_items[:8]) + ".")
    return checklist


def _risk_review(
    gear_goal: str,
    vehicle_notes: str,
    device_notes: str,
    drone_scooter_notes: str,
    maintenance_concerns: list[str],
    troubleshooting_notes: str,
    high_risk_context: bool,
) -> list[str]:
    review = [
        "Does any item involve safety, traffic, electrical, battery, flight, warranty, water damage, data loss, or dangerous hardware conditions?",
        "Can the plan stay non-destructive and manual until official or professional guidance is checked?",
        "Are repair, update, reset, diagnostic, purchase, booking, scan, and control actions clearly outside Jarvis?",
    ]
    if gear_goal:
        review.append(f"Goal to review manually: {gear_goal}.")
    if vehicle_notes:
        review.append(f"Vehicle risk notes: {vehicle_notes}.")
    if device_notes:
        review.append(f"Device risk notes: {device_notes}.")
    if drone_scooter_notes:
        review.append(f"Drone or scooter risk notes: {drone_scooter_notes}.")
    if maintenance_concerns:
        review.append("Maintenance concerns: " + "; ".join(maintenance_concerns) + ".")
    if troubleshooting_notes:
        review.append(f"Troubleshooting risk notes: {troubleshooting_notes}.")
    if high_risk_context:
        review.append("High-risk gear conditions need official, manual, or professional confirmation before action.")
    return review


def _next_actions(desired_output_type: str, thin_input: bool, high_risk_context: bool) -> list[str]:
    actions = [
        f"Review the {desired_output_type} response and remove anything that would imply diagnostics, control, repair, update, reset, purchase, booking, flight, scan, or file mutation.",
        "Add missing manual notes for vehicle context, device symptoms, gear inventory, packing needs, constraints, and priorities.",
        "Confirm safety, warranty, legal, airspace, traffic, and repair details outside Jarvis before acting.",
    ]
    if thin_input:
        actions.insert(0, "Add enough manual vehicle, device, gear, maintenance, troubleshooting, packing, and setup context before relying on the checklist.")
    if high_risk_context:
        actions.append("Use official, manual, or qualified professional confirmation for safety-critical, electrical, battery, drone, traffic, warranty, water damage, data loss, or dangerous hardware concerns.")
    return actions


def _open_questions(
    gear_goal: str,
    vehicle_notes: str,
    device_notes: str,
    drone_scooter_notes: str,
    inventory_items: list[str],
    maintenance_concerns: list[str],
    troubleshooting_notes: str,
    packing_notes: str,
    constraints: list[str],
    priorities: list[str],
) -> list[str]:
    questions = []
    if not gear_goal:
        questions.append("What vehicle, device, gear, maintenance, troubleshooting, packing, setup, or readiness goal should this support?")
    if not vehicle_notes:
        questions.append("Are there vehicle notes such as use context, symptoms, maintenance history, or safety concerns?")
    if not device_notes:
        questions.append("Are there device notes such as model, symptoms, battery, storage, accessory, or setup context?")
    if not drone_scooter_notes:
        questions.append("Are there drone or scooter notes such as location rules, battery, tires, propellers, controller, or route context?")
    if not inventory_items:
        questions.append("Which inventory items should be organized or packed?")
    if not maintenance_concerns:
        questions.append("Which maintenance concerns need manual review?")
    if not troubleshooting_notes:
        questions.append("What has already been observed or tried manually?")
    if not packing_notes:
        questions.append("What packing, trip, workspace, or readiness notes matter?")
    if not constraints:
        questions.append("What constraints apply: time, budget, warranty, safety, weather, travel, tools, or data risk?")
    if not priorities:
        questions.append("What matters most: safety, reliability, cost, speed, battery life, portability, comfort, or backup options?")
    return questions[:8]


def _warnings(thin_input: bool, high_risk_context: bool) -> list[str]:
    warnings = [
        "No devices, files, OS settings, apps, accounts, vehicle systems, OBD, Bluetooth, Wi-Fi, GPS/location, drone controller data, maps, warranty portals, repair portals, or external services are accessed.",
        "The response does not run diagnostics, commands, repairs, updates, resets, downloads, purchases, bookings, flight actions, device control, vehicle control, scans, persistence, or file mutations.",
        "No mechanic validation, electrical safety validation, flight legality, warranty validation, live airspace or map verification, device diagnosis certainty, repair certainty, data recovery certainty, production readiness, or certification is claimed.",
    ]
    if thin_input:
        warnings.insert(0, "The vehicle, device, and gear input is thin; results are a planning scaffold rather than a specific readiness review.")
    if high_risk_context:
        warnings.append("Vehicle safety, electrical issues, batteries, drones, traffic rules, airspace rules, warranties, water damage, data loss, and dangerous hardware conditions need official, manual, or professional confirmation.")
    return warnings


def _limitations(thin_input: bool, high_risk_context: bool) -> list[str]:
    limitations = [
        "Based only on user-provided vehicle, device, drone, scooter, gear, maintenance, troubleshooting, packing, constraint, and priority notes.",
        "No device access, vehicle access, drone access, file access, OS settings access, app access, account access, OBD access, Bluetooth access, Wi-Fi scanning, GPS or location access, map access, controller access, portal access, connector use, browsing, downloads, diagnostics, commands, repairs, updates, resets, purchases, bookings, flight actions, persistence, shell execution, or mutation behavior.",
        "No mechanic validation, electrical safety validation, legal validation, warranty validation, airspace validation, live verification, device diagnosis certainty, repair certainty, data recovery certainty, production readiness, security certification, or certification claim.",
    ]
    if thin_input:
        limitations.append("Thin input limits specificity until the user supplies concrete vehicle, device, drone, scooter, inventory, maintenance, troubleshooting, packing, constraint, and priority details.")
    if high_risk_context:
        limitations.append("Vehicle safety, electrical issues, batteries, drones, traffic rules, airspace rules, warranties, water damage, data loss, and dangerous hardware conditions should be confirmed with official, manual, or qualified professional sources.")
    return limitations
