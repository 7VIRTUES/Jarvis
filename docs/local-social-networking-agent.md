# Local Social / Networking / High-Class Coach Agent

The Local Social / Networking / High-Class Coach Agent turns user-provided social, networking, etiquette, event-prep, conversation, presentation, confidence, grooming/presence, and social-polish notes into structured local planning suggestions.

It is manual-input only, local-only, and response-only. It does not access contacts, email, calendars, social platforms, DMs, messages, profiles, location, camera, microphone, files, accounts, or external services.

## Endpoint

`POST /agents/social-networking/local-plan`

## Example Request

```json
{
  "profileName": "Local Social Profile",
  "socialGoal": "Prepare for a polished robotics networking reception with respectful conversation and follow-up options.",
  "setting": "University networking reception",
  "peopleContext": "Students, alumni, professors, and robotics industry guests may attend.",
  "eventNotes": "Short conversations, light refreshments, and informal introductions after a project showcase.",
  "conversationTopics": ["Robotics projects", "Career paths", "Research interests"],
  "networkingGoals": ["Practice concise introductions", "Ask thoughtful questions", "Identify welcome follow-up opportunities"],
  "presentationNotes": "Aim for calm, clear, and sincere rather than flashy.",
  "constraints": ["Manual planning only", "No contact, email, calendar, or social platform access"],
  "comfortLevel": "Somewhat nervous but willing to practice.",
  "desiredOutputType": "social_brief"
}
```

## Output Types

- `social_brief`
- `conversation_plan`
- `networking_plan`
- `event_prep`
- `etiquette_checklist`
- `presence_plan`
- `follow_up_draft`
- `social_review`

Unsupported output types fall back to `social_brief`.

## Safety Boundaries

- Uses only the request body supplied by the local user.
- No contacts/email/calendar/social-platform/messaging/location/account connectors.
- No contact access, email sending, calendar access, social platform access, messaging, public posting, profile scraping, location access, camera access, microphone access, file reads, file writes, database writes, browsing, scraping, paid APIs, or external services.
- No sending, posting, scheduling, scraping, tracking, identifying private information, task creation, persistence, shell execution, file mutation, or account mutation.
- No manipulation, coercion, deception, harassment, stalking, doxxing, impersonation, evasion, social outcome guarantees, elite acceptance guarantees, relationship outcome guarantees, hiring outcome guarantees, reputation verification, etiquette certification, production readiness, or security certification.
- Legal, workplace, harassment, consent, safety, and mental-health concerns should be handled with appropriate human, workplace, legal, safety, or professional support.

## Response Shape

Responses include `agentId`, `status`, `mode`, `profileName`, `socialGoal`, `desiredOutputType`, `socialFocus`, `settingSummary`, `conversationPlan`, `networkingPlan`, `eventPrep`, `etiquetteChecklist`, `presencePlan`, `followUpDrafts`, `socialReview`, `nextActions`, `openQuestions`, `warnings`, `limitations`, and `safety`.

## Related Local Response-Agent Docs

- [Local Response Agents Index](local-response-agents-index.md)
- [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md)
- [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)

The smoke runbook and evidence template are manual evidence aids. They do not prove validation or certification.
