# Local Transformation Agent

The Local Transformation Agent is implemented as a local-only, response-only transformation helper.

## Scope

- Uses only text and items supplied in the request body.
- Returns transformed response text and structured response fields.
- Supports `outline`, `checklist`, `table`, `sop_steps`, `flashcards`, `json_style`, `csv_style`, and `cleaned_notes`.
- Supports `short`, `medium`, and `detailed` detail levels.
- Handles empty or thin input with explicit warnings and limitations.
- Preserves requested user-provided `mustPreserve` items when possible.
- Avoids requested `mustAvoid` terms in transformed output except for listing them under `avoidedItems`.
- Returns `json_style` and `csv_style` as response text only.
- Returns `table` rows as structured response data only.
- Returns `flashcards` as local response data only.
- Does not read files.
- Does not write files.
- Does not create documents, spreadsheets, decks, exports, or downloadable artifacts.
- Does not retrieve documents.
- Does not inspect repositories.
- Does not verify sources, citations, or external facts.
- Does not execute commands, tests, or code.
- Does not create tasks or mutate workflow state.
- Does not persist transformations or tasks.
- Does not write database records.
- Does not download or upload anything.
- Does not call external services.
- Does not use paid APIs.
- Does not use Gmail, calendar, social, connector, OAuth, account access, posting, sending, purchase, or browser automation.

## Endpoint

`POST /agents/transformation/local-transform`

Request body:

```json
{
  "title": "Private alpha notes",
  "content": "Review docs. Confirm local-only safety wording. Prepare manual checklist.",
  "items": ["Review docs", "Confirm local-only safety wording"],
  "targetFormat": "checklist",
  "audience": "Reviewers",
  "constraints": ["No file export"],
  "mustPreserve": ["local-only safety wording"],
  "mustAvoid": ["certified"],
  "detailLevel": "medium"
}
```

The response includes transformed text, outline, checklist, table rows, SOP steps, flashcards, JSON-style text, CSV-style text, cleaned notes, preserved items, avoided items, missing context, warnings, limitations, and explicit safety fields.

## Limitations

This agent only transforms user-provided text and items in the response. It does not read files, write files, create documents, create spreadsheets, create decks, export files, retrieve documents, inspect repositories, run tests, persist transformations, create tasks, certify compliance, provide professional validation, download data, upload data, or use external services.
