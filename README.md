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

## Run Jarvis Core

```powershell
python -m uvicorn --app-dir services/jarvis-core/src jarvis_core.app:app --reload
```

The service is local-only by design. The `/health` endpoint returns the app name, version, status, and local mode.

## Run Tests

```powershell
python -m pytest
```

## Safety Model

Jarvis v0.1A validates actions before tools execute them. Dangerous commands, protected secret reads, file deletion automation, browser session access, public posting, email sending, payment actions, and unsupported connector actions are blocked or marked as requiring approval. Blocked safety decisions are written to JSONL security logs.

## v0.1 Exclusions

Jarvis v0.1A does not execute Codex, call paid AI APIs, run browser automation, send email, post publicly, process payments, sync to cloud, run a dashboard, manage a task queue, repair code automatically, or implement external account connectors.
