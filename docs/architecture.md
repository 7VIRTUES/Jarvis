# Architecture

Jarvis PC Local v0.1A is a local-only FastAPI service backed by SQLite and append-only JSONL audit logs.

The first v0.1B slice adds workflow orchestration foundations while keeping execution disabled or dry-run only.

The Codex planning slice adds future execution plans, command previews, and approval contracts. It does not spawn Codex or run shell commands.

## Modules

- `app.py` exposes local service endpoints.
- `db.py` initializes SQLite tables for projects, action events, security events, and registry metadata.
- `permissions.py` enforces command and action safety decisions.
- `runtime.py` validates requested actions and logs receipts before any tool execution exists.
- `project_registry.py` stores registered projects inside the allowed workspace root.
- `inspector.py` powers the Coding Agent inspection/report skeleton.
- `registries.py` validates agent, tool, and connector manifests.
- `tasks.py` stores local tasks, dry-run planning state, and project write locks.
- `events.py` stores auditable workflow events.
- `approvals.py` stores approval requests and resolution history.
- `risk.py` validates task plans against default risk budgets.
- `diagnostics.py` exports local diagnostic summaries without secret values.
- `reports.py` validates required implementation report sections.
- `codex_plans.py` creates validated Codex future-run plans, prompt previews, command previews, approval records, and plan status transitions.

## Data

Runtime state is stored under `data/jarvis/`, which is gitignored. No secrets are stored. SQLite now includes task, event, approval, action receipt, project lock, and Codex plan tables.

## Project Locks

Write-capable tasks acquire a per-project lock. Locks release when a task reaches `succeeded`, `failed`, `blocked`, or `canceled`. Tasks waiting for approval keep their lock; the current stale-lock recovery path is cancellation, which releases the lock.
