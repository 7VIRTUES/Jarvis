# Local Business Agent

The Local Business Agent turns user-provided business planning notes into a structured local brief. It is response-only and manual-input-only.

It does not validate markets, demand, revenue, profitability, compliance, taxes, accounting, investments, legal outcomes, or business readiness.

## Scope

- Uses only fields in the request body.
- Returns local planning text and structured business-planning sections.
- Does not browse, call paid APIs, use connectors, access accounts, process payments, post publicly, send email, access CRM data, create tasks, create calendar entries, read files, write files, write database records, execute commands, or mutate local state.
- Does not provide legal, tax, financial, accounting, investment, compliance, or professional-advice validation.

## Endpoint

`POST /agents/business/local-brief`

## Request Body Example

```json
{
  "businessName": "Neighborhood Meal Prep Studio",
  "businessIdea": "Offer small-batch weekly meal prep kits for busy local households.",
  "targetCustomer": "Busy families who want simple weeknight meals",
  "problem": "Weeknight cooking feels rushed and planning takes too much time.",
  "offer": "Pre-portioned local meal prep kits with simple instructions.",
  "pricingNotes": "Pilot a simple per-kit price and review customer feedback manually.",
  "operationsNotes": "Start with a small menu, local pickup window, and manual order tracking.",
  "marketingNotes": "Explain convenience, freshness, and predictable weekly planning.",
  "constraints": ["Manual local pilot only", "No paid ads until the offer is clearer"],
  "resources": ["Home kitchen planning notes", "Local ingredient supplier list"],
  "risks": ["Demand may be uncertain", "Operational capacity may be limited"],
  "goals": ["Validate interest manually", "Prepare a small launch checklist"],
  "desiredOutputType": "business_brief"
}
```

## Supported Output Types

- `business_brief`
- `lean_canvas`
- `swot`
- `offer_plan`
- `marketing_plan`
- `operations_plan`
- `risk_review`
- `launch_checklist`

## Response Shape

The response includes:

- `agentId`
- `status`
- `mode`
- `businessName`
- `businessIdea`
- `desiredOutputType`
- `businessFocus`
- `customerAssumptions`
- `problemSummary`
- `offerSummary`
- `valueProposition`
- `revenueNotes`
- `operationsNotes`
- `marketingAngles`
- `swot`
- `leanCanvas`
- `launchChecklist`
- `risks`
- `nextActions`
- `openQuestions`
- `warnings`
- `limitations`
- `safety`

## Safety Boundaries

The safety fields indicate `localOnly`, `responseOnly`, and `manualInputOnly` as true.

The safety fields indicate these are false: external services, paid APIs, web browsing, connector execution, OAuth, account access, finance connector access, payment actions, purchases, email sending, public posting, CRM access, file reads, file writes, database writes, task persistence, shell execution, mutation, professional-advice validation, and compliance certification.

## Limitations

- The output is based only on user-provided business planning inputs.
- It does not prove market validation, demand validation, revenue validation, profitability, legal readiness, tax correctness, accounting correctness, investment suitability, compliance readiness, private-alpha certification, production readiness, or security certification.
- Human review is required before relying on it for legal, tax, financial, accounting, compliance, investment, or other high-stakes business decisions.

## Related Docs

- [Local Response Agents Index](local-response-agents-index.md)
- [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md)
- [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)

These linked smoke and evidence docs are read-only docs/manual evidence aids and do not prove validation or certification.
