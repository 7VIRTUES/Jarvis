# Clean Windows VM Validation Prep Center

The Clean Windows VM Validation Prep Center is a local-only, read-only dashboard/API surface for preparing manual clean Windows VM validation.

It shows static checklist metadata only. It does not run commands, prepare software, control VM software, detect VM state, create installer artifacts, publish releases, or claim validation completion.

## Checklist Scope

- Clean Windows VM available
- Git available through manual setup
- Python available through manual setup
- Repo clone step
- Virtual environment setup step
- Pytest validation step
- Codex available and missing scenarios
- Dashboard loopback access
- LAN denied without token
- Future connectors still disabled
- Backup/restore reminder

## Endpoints

- `GET /vm-validation/prep`
- `GET /vm-validation/prep/runbook`

Both endpoints use the dashboard LAN access guard.
