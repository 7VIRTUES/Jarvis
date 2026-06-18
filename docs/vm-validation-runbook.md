# Clean Windows VM Validation Runbook

This runbook describes manual clean Windows VM validation for Jarvis PC Local. The Validation Agent can record evidence for these steps, but it does not run commands, control VirtualBox, install dependencies, package installers, or automate browser/VM behavior.

## Manual Steps

1. Confirm VM environment.
   Record Windows version, CPU count, RAM, disk size/free space, and whether VirtualBox Guest Additions are installed. Guest Additions are optional.

2. Confirm prerequisites.
   Record Git version, Python version, pip version, and whether Codex CLI is present or explicitly missing.

3. Clone repo.
   Clone `7VIRTUES/Jarvis`, confirm branch `main`, and confirm the working tree is clean.

4. Python setup.
   Create a virtual environment and install documented requirements.

5. Unit/integration tests.
   Run pytest manually. Record the current expected full-suite result for the validation date instead of treating it as permanent truth.

6. Service startup.
   Start the local service manually with the documented uvicorn command and verify `/health` works.

7. Dashboard loopback.
   Open the local dashboard from loopback and verify dashboard summary endpoints return safe status.

8. Project profile/security review dashboard.
   Verify project profile endpoint behavior and registered-project security review behavior.

9. LAN token boundary.
   Verify loopback works without a token, non-loopback access is denied without a token, non-loopback access is allowed with the configured token, and setup pages remain loopback-only.

10. Future connector boundary.
    Confirm future connectors remain disabled placeholders with `implemented=false` and `defaultEnabled=false`.

11. Public repo safety.
    Confirm no paid APIs, browser automation, production installer claims, telemetry, public posting, or production release controls are present.

12. Backup/readiness.
    Confirm the project can be backed up externally and generate a local validation report.

## Recording A Run Through The API

Create a run:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/validation/runs -ContentType application/json -Body '{"runbookId":"clean_windows_vm_validation","targetEnvironment":"Clean Windows VM manual validation"}'
```

Record a step result:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/validation/runs/<run_id>/steps/confirm_vm_environment -ContentType application/json -Body '{"status":"passed","notes":"Windows version and VM resources recorded","evidence":"Manual summary only"}'
```

Complete the run:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/validation/runs/<run_id>/complete
```

Generate a local report:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/validation/runs/<run_id>/report
```

For LAN access, use the configured dashboard token header. Do not put tokens in URLs.

## Evidence Guidance

Use concise manual summaries, versions, pass/fail observations, and safe endpoint statuses. Do not paste raw `.env` files, private keys, token values, credential dumps, protected file contents, or long sensitive logs.

## Limitations

The Validation Agent records validation evidence only. It does not certify Jarvis, create an installer, build production Tauri, automate VirtualBox, run tests, install dependencies, push to GitHub, merge, delete files, or call external services.
