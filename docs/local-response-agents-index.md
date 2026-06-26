# Local Response Agents Index

This page is a read-only inventory of the implemented local response agents after Sub-Agents 1 through 11.

It does not define a new agent, endpoint, connector, workflow, or validation claim.

For safe manual request-body examples, see the [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md).

For manual evidence notes, see the [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md).

For a compact docs-only closeout summary, see the [Local Response Agents Closeout Status](local-response-agents-closeout-status.md).

## Global Boundaries

- No paid APIs.
- No connectors.
- No OAuth or account access.
- No browser automation.
- No cloud sync.
- No file mutation except existing Coding Agent workflows.
- No email sending, posting, or purchases.
- No task persistence for response-only agents.
- No claims of clean Windows VM validation, CI validation, private-alpha certification, production readiness, or security certification.

## Agents

| Agent | Endpoint | Status | Mode / boundary | Docs | Response mode | Safety notes |
| --- | --- | --- | --- | --- | --- | --- |
| Local Research Agent | `POST /agents/research/local-brief` | `implemented_local_only` | `local_only_user_provided_notes` | [docs](local-research-agent.md) | response-only | Uses user-provided notes only; no browsing, paid APIs, connectors, account access, or file mutation. |
| File/Data Agent | `POST /agents/files/local-summary` | `implemented_local_only` | `local_registered_project_metadata_only` | [docs](file-data-agent.md) | metadata-only | Summarizes registered-project metadata only; no arbitrary path scanning, protected-content reads, uploads, command execution, or mutation. |
| Local Planning Agent | `POST /agents/planning/local-plan` | `implemented_local_only` | `response_only_user_provided_planning` | [docs](local-planning-agent.md) | response-only | Uses user-provided planning inputs only; no persistent tasks, reminders, calendar/email items, files, database records, or external calls. |
| Local Drafting Agent | `POST /agents/drafting/local-draft` | `implemented_local_only` | `response_only_user_provided_drafting` | [docs](local-drafting-agent.md) | response-only | Uses user-provided drafting inputs only; no draft persistence, email sending, posting, account access, file writes, or connectors. |
| Local Review Agent | `POST /agents/review/local-review` | `implemented_local_only` | `response_only_user_provided_review` | [docs](local-review-agent.md) | response-only | Uses user-provided review content only; no fact verification, repo inspection, tests, persistence, file access, or connectors. |
| Local Decision Agent | `POST /agents/decision/local-decision` | `implemented_local_only` | `response_only_user_provided_decision_support` | [docs](local-decision-agent.md) | response-only | Uses user-provided decision inputs only; no professional validation, purchases, sending, posting, persistence, file access, or external calls. |
| Local Troubleshooting Agent | `POST /agents/troubleshooting/local-triage` | `implemented_local_only` | `response_only_user_provided_troubleshooting` | [docs](local-troubleshooting-agent.md) | response-only | Uses user-provided troubleshooting inputs only; no command execution, file/log reads, repo inspection, repair actions, downloads, uploads, or mutation. |
| Local Summarization Agent | `POST /agents/summarization/local-summary` | `implemented_local_only` | `response_only_user_provided_summarization` | [docs](local-summarization-agent.md) | response-only | Uses user-provided text only; no file reads, document retrieval, source/citation verification, persistence, repo inspection, or tests. |
| Local Extraction Agent | `POST /agents/extraction/local-extract` | `implemented_local_only` | `response_only_user_provided_extraction` | [docs](local-extraction-agent.md) | response-only | Uses user-provided text only; no file reads, document retrieval, source/citation verification, task creation, persistence, repo inspection, or tests. |
| Local Classification Agent | `POST /agents/classification/local-classify` | `implemented_local_only` | `response_only_user_provided_classification` | [docs](local-classification-agent.md) | response-only | Uses user-provided text and items only; no file reads, document retrieval, source/citation verification, task creation, agent calls, persistence, or certification. |
| Local Transformation Agent | `POST /agents/transformation/local-transform` | `implemented_local_only` | `response_only_user_provided_transformation` | [docs](local-transformation-agent.md) | response-only | Uses user-provided text and items only; no file reads/writes, document/spreadsheet/deck/export creation, persistence, repo inspection, tests, or connectors. |

## Dashboard Field

The dashboard summary exposes this inventory as `localResponseAgentsIndex`.

The dashboard section is read-only and links back to this page.
