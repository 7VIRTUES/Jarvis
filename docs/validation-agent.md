# Validation Agent

The Validation Agent is a local-only evidence tracking agent for Jarvis PC Local private-alpha readiness. It helps record manual validation runs, especially clean Windows VM validation, without automating the VM or the host.

## What It Does

- Lists built-in manual validation runbooks.
- Creates local validation run records.
- Records manual step results with statuses, redacted notes, and redacted evidence.
- Completes a run by computing a final status from required step results.
- Writes local Markdown validation reports under the Jarvis reports directory.
- Surfaces read-only status through the guarded dashboard summary.

## What It Does Not Do

- No command execution.
- No VirtualBox automation.
- No dependency installation.
- No installer creation.
- No production Tauri work.
- No pairing wizard or QR/mobile pairing.
- No paid AI APIs or external services.
- No OAuth, cloud sync, telemetry, email, public posting, or payment actions.
- No GitHub writes, git push, merge, rebase, reset hard, or force push.
- No file deletion.
- No protected secret file content reads.

## Statuses

Validation runs use:

- `not_started`
- `in_progress`
- `passed`
- `failed`
- `blocked`
- `canceled`

Step results use:

- `not_started`
- `passed`
- `failed`
- `blocked`
- `skipped`

Completing a run marks it `failed` when any required step failed, `blocked` when a required step is blocked or incomplete, and `passed` when all required steps passed or were intentionally skipped.

## Redaction

Notes and evidence are redacted before storage and report generation. Likely token, password, API key, bearer token, GitHub token, OpenAI-style token, `.env`-like, and private-key content is replaced with redacted placeholders.

Do not paste raw `.env` files, private keys, full token values, credential dumps, or long sensitive logs into validation evidence.

## API Endpoints

All endpoints use the dashboard/LAN guard. Loopback access works without a token. Non-loopback access requires the configured LAN dashboard token.

- `GET /validation/runbooks`
- `GET /validation/runbooks/{runbook_id}`
- `POST /validation/runs`
- `GET /validation/runs`
- `GET /validation/runs/{run_id}`
- `POST /validation/runs/{run_id}/steps/{step_id}`
- `POST /validation/runs/{run_id}/complete`
- `POST /validation/runs/{run_id}/report`

Example create-run body:

```json
{
  "runbookId": "clean_windows_vm_validation",
  "targetEnvironment": "Clean Windows 11 VM, 4 CPU, 8 GB RAM"
}
```

Example step update body:

```json
{
  "status": "passed",
  "notes": "pytest completed with the expected result for this validation date",
  "evidence": "Manual summary only; no secret values included"
}
```

## Dashboard Visibility

The dashboard summary includes Validation Agent status, available runbook count, recent runs, last run status, and endpoint references. The dashboard does not expose controls that claim to run VM checks, install dependencies, create installers, or automate tests.

## Reports

Validation reports include run summary, runbook, target environment, verdict/status, step results, failed or blocked steps, evidence notes, safety boundaries, next actions, and a limitation note.

Reports are local validation evidence only. They are not certification, warranty, or production-readiness approval.
