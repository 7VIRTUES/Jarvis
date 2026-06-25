# Local Drafting Agent

The Local Drafting Agent is implemented as a local-only, response-only drafting helper.

## Scope

- Uses only drafting inputs provided in the request.
- Returns a structured draft response.
- Supports `message`, `email_draft`, `document_section`, `checklist`, and `announcement`.
- Handles thin notes with explicit warnings and limitations.
- Reflects `mustInclude` points when possible.
- Avoids intentionally inserting `mustAvoid` items into generated draft text.
- Does not send email.
- Does not create Gmail drafts.
- Does not post publicly.
- Does not save drafts.
- Does not read files.
- Does not write files.
- Does not write database records.
- Does not create tasks.
- Does not execute shell commands.
- Does not upload anything.
- Does not call external services.
- Does not use paid APIs.
- Does not use Gmail, calendar, social, connector, OAuth, account access, or browser automation.

## Endpoint

`POST /agents/drafting/local-draft`

Request body:

```json
{
  "purpose": "Invite reviewers to a local alpha check",
  "audience": "Private alpha reviewers",
  "notes": "Keep it short. Explain that the review is local-only.",
  "tone": "clear",
  "format": "message",
  "constraints": ["No hype"],
  "mustInclude": ["Local-only review"],
  "mustAvoid": ["guaranteed"]
}
```

The response includes draft title, draft text, included points, avoided items, revision notes, warnings, limitations, and explicit safety fields.

## Limitations

This agent only drafts text in the response. Email-style output is draft text only; it does not use Gmail, save a draft, send email, access accounts, or call connectors.
