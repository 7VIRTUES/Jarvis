# Local Review Agent

The Local Review Agent is implemented as a local-only, response-only review helper.

## Scope

- Uses only review content provided in the request.
- Returns a structured review response.
- Supports `general`, `clarity`, `risk`, `completeness`, `safety`, and `actionability`.
- Supports `gentle`, `balanced`, and `strict` severity.
- Handles thin content with explicit warnings and limitations.
- Does not inspect repositories.
- Does not verify external facts.
- Does not validate sources or citations.
- Does not execute tests or code.
- Does not persist reviews.
- Does not create tasks.
- Does not read files.
- Does not write files.
- Does not write database records.
- Does not execute shell commands.
- Does not upload anything.
- Does not call external services.
- Does not use paid APIs.
- Does not use Gmail, calendar, social, connector, OAuth, account access, posting, sending, or browser automation.

## Endpoint

`POST /agents/review/local-review`

Request body:

```json
{
  "subject": "Private alpha checklist",
  "content": "The checklist should stay local-only. It should explain review scope and name unresolved risks.",
  "reviewType": "risk",
  "audience": "Private alpha reviewers",
  "criteria": ["Clear scope", "Explicit safety boundaries"],
  "constraints": ["No external verification claims"],
  "severity": "balanced"
}
```

The response includes review focus, strengths, issues, missing information, risk flags, improvement suggestions, action items, review questions, warnings, limitations, and explicit safety fields.

## Limitations

This agent only reviews user-provided content in the response. It does not verify facts, inspect source code, validate citations, run tests, read local files, persist review records, or use external services.
