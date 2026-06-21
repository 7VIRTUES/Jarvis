# Backup Readiness Runbook

Use this runbook as a manual pre-flight checklist before future VM/private-alpha work.

## Manual Review

1. Confirm intended repo history is available on GitHub through your normal Git workflow.
2. Confirm the working tree is intentionally clean or that local changes are understood.
3. Review which reports and local data are useful for continuity.
4. Keep protected files excluded, including `.env` variants, private keys, credential material, logs, databases, and local secret stores.
5. If you choose to preserve allowed artifacts offline, use your own trusted local process.
6. Plan a restore test in a safe location before relying on any backup material.

## Boundaries

Jarvis does not create backup material, transfer files, inspect removable media, delete files, read secrets, or certify backup readiness from this center.
