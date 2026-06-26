# Local Summarization Agent

The Local Summarization Agent is implemented as a local-only, response-only summarization helper.

## Scope

- Uses only text supplied in the request body.
- Returns a structured local summary response.
- Supports `general`, `bullets`, `executive`, `action_items`, `study_notes`, and `risks`.
- Supports `short`, `medium`, and `detailed` detail levels.
- Handles empty or thin content with explicit warnings and limitations.
- Preserves requested user-provided items when possible.
- Avoids requested user-provided terms when they appear in generated summary text.
- Does not read files.
- Does not retrieve documents.
- Does not inspect repositories.
- Does not verify sources, citations, or external facts.
- Does not generate or verify citations.
- Does not execute commands, tests, or code.
- Does not persist summaries or tasks.
- Does not write files or database records.
- Does not download or upload anything.
- Does not call external services.
- Does not use paid APIs.
- Does not use Gmail, calendar, social, connector, OAuth, account access, posting, sending, purchase, or browser automation.

## Endpoint

`POST /agents/summarization/local-summary`

Request body:

```json
{
  "title": "Private alpha notes",
  "content": "The private alpha notes explain local-only scope. Reviewers need a concise summary and action items.",
  "summaryType": "general",
  "audience": "Reviewers",
  "detailLevel": "medium",
  "focusAreas": ["scope", "next steps"],
  "mustPreserve": ["local-only scope"],
  "mustAvoid": ["certified"]
}
```

The response includes summary text, key points, action items, risks or caveats, preserved items, avoided items, missing context, warnings, limitations, and explicit safety fields.

## Limitations

This agent only summarizes user-provided text in the response. It does not read files, retrieve documents, verify sources, verify citations, inspect repositories, run tests, persist summaries, download data, upload data, or use external services.

## Related Docs

- [Local Response Agents Index](local-response-agents-index.md)
- [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md)
- [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)

These read-only docs and manual evidence aids do not prove validation or certification.
