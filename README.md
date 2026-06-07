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

## Run Tests

```powershell
python -m pytest
```

## Safety Model

Jarvis validates actions before tools execute them. Dangerous commands, protected secret reads, file deletion automation, browser session access, public posting, email sending, payment actions, and unsupported connector actions are blocked or marked as requiring approval. Blocked safety decisions are written to JSONL security logs.

## v0.1 Exclusions

Jarvis v0.1B still does not execute Codex, call paid AI APIs, run browser automation, send email, post publicly, process payments, sync to cloud, run a dashboard, repair code automatically, or implement external account connectors. Codex approval marks a plan as approved for future execution only.
