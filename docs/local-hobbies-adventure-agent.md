# Local Hobbies / Adventure Agent

Back to the [Local Response Agents Index](local-response-agents-index.md).

Manual examples live in the [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md). Manual evidence aids live in the [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md); they do not prove validation or certification.

## Boundary

- Manual-input-only.
- Local-only.
- Response-only.
- Outputs are based only on user-provided hobby, adventure, gear, budget, location-context, timing, group, transport, risk, safety, and accessibility inputs.
- Does not access maps, GPS/location, weather services, park systems, drone apps, fishing/license systems, booking apps, stores, payments, accounts, files, camera, sensors, connectors, or external services.
- Does not book, buy, apply for permits or licenses, verify drone airspace, verify legal access, contact anyone, persist, mutate, or provide live safety or legal verification.
- Drone-related outputs remind the user to verify current FAA and local rules, airspace, property rules, privacy expectations, and safe conditions separately.
- Outdoor activity outputs remind the user to check official local conditions, rules, closures, and safety guidance separately.
- Does not support illegal trespass, evasion, unsafe stunts, weapon use, poaching, vandalism, dangerous survival tactics, or certification claims.

## Endpoint

`POST /agents/hobbies-adventure/local-plan`

## Supported Output Types

- `hobby_plan`
- `adventure_plan`
- `beginner_progression`
- `gear_checklist`
- `safety_checklist`
- `low_cost_activity_plan`
- `weekend_plan`
- `skill_practice_plan`
- `packing_list`
- `comparison`
- `checklist`
- `summary`
