# Local Legal / Immigration / Official Matters Agent

The Local Legal / Immigration / Official Matters Agent turns user-provided official-matter summaries, document lists, dates, agency notes, user questions, urgency notes, and desired outcomes into structured local organization guidance.

It is local-only, response-only, and manual-input-only.

## Purpose

- Help organize official tasks, form planning, document checklists, deadline awareness, question drafting, appointment prep, immigration or school or government-office planning, and plain-language summaries of user-provided official matter notes.
- Keep outputs based only on the request body.

## Scope

- Does not browse, call paid APIs, use connectors, access accounts, read files, write files, write database records, create tasks, create reminders, send email, book appointments, pay fees, submit forms, file applications, sign documents, contact agencies, or mutate local state.
- Does not access government portals, immigration accounts, school portals, court systems, legal databases, email, calendar, files, payment systems, maps, location, or external services.
- Does not create persistent legal, immigration, school, government, deadline, filing, account, appointment, or payment records.

## Endpoint

`POST /agents/legal-immigration-official/local-plan`

## Request Body Example

```json
{
  "request": "Make a document checklist for an immigration appointment based only on this summary.",
  "outputType": "document_checklist",
  "matterType": "immigration appointment preparation",
  "jurisdictionOrCountryIfUserProvided": "User-provided country context only",
  "currentStatus": "User has an upcoming appointment and wants to organize documents.",
  "documentList": ["Passport", "Appointment notice", "School records", "Address history notes"],
  "deadlinesOrDates": ["Appointment date from user notes"],
  "officeOrAgencyNameIfUserProvided": "User-provided office name",
  "userQuestions": ["Which documents should I ask a qualified professional to review?"],
  "desiredOutcome": "Arrive prepared with organized questions.",
  "riskLevelOrUrgency": "Needs careful review but no emergency stated.",
  "constraintsOrNotes": "General organization only; no legal advice or filing."
}
```

## Supported Output Types

- `document_checklist`
- `appointment_prep`
- `question_list`
- `deadline_tracker`
- `plain_language_summary`
- `official_task_plan`
- `form_prep_outline`
- `call_script`
- `email_draft_outline`
- `risk_flags`
- `comparison`
- `checklist`
- `summary`

## Safety Boundaries

- Not a government, immigration, school, court, legal database, email, calendar, file, payment, map, location, account, or external-service connector.
- Does not submit forms, file applications, sign documents, pay fees, book appointments, send emails, contact agencies, persist records, mutate files, or create official actions.
- Does not provide legal advice, immigration advice, attorney review, eligibility certainty, deadline certainty, visa approval prediction, government acceptance, official compliance, or certification claims.
- Always treat output as organizational/general information only. Consult a qualified attorney, accredited immigration representative, school official, or relevant agency for high-stakes matters.
- Deportation or removal notices, court dates, arrests, missed deadlines, benefit termination, identity or document fraud issues, domestic violence, threats, or official notices require qualified help promptly.

## Related Docs

- [Local Response Agents Index](local-response-agents-index.md)
- [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md)
- [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)

These linked smoke and evidence docs are read-only docs/manual evidence aids and do not prove validation or certification.
