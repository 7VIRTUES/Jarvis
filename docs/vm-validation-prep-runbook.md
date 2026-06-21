# Clean Windows VM Validation Prep Runbook

Use this runbook as manual preparation guidance before clean Windows VM validation.

## Manual Review

1. Prepare a clean Windows VM through your normal local VM workflow.
2. Confirm Git and Python are available in the VM through your own manual process.
3. Clone the Jarvis repo and confirm the branch under review.
4. Prepare the Python virtual environment from the project documentation.
5. Execute validation yourself and record results through the existing local validation evidence workflow.
6. If Codex is available, keep it inside approved local workflow boundaries.
7. If Codex is missing, record the blocker manually instead of attempting automated setup from Jarvis.
8. Confirm dashboard loopback access and LAN denial without a token.
9. Confirm future connector placeholders remain disabled.
10. Review backup/restore readiness before relying on VM evidence.

## Boundaries

Jarvis does not run commands, prepare software, control VM software, detect VM state, create installer artifacts, publish releases, or certify validation readiness from this center.
