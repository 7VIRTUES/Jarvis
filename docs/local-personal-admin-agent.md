# Local Personal Admin / Documents Agent

The Local Personal Admin / Documents Agent turns user-provided personal admin and document-prep notes into local planning output for school forms, loan paperwork, application checklists, ID/admin reminders, renewal prep, appointment prep, form review checklists, records organization, and deadline planning.

It is manual-input only, local-only, and response-only.

## Endpoint

`POST /agents/personal-admin/local-plan`

## Request Fields

- `profileName`: optional string
- `adminGoal`: required string
- `documentTypes`: optional list of strings
- `deadlines`: optional list of strings
- `requirements`: optional list of strings
- `currentStatus`: optional string
- `constraints`: optional list of strings
- `peopleOrOfficesInvolved`: optional list of strings
- `notes`: optional string
- `desiredOutputType`: optional string, defaults to `admin_brief`

Supported output types:

- `admin_brief`
- `document_checklist`
- `deadline_plan`
- `form_prep_plan`
- `appointment_prep`
- `records_organization`
- `submission_readiness`
- `follow_up_plan`

Unsupported output types are normalized to `admin_brief`.

## Example Request

```json
{
  "profileName": "Local Admin Profile",
  "adminGoal": "Prepare a manual checklist for school forms and loan paperwork before an office appointment.",
  "documentTypes": ["School enrollment form", "Loan deferment paperwork", "Photo ID copy checklist"],
  "deadlines": ["Forms due before the next advising appointment", "Loan paperwork review needed this month"],
  "requirements": ["Confirm required fields", "List supporting records", "Mark signature fields", "Prepare questions for the office"],
  "currentStatus": "Forms are gathered but not fully reviewed.",
  "constraints": ["Manual planning only", "No file, portal, email, calendar, or cloud-drive access"],
  "peopleOrOfficesInvolved": ["School advising office", "Loan servicer help desk"],
  "notes": "User wants a calm readiness review before submitting anything outside Jarvis.",
  "desiredOutputType": "admin_brief"
}
```

## Response Shape

The response includes:

- `agentId`
- `status`
- `mode`
- `profileName`
- `adminGoal`
- `desiredOutputType`
- `adminFocus`
- `statusSummary`
- `documentChecklist`
- `deadlinePlan`
- `formPrepPlan`
- `appointmentPrep`
- `recordsOrganization`
- `submissionReadiness`
- `followUpPlan`
- `nextActions`
- `openQuestions`
- `warnings`
- `limitations`
- `safety`

## Safety Boundaries

The agent bases output only on request-provided data. It does not read documents, files, IDs, PDFs, email, calendars, portals, accounts, cloud drives, school systems, loan systems, government sites, or external services.

The agent does not submit forms, send emails, schedule appointments, create reminders or tasks, upload files, sign documents, make payments, persist records, mutate files, write to databases, browse, scrape, use connectors, use paid APIs, or execute shell commands.

It does not claim legal, tax, immigration, school, loan, government, compliance, identity, submission, production, security, or certification validation.

For official forms, legal/tax/immigration/loan/school/government decisions, compliance questions, identity questions, deadlines, fees, eligibility, signatures, and submission rules, the response recommends official or professional confirmation.

## Related Manual Evidence Aids

- [Local Response Agents Index](local-response-agents-index.md)
- [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md)
- [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)

These docs are manual review aids only. They do not prove validation or certification, and they do not claim tests, CI, clean Windows VM validation, private-alpha certification, production readiness, or security certification.
