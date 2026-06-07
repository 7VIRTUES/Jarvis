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
