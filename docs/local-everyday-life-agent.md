# Local Everyday Life Agent

The Local Everyday Life Agent turns user-provided routine, chore, errand, household, personal admin, packing, preparation, time-blocking, priority, energy, budget, and resource notes into structured local planning suggestions.

It is local-only, response-only, and manual-input-only.

## Purpose

- Help organize everyday-life situations using only the request body.
- Return manual planning suggestions for daily plans, weekly plans, routines, errands, household organization, preparation checklists, and simple priority reviews.
- Keep plans and checklists non-persistent and non-executing.

## Scope

- Does not access Gmail, Calendar, contacts, maps, location, finance, smart-home, health-app, external account, connector, browser, paid API, file, database, shell, or cloud data.
- Does not create tasks, reminders, calendar events, emails, files, database rows, purchases, posts, messages, bookings, deliveries, orders, or route plans.
- Does not claim validation, automation, completion, scheduling, delivery, execution, professional advice, or certification.

## Endpoint

`POST /agents/everyday-life/local-plan`

## Request Body Example

```json
{
  "lifeArea": "Household reset",
  "situation": "Prepare for a busy week with chores, errands, and personal admin.",
  "goals": ["Reduce clutter", "Batch errands", "Set up simple evening routines"],
  "constraints": ["Keep the plan manual", "Avoid adding new apps or accounts"],
  "scheduleNotes": "Two short evening blocks and one weekend planning block.",
  "householdNotes": "Shared spaces need a quick reset before the week starts.",
  "errands": ["Return library books", "Pick up basic groceries"],
  "peopleInvolved": ["Household members"],
  "resources": ["Existing checklist", "Reusable bags"],
  "energyNotes": "Energy is lower after work, so keep weekday steps small.",
  "budgetNotes": "Use items already on hand where possible.",
  "desiredOutputType": "life_brief"
}
```

## Supported Output Types

- `life_brief`
- `daily_plan`
- `weekly_plan`
- `routine_plan`
- `errand_plan`
- `household_plan`
- `preparation_checklist`
- `priority_review`

## Safety Boundaries

- Manual-input only.
- Local-only.
- Response-only.
- No calendar, task, email, contact, map, location, finance, smart-home, health-app, account, connector, browser, paid API, file, database, shell, purchase, post, or message behavior.
- No persistence.
- No execution.
- No professional validation.
- Output is based only on user-provided input.

## Limitations

- Plans and checklists are suggestions only.
- Money, legal, medical, safety, or emergency-related situations require appropriate human, professional, emergency, or local authority help.
- The agent does not prove completion, scheduling, delivery, execution, validation, certification, or readiness.

## Related Docs

- [Local Response Agents Index](local-response-agents-index.md)
- [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md)
- [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)

These linked smoke and evidence docs are read-only docs/manual evidence aids and do not prove validation or certification.
