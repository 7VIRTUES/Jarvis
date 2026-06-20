# Docs/Runbook Center Runbook

Use the Docs/Runbook Center when you need to locate local Jarvis docs and runbooks without browsing arbitrary folders.

## Refresh Docs Index

1. Open the guarded local dashboard.
2. Find the Docs/Runbook Center section.
3. Use `Refresh docs index`.
4. Review category counts and recent docs.

The refresh reads bounded local Markdown content only from `README.md` and direct `docs/*.md` files.

## Review A Doc

Use a safe doc link to inspect bounded redacted Markdown detail. If a doc is oversized or unsafe to resolve, the center marks it unreadable or blocks access.

## Boundaries

- No subdirectory scanning.
- No doc mutation.
- No upload, share, publish, readiness certification, command execution, or external service call.
