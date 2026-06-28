# Local Vehicle / Devices / Gear Agent

The Local Vehicle / Devices / Gear Agent turns user-provided vehicle, device, drone, scooter, computer, phone, gear, maintenance, troubleshooting, packing, setup, inventory, and readiness notes into local planning and checklist output.

It is manual-input only, local-only, and response-only.

## Endpoint

`POST /agents/vehicle-devices-gear/local-plan`

## Request Fields

- `profileName`: optional string
- `gearGoal`: required string
- `vehicleNotes`: optional string
- `deviceNotes`: optional string
- `droneScooterNotes`: optional string
- `inventoryItems`: optional list of strings
- `maintenanceConcerns`: optional list of strings
- `troubleshootingNotes`: optional string
- `packingNotes`: optional string
- `constraints`: optional list of strings
- `priorities`: optional list of strings
- `desiredOutputType`: optional string, defaults to `gear_brief`

Supported output types:

- `gear_brief`
- `vehicle_maintenance_plan`
- `device_troubleshooting_plan`
- `drone_scooter_prep`
- `gear_inventory`
- `packing_plan`
- `setup_checklist`
- `risk_review`

Unsupported output types are normalized to `gear_brief`.

## Example Request

```json
{
  "profileName": "Local Gear Profile",
  "gearGoal": "Prepare a manual readiness checklist for a campus project day with laptop, scooter, and drone gear.",
  "vehicleNotes": "Car may be used for transport; confirm tire pressure and fuel manually before leaving.",
  "deviceNotes": "Laptop, phone, chargers, portable battery, and camera need a pre-trip check.",
  "droneScooterNotes": "Drone and scooter should be reviewed only after checking local rules and battery condition manually.",
  "inventoryItems": ["Laptop", "Phone", "Chargers", "Portable battery", "Camera", "Drone case", "Scooter helmet"],
  "maintenanceConcerns": ["Battery condition", "Tire pressure", "Loose accessories"],
  "troubleshootingNotes": "Phone battery has drained quickly recently; avoid destructive troubleshooting.",
  "packingNotes": "Pack light but include backup charging and safety gear.",
  "constraints": ["Manual planning only", "No diagnostics, device control, vehicle control, maps, or flight actions"],
  "priorities": ["Safety", "Battery readiness", "Reliable project capture"],
  "desiredOutputType": "gear_brief"
}
```

## Response Shape

The response includes:

- `agentId`
- `status`
- `mode`
- `profileName`
- `gearGoal`
- `desiredOutputType`
- `gearFocus`
- `vehicleMaintenancePlan`
- `deviceTroubleshootingPlan`
- `droneScooterPrep`
- `gearInventory`
- `packingPlan`
- `setupChecklist`
- `riskReview`
- `nextActions`
- `openQuestions`
- `warnings`
- `limitations`
- `safety`

## Safety Boundaries

The agent uses only the request body supplied by the local user. It does not access devices, vehicles, drones, files, OS settings, apps, accounts, OBD, Bluetooth, Wi-Fi, GPS/location, maps, drone controller data, warranty portals, repair portals, connectors, paid APIs, or external services.

The agent does not run diagnostics, commands, repairs, updates, resets, downloads, purchases, bookings, flight actions, device control, vehicle control, scans, persistence, file mutations, shell execution, or database writes.

It does not claim mechanic validation, electrical safety validation, legal validation, flight legality, warranty validation, airspace validation, live airspace or map verification, device diagnosis certainty, repair certainty, data recovery certainty, production readiness, security certification, or certification claims.

For vehicle safety, electrical issues, batteries, drones, traffic rules, airspace rules, warranties, water damage, data loss, or dangerous hardware conditions, the response recommends official, manual, or qualified professional confirmation.

## Related Manual Evidence Aids

- [Local Response Agents Index](local-response-agents-index.md)
- [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md)
- [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)

These docs are manual review aids only. They do not prove validation or certification, and they do not claim tests, CI, clean Windows VM validation, private-alpha certification, production readiness, or security certification.
