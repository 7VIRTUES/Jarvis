# Project Profiles and Workspace Boundaries

Project Profiles give Jarvis a read-only summary of a registered project before an agent plans or reviews work. They are local metadata, not automation permissions.

## What Project Profiles Include

- Project identity and root path
- Root validation status
- Detected project type: `python`, `node`, `mixed`, or `unknown`
- Detected languages and lightweight framework hints
- Package manager and package scripts when `package.json` is safe to read
- Preferred check command order
- Git repository, branch, and clean/dirty summary when Git is available
- Runtime/cache directories to skip
- Protected filename patterns
- Public-readiness and security documentation presence
- Future connector placeholder status when connector manifests are present
- Recommended Jarvis mode and risk budget hints
- Warnings and blocked reasons

## Workspace Boundary Validator

The Workspace Boundary Validator resolves paths before making decisions. It can tell callers whether a path:

- Stays inside the project root
- Escapes through `..` traversal
- Escapes through symlink resolution
- Is in a runtime, cache, dependency, or local Jarvis runtime directory
- Matches a protected filename pattern
- Is safe to read as approved metadata
- Is safe to scan as normal text

Decisions are structured with allow/skip/block status and a reason so callers can report safe explanations without opening protected files.

## Safe Metadata

Profile generation may read safe metadata files inside the validated project root, such as:

- `package.json`
- `pyproject.toml`
- `requirements.txt`
- `README.md`
- `SECURITY.md`
- `CONTRIBUTING.md`
- `docs/public-repo-readiness.md`
- `docs/public-safety-boundaries.md`

Package scripts are detected but never executed.

## Protected and Skipped Paths

Protected filename patterns include `.env`, `.env.*`, key files, service account files, local databases, and logs. Protected file contents are not read.

Runtime and cache directories skipped by default include `.git`, `node_modules`, `dist`, `build`, `.venv`, `venv`, `__pycache__`, `.pytest_cache`, `tmp`, `.jarvis/logs`, and `.jarvis/runtime`.

## Local API

When the local FastAPI service is running, profile a registered project with:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/projects/sample/profile
```

Refresh is currently read-only regeneration:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/projects/sample/profile/refresh
```

These endpoints use the dashboard/LAN access guard. They do not edit project files.

## Agent Support

Project Profiles help the Coding Agent choose safer check commands and help the Security/Safety Review Agent share workspace boundary rules. The Security/Safety Review Agent still keeps its redaction and protected-file skipping behavior.

Dashboard profile summaries are documented in [Dashboard Project Profile and Security Review Surfaces](dashboard-profile-security-surfaces.md).

## Safety Boundaries

This foundation does not install dependencies, execute scripts, call external services, use paid APIs, enable OAuth or cloud sync, add telemetry, write Git history, push, merge, delete files, or implement future connectors.

## Current Limitations

Detection is intentionally lightweight. It uses local metadata and conservative heuristics, so humans still decide the correct mode, scope, and readiness of a project before higher-risk work.
