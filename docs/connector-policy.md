# Connector Policy

All non-coding connectors are placeholders in v0.1A. Placeholder manifests must set:

- `implemented=false`
- `defaultEnabled=false`
- `readinessLevel=placeholder_only`
- `approvalRequired=true`
- `tokenStorage=not_implemented`
- `dataRetention=none`

## Cost Modes

Valid connector cost modes are:

- `local_free`
- `official_free_quota`
- `bring_your_own_account`
- `paid_provider_required`
- `disabled`

Jarvis v0.1A does not authenticate external accounts or store connector tokens.

