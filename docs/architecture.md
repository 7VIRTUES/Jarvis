# Architecture

Jarvis PC Local v0.1A is a local-only FastAPI service backed by SQLite and append-only JSONL audit logs.

The first v0.1B slice adds workflow orchestration foundations while keeping execution disabled or dry-run only.

The Codex planning slice adds future execution plans, command previews, and approval contracts. It does not spawn Codex or run shell commands.

The controlled execution slice can run only an approved Codex plan through the official local Codex CLI using fixed argv, `shell=False`, a registered project path, and the `workspace-write` sandbox.

The first v0.1C slice adds a read-only local dashboard surface and report visibility APIs. It does not add write controls, remote access, LAN pairing, token protection, desktop shell packaging, or connector execution.

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
- `dashboard.py` builds read-only dashboard summaries, connector placeholder summaries, and path-safe Markdown report listing/detail responses.
- `reports.py` validates required implementation report sections.
- `codex_plans.py` creates validated Codex future-run plans, prompt previews, command previews, approval records, and plan status transitions.
- `codex_execution.py` validates approved plans, prepares bounded prompt files, runs the official Codex CLI only, stores execution summaries, and emits receipts/events.

## Data

Runtime state is stored under `data/jarvis/`, which is gitignored. No secrets are stored. SQLite now includes task, event, approval, action receipt, project lock, Codex plan, and Codex execution tables.

Dashboard report detail reads only Markdown files directly under `data/jarvis/reports` after validating the requested report id is a contained file name.

## Project Locks

Write-capable tasks acquire a per-project lock. Locks release when a task reaches `succeeded`, `failed`, `blocked`, or `canceled`. Tasks waiting for approval keep their lock; the current stale-lock recovery path is cancellation, which releases the lock.
