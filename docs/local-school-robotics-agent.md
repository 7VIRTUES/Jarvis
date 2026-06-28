# Local School / Robotics Agent

The Local School / Robotics Agent turns user-provided school, Northeastern, robotics, research, course, co-op, professor, project, and study-planning notes into structured local preparation suggestions.

It is local-only, response-only, and manual-input-only.

## Purpose

- Help organize academic planning, robotics preparation, Vascular-Twin planning, course comparison, research outreach preparation, study schedules, co-op preparation, and campus-resource planning using only the request body.
- Return manual planning and drafting aids without checking school systems or external sources.
- Keep all output non-persistent and non-executing.

## Scope

- Does not access Northeastern systems, student portals, email, calendar, Handshake, registrar data, financial-aid accounts, professor websites, live course catalogs, GitHub, files, connectors, browser, paid API, database, shell, or cloud data.
- Does not browse, scrape, verify course availability, send emails, submit forms, register for classes, apply to jobs, create tasks, create calendar events, persist records, create files, or mutate external services.
- Does not claim admission, enrollment, financial-aid, visa, course-registration, co-op, professor-response, research-placement, graduation, employment, project-success, official academic validation, certification, or readiness certainty.

## Endpoint

`POST /agents/school-robotics/local-plan`

## Request Body Example

```json
{
  "studentName": "Local Student",
  "schoolName": "Northeastern",
  "programName": "Robotics-focused engineering plan",
  "termOrTimeline": "Next two academic terms",
  "academicGoal": "Prepare for robotics research, Vascular-Twin planning, and a stronger co-op search.",
  "roboticsFocus": "Robot perception, controls, simulation, and applied health robotics.",
  "courses": ["Robotics foundations", "Computer vision", "Control systems"],
  "professorsOrLabs": ["User-provided robotics lab note", "User-provided health robotics research note"],
  "projects": ["Vascular-Twin planning prototype", "Small robot perception demo"],
  "constraints": ["Manual planning only", "No live course availability verification"],
  "resources": ["Advisor notes", "Campus career center notes", "Robotics club notes"],
  "currentPreparation": "Completed introductory programming and early robotics reading.",
  "desiredOutputType": "school_brief"
}
```

## Supported Output Types

- `school_brief`
- `course_plan`
- `robotics_prep_plan`
- `research_outreach_plan`
- `project_roadmap`
- `study_schedule`
- `coop_prep_plan`
- `campus_resource_plan`

## Safety Boundaries

- Manual-input only.
- Local-only.
- Response-only.
- Planning and drafting only.
- No school portal, email, calendar, registrar, Handshake, financial-aid, account, live catalog, professor website, GitHub, file, browser, paid API, database, shell, connector, persistence, mutation, or external-service behavior.
- No registration, submission, sending, class registration, job application, live verification, official academic validation, admission, enrollment, financial-aid, visa, course-registration, co-op, professor-response, research-placement, graduation, employment, certification, or readiness claim.
- Output is based only on user-provided input.

## Limitations

- Suggestions and drafts are review aids only.
- Course, registrar, co-op, research, professor, campus-resource, financial-aid, visa, legal, medical, employment, and graduation questions require official school or qualified professional confirmation.
- The agent does not prove course availability, requirement fit, registration eligibility, professor interest, research placement, co-op eligibility, job outcomes, graduation progress, validation, certification, or readiness.

## Related Docs

- [Local Response Agents Index](local-response-agents-index.md)
- [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md)
- [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)

These linked smoke and evidence docs are read-only docs/manual evidence aids and do not prove validation or certification.
