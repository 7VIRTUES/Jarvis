# Backup Readiness Checklist Center

The Backup Readiness Checklist Center is a local-only, read-only dashboard/API surface for manual backup preparation before future VM or private-alpha work.

It shows checklist metadata only. It does not inspect the whole machine, transfer files, create archives, inspect removable media, read secrets, or claim a backup was completed.

## Checklist Scope

- Repo pushed to GitHub
- Clean working tree reviewed
- Reports directory understood
- Local data directory understood
- Protected files excluded
- Manual external-drive backup step
- Restore-test reminder

## Endpoints

- `GET /backup/readiness`
- `GET /backup/readiness/runbook`

Both endpoints use the dashboard LAN access guard.
