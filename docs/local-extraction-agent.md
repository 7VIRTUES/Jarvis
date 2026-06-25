# Local Extraction Agent

The Local Extraction Agent is implemented as a local-only, response-only structured extraction helper.

## Scope

- Uses only text supplied in the request body.
- Returns structured extraction output.
- Supports `general`, `action_items`, `requirements`, `risks`, `entities`, `questions`, and `timeline`.
- Supports `short`, `medium`, and `detailed` detail levels.
- Handles empty or thin content with explicit warnings and limitations.
- Preserves requested user-provided `mustCapture` items when possible.
- Avoids requested `mustIgnore` terms in extracted output except for listing them under `ignoredItems`.
- Does not read files.
- Does not retrieve documents.
- Does not inspect repositories.
- Does not verify sources, citations, or external facts.
- Does not execute commands, tests, or code.
- Does not create tasks from action items.
- Does not persist extracted items or tasks.
- Does not write files or database records.
- Does not download or upload anything.
- Does not call external services.
- Does not use paid APIs.
- Does not use Gmail, calendar, social, connector, OAuth, account access, posting, sending, purchase, or browser automation.

## Endpoint

`POST /agents/extraction/local-extract`

Request body:

```json
{
  "title": "Private alpha notes",
  "content": "The dashboard must show local-only agents. Next step: update docs. Risk: overclaiming validation.",
  "extractionType": "general",
  "focusAreas": ["requirements", "risks"],
  "mustCapture": ["local-only agents"],
  "mustIgnore": ["certified"],
  "detailLevel": "medium"
}
```

The response includes extraction focus, extracted items, action items, requirements, risks, entities, questions, timeline items, captured items, ignored items, missing context, warnings, limitations, and explicit safety fields.

## Limitations

This agent only extracts from user-provided text in the response. It does not read files, retrieve documents, verify sources, verify citations, inspect repositories, run tests, create tasks, persist extracted records, download data, upload data, or use external services.
