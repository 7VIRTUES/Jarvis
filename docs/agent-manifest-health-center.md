# Agent Manifest Health Center

The Agent Manifest Health Center is a local-only metadata checker for Jarvis agent manifests and future connector placeholder manifests.

## What It Does

- Reads JSON manifests under `connectors/agents`.
- Reads JSON manifests under `connectors/placeholders`.
- Returns counts, warnings, and safe per-manifest metadata.
- Checks required manifest fields.
- Checks local implemented agent safety booleans.
- Checks that future connector placeholders remain `implemented=false` and `defaultEnabled=false`.
- Redacts secret-like values if a manifest accidentally contains them.

## What It Does Not Do

- Does not scan arbitrary folders.
- Does not mutate manifests.
- Does not change connector state.
- Does not execute tools.
- Does not call external services.
- Does not upload, send, share, publish, certify, fix, or run manifests.

## Guarded Endpoints

- `GET /agents/manifest-health`
- `GET /agents/manifest-health/{manifest_id}`

Both endpoints use the dashboard/LAN access guard. `manifest_id` must be a single JSON filename from a known manifest directory.

## Dashboard Surface

The dashboard shows total manifests, implemented local agents, disabled placeholders, warning count, and recent or flagged safe manifest metadata. The only control refreshes the local metadata view.
