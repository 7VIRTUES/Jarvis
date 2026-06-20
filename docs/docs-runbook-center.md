# Docs/Runbook Center

The Docs/Runbook Center is a local-only read surface for approved Jarvis Markdown documentation.

## What It Does

- Indexes `README.md`.
- Indexes direct `docs/*.md` files.
- Extracts safe metadata: doc id, filename, title, category, size, modified time, and summary.
- Returns bounded redacted Markdown detail.
- Redacts secret-like values and private-path shapes.

## What It Does Not Do

- Does not scan arbitrary folders or docs subdirectories.
- Does not edit, delete, upload, share, publish, fix, run, or certify docs.
- Does not execute commands or call external services.

## Guarded Endpoints

- `GET /docs/index`
- `GET /docs/{doc_id}`
- `GET /docs/{doc_id}/metadata`

All endpoints use the dashboard/LAN access guard. `doc_id` must be a single Markdown filename.

## Dashboard Surface

The dashboard shows total docs, counts by category, recent docs, safe doc links, and a refresh-only control.
