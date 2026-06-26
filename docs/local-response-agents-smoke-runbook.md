# Local Response Agents Manual Smoke Runbook

This runbook gives safe manual request-body examples for the 11 implemented local response agents.

These examples are manual local checks only. They are not automated certification, CI validation, full-suite validation, clean Windows VM validation, LAN token validation, private-alpha certification, production readiness, or security certification.

To record manual observations, use the [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md).

## Prerequisites

- Jarvis Core is running locally.
- Use loopback/local dashboard access, such as `http://127.0.0.1:8000`.
- For non-loopback LAN access, existing dashboard token rules apply.
- Use the JSON request bodies below with a local API client or other loopback-only manual request tool.
- Do not include secrets, tokens, login details, account names, real emails, private local paths, or protected content in smoke inputs.

## Global Safety Note

- No paid APIs.
- No connectors.
- No OAuth or account access.
- No browser automation.
- No cloud sync.
- No sending, posting, or purchases.
- No file mutation for response-only agents.
- No task persistence for response-only agents.
- No CI, clean VM, private-alpha, production, or security certification claims.

## Expected Response Checks

For each manual response, check the relevant fields without treating the result as validation or certification:

- `agentId` matches the target agent.
- `status` is local-only, or the response includes a local-only `mode`.
- Safety fields show no external services.
- Safety fields show no connector execution.
- Safety fields show no persistence or mutation for response-only agents.
- Limitations or warnings do not claim external verification, CI validation, clean VM validation, LAN token boundary proof, private-alpha certification, production readiness, or security certification.

## 1. Local Research Agent

Endpoint: `POST /agents/research/local-brief`

Example JSON request body:

```json
{
  "topic": "Local alpha reviewer notes",
  "notes": "Reviewers need a concise local-only brief. The work should avoid external services and avoid validation claims.",
  "sourceTitles": ["Reviewer notes"],
  "questions": ["What should reviewers focus on?"],
  "outputType": "brief"
}
```

Expected response checks:

- `agentId` is `local_research_agent`.
- `status` or `mode` indicates local-only operation.
- Safety fields show no browsing, paid APIs, connectors, account access, or file mutation.

## 2. File/Data Agent

Endpoint: `POST /agents/files/local-summary`

This example requires a registered project named `Jarvis`. The File/Data Agent accepts a registered `projectName` only and does not accept raw arbitrary paths.

Example JSON request body:

```json
{
  "projectName": "Jarvis"
}
```

Expected response checks:

- `agentId` is `file_data_agent`.
- `status` or `mode` indicates local-only registered-project metadata.
- Safety fields show no arbitrary path scanning, protected-content reads, uploads, command execution, or mutation.

## 3. Local Planning Agent

Endpoint: `POST /agents/planning/local-plan`

Example JSON request body:

```json
{
  "goal": "Prepare a local manual smoke checklist",
  "contextNotes": "The checklist should exercise response-only agents without claiming certification.",
  "constraints": ["No external services", "No task creation"],
  "resources": ["Existing local docs"],
  "blockers": ["Needs human review"],
  "timeframe": "One local session",
  "desiredOutputType": "checklist"
}
```

Expected response checks:

- `agentId` is `local_planning_agent`.
- `status` or `mode` indicates local-only response-only planning.
- Safety fields show no task persistence, reminders, calendar/email actions, external services, or mutation.

## 4. Local Drafting Agent

Endpoint: `POST /agents/drafting/local-draft`

Example JSON request body:

```json
{
  "purpose": "Draft a note for local reviewers",
  "audience": "Local manual testers",
  "notes": "Ask reviewers to try the local smoke examples and report confusing wording.",
  "tone": "clear",
  "format": "message",
  "constraints": ["No hype", "No certification claims"],
  "mustInclude": ["manual local checks only"],
  "mustAvoid": ["guaranteed"]
}
```

Expected response checks:

- `agentId` is `local_drafting_agent`.
- `status` or `mode` indicates local-only response-only drafting.
- Safety fields show no draft persistence, email sending, public posting, account access, file writes, or connectors.

## 5. Local Review Agent

Endpoint: `POST /agents/review/local-review`

Example JSON request body:

```json
{
  "subject": "Manual smoke runbook wording",
  "content": "The runbook should be clear that checks are local and manual. It should not claim CI, clean VM validation, or certification.",
  "reviewType": "safety",
  "audience": "Local maintainers",
  "criteria": ["Clear scope", "No validation overclaims"],
  "constraints": ["No external verification claims"],
  "severity": "balanced"
}
```

Expected response checks:

- `agentId` is `local_review_agent`.
- `status` or `mode` indicates local-only response-only review.
- Safety fields show no fact verification, repo inspection, tests, persistence, file access, or connectors.

## 6. Local Decision Agent

Endpoint: `POST /agents/decision/local-decision`

Example JSON request body:

```json
{
  "decision": "Choose a manual smoke check format",
  "options": ["Short checklist", "Long worksheet"],
  "criteria": ["Easy to repeat", "Low risk of overclaiming"],
  "constraints": ["No automation", "No external services"],
  "priorities": ["Clarity", "Safety"],
  "contextNotes": "The result should help local testers without creating persistent decisions.",
  "decisionStyle": "safest"
}
```

Expected response checks:

- `agentId` is `local_decision_agent`.
- `status` or `mode` indicates local-only response-only decision support.
- Safety fields show no professional validation, purchases, sending, posting, persistence, file access, or external calls.

## 7. Local Troubleshooting Agent

Endpoint: `POST /agents/troubleshooting/local-triage`

Example JSON request body:

```json
{
  "problem": "A manual smoke response looks incomplete",
  "symptoms": ["Expected safety fields are missing from the response"],
  "errorMessages": ["No error message was shown"],
  "environmentNotes": "Local Jarvis Core manual smoke session on loopback.",
  "attemptedFixes": ["Refreshed the local API client"],
  "constraints": ["No command execution", "No file inspection"],
  "urgency": "normal",
  "troubleshootingType": "workflow_issue"
}
```

Expected response checks:

- `agentId` is `local_troubleshooting_agent`.
- `status` or `mode` indicates local-only response-only troubleshooting.
- Safety fields show no command execution, file or log reads, repo inspection, repair actions, downloads, uploads, or mutation.

## 8. Local Summarization Agent

Endpoint: `POST /agents/summarization/local-summary`

Example JSON request body:

```json
{
  "title": "Manual smoke notes",
  "content": "The local response agents returned structured outputs. Reviewers should check agent IDs, local-only status, and safety flags.",
  "summaryType": "bullets",
  "audience": "Local maintainers",
  "detailLevel": "medium",
  "focusAreas": ["safety fields", "manual checks"],
  "mustPreserve": ["local-only status"],
  "mustAvoid": ["certified"]
}
```

Expected response checks:

- `agentId` is `local_summarization_agent`.
- `status` or `mode` indicates local-only response-only summarization.
- Safety fields show no file reads, document retrieval, source or citation verification, persistence, repo inspection, or tests.

## 9. Local Extraction Agent

Endpoint: `POST /agents/extraction/local-extract`

Example JSON request body:

```json
{
  "title": "Manual smoke findings",
  "content": "Agent ID should match. Status should be local-only. Safety flags should show no connectors, no persistence, and no mutation.",
  "extractionType": "requirements",
  "focusAreas": ["response checks", "safety boundaries"],
  "mustCapture": ["no connectors"],
  "mustIgnore": ["certified"],
  "detailLevel": "medium"
}
```

Expected response checks:

- `agentId` is `local_extraction_agent`.
- `status` or `mode` indicates local-only response-only extraction.
- Safety fields show no file reads, document retrieval, source or citation verification, task creation, persistence, repo inspection, or tests.

## 10. Local Classification Agent

Endpoint: `POST /agents/classification/local-classify`

Example JSON request body:

```json
{
  "title": "Manual smoke triage",
  "content": "README link updates are documentation work. Safety wording review is high priority.",
  "items": ["Check README link", "Review safety wording"],
  "classificationType": "priority",
  "labels": ["docs", "safety"],
  "criteria": ["manual review impact"],
  "constraints": ["no task creation"],
  "detailLevel": "medium"
}
```

Expected response checks:

- `agentId` is `local_classification_agent`.
- `status` or `mode` indicates local-only response-only classification.
- Safety fields show no file reads, document retrieval, source or citation verification, task creation, agent calls, persistence, or certification.

## 11. Local Transformation Agent

Endpoint: `POST /agents/transformation/local-transform`

Example JSON request body:

```json
{
  "title": "Manual smoke notes",
  "content": "Check agent ID. Confirm local-only status. Review safety flags.",
  "items": ["Check agent ID", "Confirm local-only status", "Review safety flags"],
  "targetFormat": "checklist",
  "audience": "Local maintainers",
  "constraints": ["No file export"],
  "mustPreserve": ["local-only status"],
  "mustAvoid": ["certified"],
  "detailLevel": "medium"
}
```

Expected response checks:

- `agentId` is `local_transformation_agent`.
- `status` or `mode` indicates local-only response-only transformation.
- Safety fields show no file reads or writes, document/spreadsheet/deck/export creation, persistence, repo inspection, tests, or connectors.

## What This Does Not Prove

- Does not prove CI validation.
- Does not prove full-suite validation.
- Does not prove clean Windows VM validation.
- Does not prove LAN token boundary behavior.
- Does not prove private-alpha certification.
- Does not prove production readiness.
- Does not prove security certification.
