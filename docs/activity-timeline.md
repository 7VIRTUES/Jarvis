# Recent Activity / Audit Trail Center

The Recent Activity / Audit Trail Center is a local-only, read-only dashboard/API surface for recent Jarvis activity metadata.

It summarizes recent tasks, events, approvals, security notes, and action receipts without opening raw log files or exposing raw event payloads.

## Boundaries

- Reads structured local SQLite metadata only.
- Does not read raw log files.
- Does not expose raw command output, stdout, stderr, protected file contents, or event payloads.
- Redacts secret-looking values and private local paths from summaries.
- Bounds results to recent items only.
- Does not approve, reject, retry, rerun, mutate, upload, share, publish, or certify anything.

## Endpoints

- `GET /activity/timeline`
- `GET /activity/timeline/{item_id}`

Both endpoints use the dashboard LAN access guard.
