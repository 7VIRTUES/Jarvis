# Local Troubleshooting Agent

The Local Troubleshooting Agent is implemented as a local-only, response-only troubleshooting triage helper.

## Scope

- Uses only troubleshooting inputs provided in the request.
- Returns a structured local triage response.
- Supports `general`, `pc_issue`, `app_issue`, `build_error`, `workflow_issue`, and `network_issue`.
- Supports `low`, `normal`, and `high` urgency.
- Handles thin input with explicit warnings and limitations.
- Frames safe checks as manual/user-performed checks only.
- Does not inspect files.
- Does not read logs unless excerpts are pasted in the request.
- Does not inspect repositories.
- Does not execute commands, tests, code, downloaded scripts, or repair actions.
- Does not validate fixes, sources, external facts, or build/test results.
- Does not persist tickets or tasks.
- Does not modify settings.
- Does not delete files, wipe disks, disable security tools, delete registry data, force push, hard reset, or make system-wide changes.
- Does not write files or database records.
- Does not download or upload anything.
- Does not call external services.
- Does not use paid APIs.
- Does not use Gmail, calendar, social, connector, OAuth, account access, posting, sending, purchase, or browser automation.

## Endpoint

`POST /agents/troubleshooting/local-triage`

Request body:

```json
{
  "problem": "Build fails after dependency update",
  "symptoms": ["Build stops before packaging"],
  "errorMessages": ["ModuleNotFoundError: No module named example"],
  "environmentNotes": "Windows local dev environment. The error started after updating dependencies.",
  "attemptedFixes": ["Restarted the terminal"],
  "constraints": ["No installs until reviewed"],
  "urgency": "normal",
  "troubleshootingType": "build_error"
}
```

The response includes triage focus, observed signals, likely causes, manual safe checks, next steps, escalation triggers, information needed, avoided actions, warnings, limitations, and explicit safety fields.

## Limitations

This agent only triages user-provided troubleshooting details in the response. It does not execute commands, inspect files, read logs, inspect repositories, validate fixes, run tests, mutate settings, persist tickets, download scripts, upload data, or use external services.
