# Local Planning Agent

The Local Planning Agent is implemented as a local-only, response-only planning helper.

## Scope

- Uses only planning inputs provided in the request.
- Returns a structured plan response.
- Supports `project_plan`, `study_plan`, `checklist`, and `weekly_plan`.
- Handles thin context with explicit warnings and limitations.
- Does not create persistent tasks.
- Does not create reminders.
- Does not use calendar or email.
- Does not read files.
- Does not write files.
- Does not write database records.
- Does not execute shell commands.
- Does not upload anything.
- Does not call external services.
- Does not use paid APIs.
- Does not use connectors, OAuth, account access, browser automation, posting, or sending.

## Endpoint

`POST /agents/planning/local-plan`

Request body:

```json
{
  "goal": "Prepare a local alpha checklist",
  "contextNotes": "The work must stay local and reviewable.",
  "constraints": ["No external services"],
  "resources": ["Existing README and docs"],
  "blockers": ["Need final review"],
  "timeframe": "This week",
  "desiredOutputType": "project_plan"
}
```

The response includes planning focus, assumptions, phases, checklist, next actions, risks, blockers, review questions, limitations, warnings, and explicit safety fields.

## Limitations

This agent only drafts a plan in the response. It is not a scheduler, task system, calendar assistant, email agent, project-management integration, or persistent workflow engine.

## Related Docs

- [Local Response Agents Index](local-response-agents-index.md)
- [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md)
- [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)

These read-only docs and manual evidence aids do not prove validation or certification.
