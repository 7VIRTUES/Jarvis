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
- Implementation report section validation.
- Codex plan creation, listing, reading, canceling, approving, and rejecting.
- Codex command preview flag validation without execution.
- Codex prompt/output path boundary validation.
- Blocked Codex execution action validation.
- Codex diagnostics summaries without prompt content or secrets.
