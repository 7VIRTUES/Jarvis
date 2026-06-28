# Local Life Direction / Values Agent

The Local Life Direction / Values Agent turns user-provided life direction, values, long-term goals, identity, standards, priorities, discipline, tradeoffs, season planning, strengths, growth areas, and reflection notes into local planning output.

It is manual-input only, local-only, and response-only.

## Endpoint

`POST /agents/life-direction/local-plan`

## Request Fields

- `profileName`: optional string
- `lifeQuestion`: required string
- `currentSeason`: optional string
- `values`: optional list of strings
- `longTermGoals`: optional list of strings
- `currentPriorities`: optional list of strings
- `tensionsOrTradeoffs`: optional list of strings
- `constraints`: optional list of strings
- `areasToImprove`: optional list of strings
- `strengths`: optional list of strings
- `nonNegotiables`: optional list of strings
- `reflectionNotes`: optional string
- `desiredOutputType`: optional string, defaults to `life_direction_brief`

Supported output types:

- `life_direction_brief`
- `values_review`
- `priority_plan`
- `five_year_direction`
- `season_plan`
- `tradeoff_review`
- `identity_standards`
- `discipline_plan`

Unsupported output types are normalized to `life_direction_brief`.

## Example Request

```json
{
  "profileName": "Local Direction Profile",
  "lifeQuestion": "Clarify the next season across school, career, money, health, projects, relationships, and personal growth.",
  "currentSeason": "Building technical skill, preparing career options, and trying to become more disciplined without burning out.",
  "values": ["Competence", "Integrity", "Health", "Family", "Creative independence"],
  "longTermGoals": ["Become a strong technical builder", "Create durable projects", "Build stable finances"],
  "currentPriorities": ["School progress", "Portfolio projects", "Health habits"],
  "tensionsOrTradeoffs": ["Ambition versus rest", "Many project ideas versus finishing a few"],
  "constraints": ["Manual reflection only", "No calendar, task, account, health, finance, or school portal access"],
  "areasToImprove": ["Consistency", "Focus", "Follow-through"],
  "strengths": ["Curiosity", "Systems thinking", "Persistence"],
  "nonNegotiables": ["No fake claims", "Protect health", "Keep commitments realistic"],
  "reflectionNotes": "User wants a grounded season plan and standards, not therapy or guaranteed outcomes.",
  "desiredOutputType": "life_direction_brief"
}
```

## Response Shape

The response includes:

- `agentId`
- `status`
- `mode`
- `profileName`
- `lifeQuestion`
- `desiredOutputType`
- `directionFocus`
- `valuesSummary`
- `longTermDirection`
- `currentSeasonSummary`
- `priorityPlan`
- `fiveYearDirection`
- `seasonPlan`
- `tradeoffReview`
- `identityStandards`
- `disciplinePlan`
- `nextActions`
- `openQuestions`
- `warnings`
- `limitations`
- `safety`

## Safety Boundaries

The agent uses only the request body supplied by the local user. It does not access files, journals, calendars, tasks, accounts, messages, health data, finance data, school portals, contacts, connectors, paid APIs, or external services.

The agent does not persist goals, create tasks, create reminders, schedule events, message anyone, post publicly, purchase anything, mutate files, write to databases, browse, or execute shell commands.

It does not claim therapy, mental-health diagnosis, treatment, crisis support, legal advice, financial advice, medical advice, spiritual authority, guaranteed success, life-outcome certainty, production readiness, security certification, or certification claims.

For crisis, self-harm, abuse, violence, severe mental-health distress, legal, medical, financial, immigration, or other high-stakes situations, the response recommends appropriate human, professional, official, or emergency help.

## Related Manual Evidence Aids

- [Local Response Agents Index](local-response-agents-index.md)
- [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md)
- [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)

These docs are manual review aids only. They do not prove validation or certification, and they do not claim tests, CI, clean Windows VM validation, private-alpha certification, production readiness, or security certification.
