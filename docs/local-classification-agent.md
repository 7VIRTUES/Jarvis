# Local Classification Agent

The Local Classification Agent is implemented as a local-only, response-only classification helper.

## Scope

- Uses only text and items supplied in the request body.
- Returns structured local classification output.
- Supports `general`, `priority`, `risk`, `effort`, `topic`, `routing`, and `safety`.
- Supports `short`, `medium`, and `detailed` detail levels.
- Handles empty or thin input with explicit warnings and limitations.
- Treats supplied labels as user-provided candidate labels only.
- Provides routing hints as advisory local response text only.
- Provides conservative safety notes without claiming compliance, security, legal, medical, financial, or professional validation.
- Does not read files.
- Does not retrieve documents.
- Does not inspect repositories.
- Does not verify sources, citations, or external facts.
- Does not execute commands, tests, or code.
- Does not create tasks, call agents, or mutate workflow state.
- Does not persist classifications or tasks.
- Does not write files or database records.
- Does not download or upload anything.
- Does not call external services.
- Does not use paid APIs.
- Does not use Gmail, calendar, social, connector, OAuth, account access, posting, sending, purchase, or browser automation.

## Endpoint

`POST /agents/classification/local-classify`

Request body:

```json
{
  "title": "Private alpha triage",
  "content": "Dashboard docs are high priority. Safety wording needs manual review.",
  "items": ["Update README", "Review safety language"],
  "classificationType": "priority",
  "labels": ["docs", "safety"],
  "criteria": ["review impact"],
  "constraints": ["no task creation"],
  "detailLevel": "medium"
}
```

The response includes classification focus, classified items, labels used, priority bands, risk bands, effort bands, routing hints, safety notes, assumptions, missing context, warnings, limitations, and explicit safety fields.

## Limitations

This agent only classifies user-provided text and items in the response. It does not read files, retrieve documents, verify sources, verify citations, inspect repositories, run tests, create tasks, call agents, persist classifications, certify compliance, provide professional validation, download data, upload data, or use external services.
