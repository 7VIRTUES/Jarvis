# Clean Windows VM Validation Runbook Pack

The Validation Agent includes additional manual runbook templates for clean Windows VM validation evidence.

These runbooks are manual evidence templates only. They do not run commands, prepare software, control or detect VM software, create artifacts, contact external services, upload/share evidence, or certify readiness.

## Runbooks

- `clean_vm_core_service_smoke`
- `clean_vm_dashboard_loopback_smoke`
- `clean_vm_lan_guard_smoke`
- `clean_vm_codex_available_scenario`
- `clean_vm_codex_missing_scenario`
- `clean_vm_future_connectors_disabled`
- `clean_vm_backup_restore_reminder`

Each template includes ordered manual steps, expected evidence fields, and pass/fail/warning guidance in the step expected result text.

Use the existing Validation Agent endpoints and dashboard workflow to inspect templates, create manual validation runs, record step notes/evidence, and generate local reports.
