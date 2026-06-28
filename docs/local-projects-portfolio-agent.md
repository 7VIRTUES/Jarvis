# Local Projects / Portfolio Agent

The Local Projects / Portfolio Agent turns user-provided project and portfolio notes into structured local planning, drafting, and prioritization suggestions.

It is manual-input only, local-only, and response-only. It does not inspect GitHub, local repos, files, project registries, source code, commits, branches, websites, analytics, resumes, accounts, or external services.

## Endpoint

`POST /agents/projects-portfolio/local-plan`

## Example Request

```json
{
  "profileName": "Local Portfolio Profile",
  "portfolioGoal": "Prepare a project portfolio plan for robotics software internship conversations.",
  "targetAudience": "Recruiters and technical reviewers reading user-provided portfolio notes.",
  "targetRoles": ["Robotics software intern", "Computer vision intern"],
  "projectNotes": ["Vascular-Twin planning prototype", "Robot perception demo", "Local Jarvis response-agent work"],
  "skills": ["Python", "C++", "Computer vision", "Technical writing"],
  "proofArtifacts": ["Case study draft", "Demo outline", "Screenshot checklist"],
  "currentStatus": "Projects need clearer summaries and manually reviewed proof artifacts.",
  "constraints": ["Manual planning only", "No repo or GitHub inspection"],
  "priorities": ["Show technical depth", "Keep claims human-reviewed", "Make proof easy to scan"],
  "timeline": "Prepare a first portfolio pass before internship outreach.",
  "desiredOutputType": "portfolio_brief"
}
```

## Output Types

- `portfolio_brief`
- `project_inventory`
- `project_roadmap`
- `github_profile_plan`
- `resume_project_pitch`
- `case_study_outline`
- `portfolio_website_copy`
- `proof_of_work_plan`

Unsupported output types fall back to `portfolio_brief`.

## Safety Boundaries

- Uses only the request body supplied by the local user.
- No GitHub/repo/filesystem/account connectors.
- No repo inspection, project registry inspection, source-code inspection, file reads, file writes, branch checks, commit checks, website checks, analytics checks, resume reads, scraping, browsing, paid APIs, or external services.
- No file creation, repo edits, issue creation, commits, pushes, uploads, publishing, submissions, persistence, shell execution, or mutation.
- No claims of live GitHub verification, portfolio quality certification, hiring outcome certainty, project completion, technical correctness, code review validation, official validation, production readiness, or certification.
- Employment, legal, IP/copyright, academic, and public-claim concerns should be confirmed by appropriate humans or qualified professionals.

## Response Shape

Responses include `agentId`, `status`, `mode`, `profileName`, `portfolioGoal`, `desiredOutputType`, `portfolioFocus`, `audienceSummary`, `projectInventory`, `projectRoadmap`, `githubProfilePlan`, `resumeProjectPitch`, `caseStudyOutline`, `portfolioWebsiteCopy`, `proofOfWorkPlan`, `prioritizationNotes`, `nextActions`, `openQuestions`, `warnings`, `limitations`, and `safety`.

## Related Local Response-Agent Docs

- [Local Response Agents Index](local-response-agents-index.md)
- [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md)
- [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)

The smoke runbook and evidence template are manual evidence aids. They do not prove validation or certification.
