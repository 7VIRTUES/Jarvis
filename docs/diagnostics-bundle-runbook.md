# Diagnostics Bundle Runbook

Use a local redacted diagnostics bundle when troubleshooting Jarvis during local development, clean Windows VM validation, private-alpha readiness review, or when comparing recent local evidence across validation, readiness snapshots, and security review reports.

## When To Generate

- Before reviewing a private-alpha readiness question with local evidence.
- After a manual validation run is recorded.
- After a security/safety review report is generated.
- When a dashboard, LAN protection, connector boundary, or report visibility issue needs a compact local summary.

## How To Generate

- Open the guarded local dashboard and use `Generate local diagnostics report`.
- Or call `POST /diagnostics/bundle/report` through the local service with valid dashboard/LAN access.

The generated files remain local under the Jarvis reports directory.

## Review Before Sharing

Review any bundle content before sharing it outside the machine. Do not paste secrets, `.env` contents, private keys, token values, raw command output, raw logs, database files, browser/session stores, or private local paths into an issue, chat, email, or public post.

The bundle is redacted, but redaction is a safety layer, not permission to share blindly.

## Interpreting Warnings

Warnings identify local evidence that needs human review, such as missing or incomplete validation evidence, readiness snapshots that still need evidence, security review metadata that needs attention, or connector placeholders that appear unexpectedly enabled.

Warnings are not automated fixes and are not certification results.

## Relationship To VM Validation

The diagnostics bundle can summarize VM validation metadata and latest report metadata. It does not perform VM validation, control VirtualBox, run pytest, install dependencies, or decide readiness. Manual clean Windows VM validation remains a separate evidence workflow.

## Relationship To Private-Alpha Readiness

The bundle can collect local metadata that helps a human review private-alpha readiness. It does not create installer artifacts, build production Tauri, create release artifacts, publish releases, push to GitHub, upload diagnostics, or certify production/security readiness.

## Limitations

- Local report only.
- No uploads or external services.
- No command execution.
- No protected secret file reads.
- No full raw logs or raw stdout/stderr dumps.
- No complete security audit.
- No Git history review.
- No credential rotation.
- No production or security certification.
