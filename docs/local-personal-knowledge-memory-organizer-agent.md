# Local Personal Knowledge / Memory Organizer Agent

Back to the [Local Response Agents Index](local-response-agents-index.md).

Manual examples live in the [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md). Manual evidence aids live in the [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md); they do not prove validation or certification.

## Boundary

- Manual-input-only.
- Local-only.
- Response-only.
- Outputs are based only on user-provided knowledge-area, source-note, category, project, review, priority, retention, decision, and memory-context text.
- Does not access files, notes apps, cloud drives, browser history, email, calendar, contacts, memory stores, databases, accounts, payments, connectors, or external services.
- Does not create, edit, delete, move, persist, sync, export, mutate, or store files, notes, records, databases, or memories.
- Does not claim file search or memory outside provided input.
- Does not infer sensitive facts beyond text supplied by the user.
- Redact secrets, credentials, private IDs, medical details, legal details, financial account details, and protected personal data before storing notes anywhere.

## Endpoint

`POST /agents/personal-knowledge-memory-organizer/local-plan`

## Supported Output Types

- `knowledge_map`
- `note_structure`
- `memory_index`
- `tagging_plan`
- `review_plan`
- `decision_record`
- `project_context_summary`
- `personal_wiki_outline`
- `learning_log_structure`
- `retrieval_checklist`
- `comparison`
- `checklist`
- `summary`
