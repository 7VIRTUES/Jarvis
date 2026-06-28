# Local Emergency / Preparedness Agent

The Local Emergency / Preparedness Agent turns user-provided preparedness, household, supply, pet, vehicle, medical/accessibility, budget, communication, and constraint notes into structured local preparedness guidance.

It is local-only, response-only, and manual-input-only.

## Purpose

- Help organize household preparedness, emergency checklists, go-bags, severe weather prep, power outage plans, car emergency kits, communication plans, evacuation thinking, and post-event organization.
- Keep outputs based only on the request body.

## Scope

- Does not browse, call paid APIs, use connectors, access accounts, read files, write files, write database records, create tasks, create reminders, call emergency services, send alerts, contact family, book hotels, buy supplies, unlock doors, control devices, submit claims, or mutate local state.
- Does not access emergency services, police/fire/EMS, weather services, maps, GPS/location, smart devices, alarms, cameras, contacts, files, accounts, payment systems, or external services.
- Does not create persistent preparedness, household, emergency, insurance, contact, travel, purchase, or medical records.

## Endpoint

`POST /agents/emergency-preparedness/local-plan`

## Request Body Example

```json
{
  "request": "Make a basic car emergency kit checklist for winter driving.",
  "outputType": "car_emergency_kit",
  "scenarioType": "winter driving preparedness",
  "householdSize": "1 driver",
  "pets": [],
  "locationContextIfUserProvided": "Cold-weather driving context from user notes.",
  "currentSupplies": ["Blanket", "Phone charger", "Flashlight"],
  "vehicleOrTravelContext": "Commutes by car during winter.",
  "medicalOrAccessibilityNeeds": [],
  "budgetLevel": "low",
  "budgetNotes": "Use current supplies first.",
  "timeHorizon": "Prepare before the next cold-weather trip.",
  "communicationContactsSummary": "User will keep contact list manually.",
  "constraintsOrNotes": "Preparedness planning only; no emergency calls or purchases."
}
```

## Supported Output Types

- `go_bag_checklist`
- `emergency_plan`
- `severe_weather_plan`
- `power_outage_plan`
- `car_emergency_kit`
- `evacuation_prep`
- `communication_plan`
- `supply_gap_analysis`
- `pet_preparedness_plan`
- `post_event_checklist`
- `comparison`
- `checklist`
- `summary`

## Safety Boundaries

- Not an emergency-service, police/fire/EMS, weather, map, GPS/location, smart-device, alarm, camera, contact, file, account, payment, or external-service connector.
- Does not call 911, send alerts, contact family, book hotels, buy supplies, unlock doors, control devices, submit claims, persist records, or mutate files.
- Does not claim live hazard detection, official emergency guidance, evacuation-order awareness, medical triage certainty, survival guarantee, or certification claims.
- For immediate danger, contact local emergency services or leave the area if safe to do so.
- Medical emergencies, fire, gas leak, active violence, carbon monoxide symptoms, flooding with electrical risk, or severe injury require immediate professional or emergency-service guidance.

## Related Docs

- [Local Response Agents Index](local-response-agents-index.md)
- [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md)
- [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)

These linked smoke and evidence docs are read-only docs/manual evidence aids and do not prove validation or certification.
