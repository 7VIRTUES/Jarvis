# Local Security/Safety Agent

The Local Security/Safety Agent turns user-provided safety and security situations, assets, concerns, current controls, constraints, environment notes, and incident notes into structured local review suggestions and checklists.

It is local-only, response-only, and manual-input-only.

## Purpose

- Help organize user-provided safety and security notes using only the request body.
- Return manual review aids for risk review, privacy checklists, account hygiene, device safety, phishing/scam notes, travel or personal-safety preparation, and non-executing incident preparation.
- Keep all output non-persistent and non-executing.

## Scope

- Does not inspect devices, accounts, files, repositories, networks, logs, secrets, browsers, cookies, password managers, tokens, emails, cloud services, or external systems.
- Does not run scans, commands, scripts, downloads, malware checks, penetration tests, exploit checks, automated remediation, account recovery, sending, posting, purchases, or connector actions.
- Does not provide hacking, exploit, evasion, malware, phishing, credential-theft, stealth, bypass, or unauthorized-access help.
- Does not claim forensic validation, compliance certification, legal validation, incident resolution, account recovery, vulnerability confirmation, system security, security certification, or readiness.

## Endpoint

`POST /agents/security-safety/local-review`

## Request Body Example

```json
{
  "reviewName": "Local Account Hygiene Review",
  "situation": "Prepare a manual safety review for a personal account and shared device after a suspicious message.",
  "assetsOrAccounts": ["Personal email account", "Shared laptop"],
  "concerns": ["Suspicious message", "Unclear recovery settings"],
  "currentControls": ["Two-step sign-in is believed to be enabled"],
  "constraints": ["No account access from Jarvis", "No scans or downloads"],
  "riskTolerance": "Cautious",
  "environmentNotes": "Use only user-provided notes for a local checklist.",
  "incidentNotes": "No active emergency reported; prepare notes for manual review.",
  "desiredOutputType": "safety_brief"
}
```

## Supported Output Types

- `safety_brief`
- `risk_review`
- `privacy_checklist`
- `account_hygiene_plan`
- `device_safety_checklist`
- `phishing_scam_review`
- `travel_safety_plan`
- `incident_prep_plan`

## Safety Boundaries

- Manual-input only.
- Local-only.
- Response-only.
- Defensive review and checklist support only.
- No scans, commands, account access, file reads, secret reads, browser/cookie access, password-manager access, downloads, remediation, account recovery, email sending, public posting, purchases, database writes, task persistence, mutation, or connector behavior.
- No hacking, exploit, evasion, malware, phishing, credential-theft, stealth, bypass, or unauthorized-access help.
- No forensic validation, legal validation, compliance certification, security certification, incident resolution, vulnerability confirmation, account recovery, system-security, or readiness claims.
- Output is based only on user-provided input.

## Limitations

- Suggestions and checklists are review aids only.
- Emergencies, active threats, compromise, stalking, violence, extortion, financial fraud, or legal exposure require appropriate human, professional, emergency, financial, platform, or legal help.
- The agent does not prove safety, security, forensic status, legal status, compliance, incident resolution, account recovery, vulnerability status, validation, certification, or readiness.

## Related Docs

- [Local Response Agents Index](local-response-agents-index.md)
- [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md)
- [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)

These linked smoke and evidence docs are read-only docs/manual evidence aids and do not prove validation or certification.
