# Local Career / Job Search Agent

The Local Career / Job Search Agent turns user-provided career goals, resume notes, job targets, co-op or internship plans, interview prep notes, networking notes, skill gaps, projects, and constraints into structured local career-planning suggestions.

It is local-only, response-only, and manual-input-only.

## Purpose

- Help organize resume positioning, job-search strategy, networking scripts, interview prep, skill-gap planning, application checklists, and project pitch notes using only the request body.
- Return manual planning and drafting aids without checking accounts, job boards, company sites, school portals, contacts, email, calendar, GitHub, files, or external sources.
- Keep all output non-persistent and non-executing.

## Scope

- Does not access LinkedIn, Handshake, Indeed, company sites, Gmail, Calendar, contacts, school portals, job boards, GitHub, files, connectors, browser, paid API, database, shell, or cloud data.
- Does not browse, scrape, apply to jobs, submit forms, send messages, schedule interviews, create tasks, persist records, upload resumes, create files, or mutate external services.
- Does not claim job placement, interview guarantee, hiring certainty, salary certainty, visa or legal validation, employment-law advice, live job-market verification, application outcomes, networking responses, certification, or readiness.

## Endpoint

`POST /agents/career/local-plan`

## Request Body Example

```json
{
  "profileName": "Local Career Profile",
  "careerGoal": "Prepare for robotics software internships and co-op conversations.",
  "targetRoles": ["Robotics software intern", "Computer vision intern"],
  "targetIndustries": ["Robotics", "Health technology"],
  "currentExperience": "Course projects and local planning work in robotics and software.",
  "educationNotes": "Engineering student building robotics and applied software experience.",
  "skills": ["Python", "C++", "Computer vision", "Controls", "Technical writing"],
  "projects": ["Vascular-Twin planning prototype", "Robot perception demo"],
  "resumeNotes": "Emphasize project evidence, measurable scope, and manual review wording.",
  "jobSearchNotes": "Focus on a small manually reviewed target list.",
  "networkingNotes": "Prepare respectful informational conversation scripts.",
  "constraints": ["Manual planning only", "No live job-board verification"],
  "desiredOutputType": "career_brief"
}
```

## Supported Output Types

- `career_brief`
- `resume_positioning`
- `job_search_plan`
- `networking_plan`
- `interview_prep`
- `skill_gap_plan`
- `application_checklist`
- `project_pitch_plan`

## Safety Boundaries

- Manual-input only.
- Local-only.
- Response-only.
- Planning and drafting only.
- No LinkedIn/Handshake/job-board/email/calendar/contact/account connectors.
- No applying, submitting, messaging, scheduling, uploading, scraping, browsing, live verification, account access, job-board access, school portal access, GitHub access, file access, paid API, database, shell, connector, persistence, mutation, or external-service behavior.
- No persistence.
- No job placement, interview guarantee, salary certainty, hiring certainty, visa or legal validation, employment-law advice, live job-market verification, application outcome, networking response, certification, or readiness claim.
- Output is based only on user-provided input.

## Limitations

- Suggestions and drafts are review aids only.
- Legal, immigration, visa, salary-negotiation, employment-contract, work-authorization, and other high-stakes career questions require official or qualified professional confirmation.
- The agent does not prove resume quality, role fit, job availability, market demand, application readiness, interview readiness, hiring probability, salary outcomes, validation, certification, or readiness.

## Related Docs

- [Local Response Agents Index](local-response-agents-index.md)
- [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md)
- [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)

These linked smoke and evidence docs are read-only docs/manual evidence aids and do not prove validation or certification.
