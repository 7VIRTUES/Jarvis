# Test Plan

Run:

```powershell
python -m pytest
```

Tests cover:

- Permission engine allow/block behavior.
- Protected path detection.
- Project registry path validation.
- Package script detection and check planning.
- Connector cost mode and placeholder validation.
- Agent and tool manifest validation.
- Report section validation.
- Blocked action security logging.
- Task creation, listing, reading, and canceling.
- Event creation and task event queries.
- Approval request, approve, and reject flows.
- Approval rejection for hard-blocked actions.
- Project write lock behavior.
- Dry-run receipts without execution.
- Risk budget validation.
- Diagnostic export without secret values.
- Implementation report section validation, including post-Codex review findings, safe check results, and repair attempts/results.
- Codex plan creation, listing, reading, canceling, approving, and rejecting.
- Codex command preview flag validation without execution.
- Codex prompt/output path boundary validation.
- Blocked Codex execution action validation.
- Codex diagnostics summaries without prompt content or secrets.
- Controlled Codex execution blocked states.
- Mocked successful Codex execution with fixed argv and `shell=False`.
- Execution receipts, events, run limits, lock release, and diagnostics summaries.
- Post-Codex diff review for changed-file budgets, diff-line budgets, protected-file path changes, and dependency/package-file changes.
- Safe check planning from detected package scripts only, including preferred ordering and empty-plan reasons.
- Controlled Codex flow stopping before checks when post-execution review requires user review.
- Safe check execution receipts, stored results, ordered execution, skipped no-script plans, blocked unsafe plans, output redaction, and stop-on-failure behavior.
- Controlled repair loop attempts, max-attempt and max-Codex-run limits, repeated failure stops, post-repair review stops, repair prompt context, and stored repair results.
- Dashboard summary status, safety summary, connector placeholder visibility, report listing, report detail, report missing responses, report traversal rejection, absolute path rejection, active task/stop task dashboard markup, desktop shell/Tauri placeholder markup, first-run/setup placeholder markup, disabled stop control when no task is active, and absence of working unsupported dashboard controls.
- Settings/status summary read-only fields, disabled paid AI/browser automation flags, disabled external connector flags, future LAN pairing/installer status, desktop shell placeholder-only status, first-run wizard placeholder-only status, stop-task task-record-only status, settings/status dashboard markup, and absence of save/edit controls.
- LAN dashboard/API token protection for loopback allowance, non-loopback denial without configured token, too-short token rejection, missing/wrong token rejection, accepted dashboard header token, accepted bearer token, query-string token rejection, constant-time comparison helper use, protected route dependencies, and safe status metadata that excludes token values.
- Loopback-only LAN setup status/page access, non-loopback setup denial even with a token, safe setup status fields, accepted header names, query-string/cookie rejection, pairing/QR/mobile future status, token non-exposure, no token input/write controls, and dashboard link to local setup guidance.
- Stop-task status metadata, active Jarvis task listing, active task stop behavior, task cancellation event emission, project lock release, unknown task rejection, non-active task rejection, LAN guard dependencies for task endpoints, and absence of PID/process-name/command/process-kill routes.
- Desktop shell placeholder metadata, Tauri not production-implemented status, installer packaging not implemented status, disabled auto-updater and telemetry status, placeholder directory reporting, and absence of fake launch/install/update controls.
- First-run placeholder metadata, no setup persistence, no config-file writes, no token generation or persistence, no account setup or OAuth, cloud sync disabled, telemetry/updater disabled, loopback-only setup page/status access, no token exposure, informational checklist, and absence of fake setup controls.
