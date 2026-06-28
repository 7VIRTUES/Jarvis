# Local Housing / Move / Travel Agent

The Local Housing / Move / Travel Agent turns user-provided housing, move, commute, utility setup, budget, transportation, and travel notes into structured local planning suggestions.

It is manual-input only, local-only, and response-only. It does not browse listings, use maps, check locations, contact booking platforms, access school housing portals, send messages, create calendar items, read contacts, access accounts, sign leases, submit applications, reserve rooms, buy tickets, make payments, read files, write files, persist tasks, or mutate records.

## Endpoint

`POST /agents/housing-move-travel/local-plan`

## Example Request

```json
{
  "planName": "Boston Move Plan",
  "destination": "Boston campus area",
  "housingGoal": "Compare user-provided housing options and prepare a manual move checklist.",
  "timeline": "Move before the fall term starts",
  "budgetNotes": "Estimate rent, deposit, utilities, moving supplies, travel, and emergency buffer manually.",
  "housingOptions": ["Shared apartment near transit", "Student housing option from user notes"],
  "moveItems": ["Laptop and chargers", "Clothes", "Bedding", "Important documents"],
  "transportationNotes": "Compare driving with shipped boxes against flying with checked bags.",
  "commuteNotes": "Review walking, transit, and backup commute assumptions from user notes.",
  "utilitySetupNotes": "Internet, mail forwarding, renter insurance, and move-in inspection need manual confirmation.",
  "constraints": ["Manual planning only", "No live listings or map checks"],
  "priorities": ["Protect budget buffer", "Keep commute reliable", "Avoid rushed move-in"],
  "desiredOutputType": "move_brief"
}
```

## Output Types

- `move_brief`
- `housing_comparison`
- `move_plan`
- `packing_plan`
- `drive_vs_fly_plan`
- `commute_review`
- `setup_checklist`
- `travel_prep_plan`

Unsupported output types fall back to `move_brief`.

## Safety Boundaries

- Uses only the request body supplied by the local user.
- No apartment sites, live listings, maps, location access, booking platforms, school portals, email, calendar, contacts, bank accounts, payment accounts, lease systems, files, connectors, paid APIs, or external services.
- No travel booking, room reservation, lease signing, application submission, landlord messaging, tour scheduling, calendar event creation, payment, ticket purchase, task persistence, file mutation, or other account mutation.
- No claims of live availability, current prices, neighborhood safety validation, legal lease review, housing approval, travel booking, commute-time certainty, insurance validation, financial validation, production readiness, or certification.
- Lease, deposit, legal, safety, insurance, financial, and official school housing questions should be confirmed with official sources or qualified professionals.

## Response Shape

Responses include `agentId`, `status`, `mode`, `planName`, `destination`, `housingGoal`, `desiredOutputType`, `moveFocus`, `housingSummary`, `housingComparison`, `movePlan`, `packingPlan`, `driveVsFlyPlan`, `commuteReview`, `setupChecklist`, `travelPrepPlan`, `budgetNotes`, `nextActions`, `openQuestions`, `warnings`, `limitations`, and `safety`.

## Related Local Response-Agent Docs

- [Local Response Agents Index](local-response-agents-index.md)
- [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md)
- [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)

The smoke runbook and evidence template are manual evidence aids. They do not prove validation or certification.
