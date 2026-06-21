# Dashboard Surface Health Center

The Dashboard Surface Health Center is a local-only, read-only dashboard/API summary for dashboard wiring.

It checks existing FastAPI route metadata, the dashboard summary snapshot, and the dashboard HTML string for required local surfaces, guarded endpoints, safety notes, and dashboard documentation links.

## Boundaries

- Does not call external services.
- Does not execute commands.
- Does not mutate routes, reports, docs, manifests, settings, or connector state.
- Does not upload, send, share, publish, or certify dashboard readiness.
- Reports warnings only when expected dashboard sections, endpoints, docs links, summary keys, or safety notes are missing.

## Endpoints

- `GET /dashboard/surface-health`
- `GET /dashboard/surface-health/{surface_id}`

Both endpoints use the dashboard LAN access guard.
