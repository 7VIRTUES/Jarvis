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

## Run Jarvis Core

```powershell
python -m uvicorn --app-dir services/jarvis-core/src jarvis_core.app:app --reload
```

The service is local-only by design. The `/health` endpoint returns the app name, version, status, and local mode.

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

## Run Tests

```powershell
python -m pytest
```

## Safety Model

Jarvis validates actions before tools execute them. Dangerous commands, protected secret reads, file deletion automation, browser session access, public posting, email sending, payment actions, and unsupported connector actions are blocked or marked as requiring approval. Blocked safety decisions are written to JSONL security logs.

## v0.1 Exclusions

Jarvis v0.1B does not call paid AI APIs, run browser automation, send email, post publicly, process payments, sync to cloud, run a dashboard, run autonomous background repair, run unrestricted repair loops, or implement external account connectors. Controlled Codex execution and bounded post-check repair are limited to approved plans through the official local CLI.
