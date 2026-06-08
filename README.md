# Jarvis PC Local

Jarvis PC Local is a local-first Windows assistant platform foundation. Version 0.1A establishes the core service, registries, safety policy, project inspection, and audit logging needed before any execution or connector features are added.

## v0.1A Scope

- FastAPI local service with `/health`
- SQLite state initialization
- JSON config and manifest loading
- JSONL audit logs for actions, commands, and security events
- Project, agent, tool, and connector registries
- Safe Action Runtime skeleton
- Permission Engine with hard blocks for dangerous operations
- Coding Agent inspection, check planning, Codex CLI detection, and Markdown reports
- Disabled placeholder connector manifests
- Sample TypeScript project
- Pytest safety and registry tests

## v0.1B Workflow Foundation

Closeout status: v0.1B is complete after local validation. v0.1C is complete as a private-alpha readiness foundation with dashboard, report, settings/status, LAN token protection, loopback-only setup guidance, stop-task control boundary, desktop-shell placeholder, first-run wizard placeholder, and private-alpha packaging readiness foundations. Post-v0.1C work must be planned before implementation begins.

The first v0.1B slice adds local task orchestration without enabling Codex or shell execution:

- task queue APIs
- event log APIs
- approval queue APIs
- project write locks
- dry-run planning
- expanded action receipts
- risk budget validation
- local diagnostics export without secret values
- implementation report validation

The Codex execution planning slice adds safe future-run planning without enabling Codex execution:

- Codex plan APIs
- validated command previews
- prompt content planning for `.jarvis/prompts/current-task.md`
- approval records for future execution
- plan receipts and events
- diagnostics plan summaries without prompt content

The controlled Codex execution slice adds one approved-plan execution endpoint. It uses the official local Codex CLI only, with a fixed argv template, `workspace-write`, `shell=False`, registered project boundaries, and action receipts.

The post-Codex review slice adds a policy gate after the Codex process returns:

- git status and diff-stat review
- changed-file and diff-line budget enforcement
- protected-file path detection without reading protected contents
- dependency/package-file change detection
- safe planned-check generation from detected package scripts only

If the post-review gate requires user review, Jarvis stops before checks.

The check execution receipts slice executes only the generated safe check plan after review passes:

- fixed argv commands for detected package scripts only
- Safe Action Runtime receipts for each check
- redacted stdout/stderr excerpts stored on the execution record
- stop-on-first-failed-or-blocked-check behavior

The controlled repair loop slice may run at most two Codex repair attempts after failed safe checks. Each repair uses fixed Codex argv, redacted failed-check context, post-repair policy review, and safe checks again. It stops on repeated failures, max-run limits, review-required changes, protected/dependency-file changes, or risk-budget issues.

## v0.1C Dashboard Foundation

v0.1C closes with a read-only dashboard and report visibility foundation. This slice adds local status, safety, connector-placeholder, report-list, and report-detail views without adding write controls or future automation.

Slice 2 adds read-only settings/status visibility. Settings are status placeholders only; there are no editable controls, no settings persistence, and no save actions.

Slice 3 adds LAN dashboard/API token protection. Loopback access remains available without a token. Non-loopback dashboard/API access requires a configured `JARVIS_LAN_DASHBOARD_TOKEN`; if the token is missing or too short, LAN access is denied. Tokens are accepted only through `X-Jarvis-LAN-Token` or `Authorization: Bearer` headers, never query strings.

Slice 4 adds loopback-only LAN setup guidance and status. The setup page explains the environment variable source, accepted headers, and unsupported token channels without exposing token values, token fragments, hashes, or editable controls.

Slice 5 adds an Active Task / Stop Task boundary for Jarvis-owned task records. The dashboard and API can list active Jarvis tasks and stop only known task IDs already tracked in the local Jarvis task table. It records the existing `task.canceled` event and releases Jarvis project locks. It is not arbitrary process control and does not accept PID, process name, shell command, or Windows service identifiers.

Slice 6 adds a Tauri desktop shell placeholder/readiness foundation under `apps/desktop`. It is documentation and status metadata only. It does not install Tauri, add package dependencies, launch a desktop app, add an auto-updater, add telemetry, or implement installer/private-alpha packaging. A future desktop shell must wrap the local dashboard without bypassing LAN/token protection or Safe Action Runtime boundaries.

Slice 7 adds a first-run wizard placeholder/readiness foundation. The first-run page and status are loopback-only and informational. They do not persist setup state, write configuration files, generate or store tokens, create accounts, use OAuth, enable cloud sync, add telemetry, add an auto-updater, or implement installer/private-alpha packaging.

Slice 8 adds private-alpha packaging documentation and readiness metadata. No installer artifact, Tauri production build, code signing, auto-updater, telemetry, GitHub release automation, public release, or cloud distribution is implemented. Manual local run remains the current path, and fresh Windows VM validation is required before any future private-alpha build.

Post-v0.1C future work still needs planning before implementation: full pairing wizard, QR/mobile pairing, production first-run setup, and real installer/private-alpha packaging.

## Run Jarvis Core

```powershell
python -m uvicorn --app-dir services/jarvis-core/src jarvis_core.app:app --reload
```

The service is local-only by design. The `/health` endpoint returns the app name, version, status, and local mode.

## ChatGPT and Codex Workflow

Jarvis uses ChatGPT Project for planning, architecture, safety review, prompt writing, review triage, and next-step decisions. Codex is used for local implementation only: code/docs edits, tests, local commands, and approved local commits. See [docs/chatgpt-codex-workflow.md](docs/chatgpt-codex-workflow.md).

Key workflow endpoints:

- `POST /tasks`
- `GET /tasks`
- `GET /tasks/{task_id}`
- `POST /tasks/{task_id}/cancel`
- `GET /events`
- `GET /tasks/{task_id}/events`
- `GET /approvals`
- `GET /approvals/{approval_id}`
- `POST /approvals/{approval_id}/approve`
- `POST /approvals/{approval_id}/reject`
- `GET /diagnostics/export`
- `POST /reports/validate`
- `POST /codex/plans`
- `GET /codex/plans`
- `GET /codex/plans/{plan_id}`
- `POST /codex/plans/{plan_id}/cancel`
- `POST /codex/plans/{plan_id}/approve-for-future-execution`
- `POST /codex/plans/{plan_id}/reject`
- `POST /codex/plans/{plan_id}/execute`
- `GET /dashboard`
- `GET /api/dashboard/summary`
- `GET /api/safety/summary`
- `GET /api/settings/summary`
- `GET /api/tasks/active`
- `GET /api/tasks/stop/status`
- `POST /api/tasks/{task_id}/stop`
- `GET /api/reports`
- `GET /api/reports/{report_id}`
- `GET /setup/lan`
- `GET /api/setup/lan/status`
- `GET /setup/first-run`
- `GET /api/setup/first-run/status`

Dashboard and dashboard-related API endpoints, including task status and stop-task routes, are guarded for LAN access. Loopback requests can read or use them without a token; non-loopback requests require a valid configured token.

LAN setup and first-run setup placeholder endpoints are loopback-only. Non-loopback requests are denied even with a token until a real pairing/setup UX is planned and implemented.

## Run Tests

```powershell
python -m pytest
```

## Safety Model

Jarvis validates actions before tools execute them. Dangerous commands, protected secret reads, file deletion automation, browser session access, public posting, email sending, payment actions, and unsupported connector actions are blocked or marked as requiring approval. Blocked safety decisions are written to JSONL security logs.

## v0.1 Exclusions

Jarvis v0.1C Slice 8 does not call paid AI APIs, run browser automation, send email, post publicly, process payments, sync to cloud, expose editable settings, run arbitrary process killing, run autonomous background repair, run unrestricted repair loops, implement token generation or persistence, implement account setup or OAuth, implement a full pairing wizard, install Tauri dependencies, add an auto-updater, add telemetry, create installer packaging, add code signing, add release automation, publish downloads, or implement external account connectors. Stop-task controls apply only to Jarvis-owned task records. Controlled Codex execution and bounded post-check repair remain limited to approved plans through the official local CLI.
