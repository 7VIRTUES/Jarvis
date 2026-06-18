# Security/Safety Review Agent

The Security/Safety Review Agent is a local-only, read-only foundation for checking a registered project, or the Jarvis repo itself, for public-readiness and safety-boundary risks.

It produces a structured result and a Markdown report under the existing local reports directory. The agent id is `security_safety_agent`.

## What It Does

- Summarizes Git state when Git is available.
- Checks tracked or reviewed filenames for protected patterns such as `.env`, key files, local databases, and logs.
- Scans safe text files for likely secret and token patterns with values redacted.
- Scans safe text files for private local path patterns with snippets redacted.
- Checks documentation for unsafe public-release or production-readiness claims while allowing boundary wording such as "not implemented" or "No production release".
- Checks connector manifests to confirm future connectors remain `implemented=false` and `defaultEnabled=false`.
- Checks for public-readiness docs such as `README.md`, `SECURITY.md`, `CONTRIBUTING.md`, `docs/public-repo-readiness.md`, and `docs/public-safety-boundaries.md`.
- Notes whether dangerous-command policy references are present.

## What It Does Not Do

- It does not read protected file contents.
- It does not print raw secret values.
- It does not rotate secrets.
- It does not rewrite Git history.
- It does not delete files.
- It does not push, merge, force-push, or reset repositories.
- It does not call paid AI APIs or external services.
- It does not enable OAuth, cloud sync, telemetry, browser automation, or future connectors.
- It does not certify that a repository is secure.

## Scan Categories

Reports include:

- Project metadata
- Git state summary
- Protected file scan
- Secret-pattern scan
- Private-path scan
- Public-release claim scan
- Connector-placeholder scan
- Public-readiness documentation scan
- Dangerous command policy references
- Findings with severity
- Summary verdict
- Recommended next actions

Verdicts are `pass`, `pass_with_warnings`, `needs_review`, or `blocked`.

## Local API

When the local FastAPI service is running, create a review with:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/security/reviews -ContentType application/json -Body '{"projectName":"sample"}'
```

You can also pass `projectPath`, but the path must stay inside the Jarvis workspace root. If neither `projectName` nor `projectPath` is provided, the Jarvis repository itself is reviewed.

Read a generated report with:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/security/reviews/security-safety-sample-YYYYMMDDTHHMMSSZ.md
```

The endpoints use the same dashboard/LAN access guard as other sensitive local report surfaces.

Dashboard review actions and report visibility are documented in [Dashboard Project Profile and Security Review Surfaces](dashboard-profile-security-surfaces.md).

## Public Repo Readiness

This agent supports the public-readiness checklist by surfacing likely issues before human review. It is a helper, not a replacement for GitHub secret scanning, secret rotation, history review, or a final release decision.
