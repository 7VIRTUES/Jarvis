# Local Decision Agent

The Local Decision Agent is implemented as a local-only, response-only decision-support helper.

## Scope

- Uses only decision inputs provided in the request.
- Returns a structured comparison response.
- Supports `balanced`, `safest`, `fastest`, `cheapest`, and `highest_upside`.
- Handles thin context with explicit warnings and limitations.
- Handles fewer than two usable options as an honest limited comparison.
- Does not persist decisions.
- Does not inspect repositories.
- Does not verify external facts.
- Does not validate sources or citations.
- Does not provide financial, legal, medical, academic, or other professional advice.
- Does not execute tests or code.
- Does not create tasks.
- Does not read files.
- Does not write files.
- Does not write database records.
- Does not execute shell commands.
- Does not upload anything.
- Does not call external services.
- Does not use paid APIs.
- Does not use Gmail, calendar, social, connector, OAuth, account access, posting, sending, purchase, or browser automation.

## Endpoint

`POST /agents/decision/local-decision`

Request body:

```json
{
  "decision": "Choose a private alpha support path",
  "options": ["Short manual checklist", "Long guided worksheet"],
  "criteria": ["Clear for first-time testers", "Easy to review"],
  "constraints": ["No external services", "No account linking"],
  "priorities": ["Fast to use", "Low support burden"],
  "contextNotes": "The user wants a local-only private alpha flow with clear boundaries.",
  "decisionStyle": "balanced"
}
```

The response includes decision focus, comparison matrix, tradeoffs, suggested direction, confidence, assumptions, risks, missing information, next actions, review questions, warnings, limitations, and explicit safety fields.

## Limitations

This agent only compares user-provided options in the response. It does not verify facts, inspect source code, validate citations, run tests, read local files, persist decision records, purchase anything, send or post anything, or use external services.

For legal, medical, financial, academic, safety, or other high-stakes decisions, treat the output as local decision support only and obtain appropriate human or qualified professional verification before acting.
