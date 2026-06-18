# Dashboard Project Profile and Security Review Surfaces

Jarvis exposes local dashboard surfaces for two already implemented read-only foundations:

- Project Profiles and workspace boundary summaries
- Security/Safety Review Agent report creation and report visibility

These surfaces are for local visibility and registered-project review only.

## Project Profiles

The dashboard profile API summarizes safe project metadata:

- Project name
- Project type
- Detected languages and frameworks
- Package manager
- Preferred check order
- Git clean/dirty state when available
- Documentation presence
- Future connector placeholder status
- Recommended Jarvis mode
- Warning and blocked-reason counts
- Workspace boundary status

The dashboard intentionally omits raw profile internals such as full root paths from profile summaries.

## Workspace Boundary Status

Each profile summary includes a concise boundary status:

- Whether the project root validated
- Whether protected filename patterns are active
- Whether runtime/cache skip directories are active
- Warning count
- Blocked reason count

The dashboard does not edit workspace roots and does not accept arbitrary raw paths for these profile summaries.

## Security/Safety Reviews

The dashboard can run a local read-only Security/Safety Review for a registered project. The action:

- Uses the existing registered project path
- Runs the existing local review service
- Writes the existing local Markdown report
- Returns verdict, finding counts, and report metadata

The dashboard does not expose secret snippets or protected file contents.

## Local API

Profile summaries:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/projects/profiles
```

Run a registered-project review:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/projects/sample/security-review
```

Read the latest registered-project review metadata:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/projects/sample/security-review/latest
```

Report content remains available through the existing guarded report/review endpoints.

## Guard Behavior

All new dashboard/API surfaces use the existing dashboard/LAN access guard. Loopback access is allowed, and non-loopback dashboard access requires the configured LAN token.

## Safety Boundaries

These surfaces do not install dependencies, execute scripts, call external services, use paid APIs, enable future connectors, use OAuth or cloud sync, add telemetry, write Git state, rewrite history, delete files, rotate secrets, certify security, or scan the whole PC.

## Limitations

Project profile detection is lightweight and metadata-based. Security/Safety Review findings are review aids, not compliance certification or secret cleanup. If a real secret is found, rotation, revocation, and history-cleanup decisions happen outside these dashboard surfaces.
