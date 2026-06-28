# Local Learning / Study Coach Agent

The Local Learning / Study Coach Agent turns user-provided learning goals, study topics, schedule notes, current skill level, resources, weak areas, preferred methods, constraints, and motivation notes into structured local study-planning suggestions.

It is manual-input only, local-only, and response-only. It does not access school portals, LMS systems, textbooks, websites, files, calendars, task apps, Anki, Notion, Google Drive, GitHub, accounts, or external services.

## Endpoint

`POST /agents/learning-study/local-plan`

## Example Request

```json
{
  "learnerName": "Local Learner",
  "learningGoal": "Build a steady study plan for robotics controls and computer vision foundations.",
  "topics": ["PID control", "State estimation", "Image filtering", "Camera calibration"],
  "currentLevel": "Comfortable with programming basics; weaker on math-heavy explanations.",
  "timeline": "Prepare over the next six weeks before project work intensifies.",
  "availableTime": "Four 45-minute blocks during the week and one weekend review block.",
  "resources": ["Class notes", "Practice problem set", "User-provided project notes"],
  "weakAreas": ["Deriving equations", "Explaining assumptions", "Remembering formulas"],
  "preferredMethods": ["Active recall", "Practice problems", "Feynman explanations"],
  "constraints": ["Manual planning only", "No LMS or calendar connection"],
  "motivationNotes": "Connect each study block to stronger robotics project confidence.",
  "desiredOutputType": "learning_brief"
}
```

## Output Types

- `learning_brief`
- `study_plan`
- `learning_roadmap`
- `active_recall_plan`
- `feynman_drills`
- `spaced_repetition_plan`
- `weekly_review`
- `boss_test`

Unsupported output types fall back to `learning_brief`.

## Safety Boundaries

- Uses only the request body supplied by the local user.
- No school/LMS/calendar/task/file/app/account connectors.
- No school portal access, LMS access, textbook access, website access, calendar access, task app access, Anki access, Notion access, Google Drive access, GitHub access, account access, file reads, file writes, database writes, downloads, browsing, scraping, paid APIs, or external services.
- No external flashcard creation, calendar event creation, task creation, study-record persistence, assignment submission, shell execution, or mutation.
- No official tutoring, course credit, grade improvement certainty, exam score certainty, certification, academic validation, mastery validation, official validation, production readiness, or security certification.
- Official academic requirements, exams, accommodations, health concerns, and high-stakes education decisions should be confirmed with official sources or qualified professionals.

## Response Shape

Responses include `agentId`, `status`, `mode`, `learnerName`, `learningGoal`, `desiredOutputType`, `learningFocus`, `baselineSummary`, `topicMap`, `studyPlan`, `learningRoadmap`, `activeRecallPlan`, `feynmanDrills`, `spacedRepetitionPlan`, `weeklyReview`, `bossTest`, `progressChecklist`, `nextActions`, `openQuestions`, `warnings`, `limitations`, and `safety`.

## Related Local Response-Agent Docs

- [Local Response Agents Index](local-response-agents-index.md)
- [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md)
- [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)

The smoke runbook and evidence template are manual evidence aids. They do not prove validation or certification.
