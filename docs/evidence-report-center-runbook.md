# Evidence Report Center Runbook

Use the Evidence Report Center when you need to locate local Jarvis evidence reports and inspect safe metadata without opening arbitrary files.

## Refresh The Index

1. Open the local dashboard.
2. Find the Evidence Report Center section.
3. Use `Refresh report index` to reload local report metadata.
4. Review report counts by type and recent reports.

The refresh action reads bounded metadata only. It does not run tests, execute commands, transfer reports, or mutate files.

## Open Safe Detail

Use the safe detail link for a report when you need generated Markdown detail from safe metadata and sanitized summary text. JSON reports return metadata only. If a report is too large or malformed, the center marks it unreadable with a blocked reason.

## What Not To Share

Review any detail before copying it outside the machine. Do not share secrets, `.env` contents, private keys, token values, raw command output, raw logs, database files, browser/session stores, or private local paths.

## Limitations

- The report center indexes only allowed `.md` and `.json` files directly under the Jarvis reports directory.
- It does not scan subdirectories or arbitrary folders.
- It does not claim report correctness, production readiness, or security readiness.
- It does not mutate stale reports, rewrite reports, rotate credentials, review Git history, or transfer evidence.

