# Architecture

Jarvis PC Local v0.1A is a local-only FastAPI service backed by SQLite and append-only JSONL audit logs.

## Modules

- `app.py` exposes local service endpoints.
- `db.py` initializes SQLite tables for projects, action events, security events, and registry metadata.
- `permissions.py` enforces command and action safety decisions.
- `runtime.py` validates requested actions and logs receipts before any tool execution exists.
- `project_registry.py` stores registered projects inside the allowed workspace root.
- `inspector.py` powers the Coding Agent inspection/report skeleton.
- `registries.py` validates agent, tool, and connector manifests.

## Data

Runtime state is stored under `data/jarvis/`, which is gitignored. No secrets are stored.

