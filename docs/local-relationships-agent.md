# Local Relationship / Family Agent

The Local Relationship / Family Agent is a local-only, manual-input, response-only planning helper for relationship and family communication notes.

Endpoint: `POST /agents/relationships/local-plan`

Mode: `response_only_user_provided_relationship_planning`

## Request Fields

- `profileName` optional string
- `relationshipGoal` required string
- `relationshipType` optional string
- `peopleContext` optional string
- `situationNotes` optional string
- `communicationGoals` optional list of strings
- `concerns` optional list of strings
- `boundaries` optional list of strings
- `desiredTone` optional string
- `constraints` optional list of strings
- `desiredOutputType` optional string

Supported output types: `relationship_brief`, `conversation_plan`, `boundary_plan`, `conflict_prep`, `apology_draft`, `check_in_plan`, `gift_occasion_plan`, and `relationship_maintenance`.

Unsupported output types fall back to `relationship_brief`.

## Response Shape

The response includes relationship focus, situation summary, communication plan, conversation scripts, boundary plan, conflict prep, apology drafts, check-in plan, gift or occasion plan, relationship maintenance notes, next actions, open questions, warnings, limitations, and safety flags.

All response content is based only on the request body.

## Boundaries

- No contacts, messages, DMs, email, calendar, social platforms, location, photos, files, accounts, connectors, paid APIs, browsing, or external services.
- No sending, scheduling, posting, scraping, tracking, private-information identification, persistence, task creation, database writes, shell execution, file mutation, or account mutation.
- No manipulation, coercion, deception, harassment, stalking, doxxing, impersonation, jealousy-control, evasion, therapy claims, diagnosis, treatment plans, relationship outcome certainty, conflict resolution guarantees, legal validation, safety validation, emotional certainty, production readiness, or certification claims.
- Abuse, violence, stalking, coercive control, self-harm, severe mental-health distress, legal danger, and immediate safety concerns should be handled with appropriate human, professional, legal, safety, or emergency support.

## Related Docs

- [Local Response Agents Index](local-response-agents-index.md)
- [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md)
- [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)

## Manual Evidence Aids

Manual evidence aids can record the endpoint, local-only response shape, safety flags, warnings, and limitations for later review. They do not prove validation or certification.
