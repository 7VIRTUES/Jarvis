# Local Response Agents Smoke Evidence Template

Manual evidence only. Not certification.

Use this template to record observations from manually exercising the 11 local response agents. This template does not certify CI, full-suite validation, clean Windows VM validation, LAN token behavior, private-alpha readiness, production readiness, or security.

## Metadata

- Tester:
- Date/time:
- Machine/environment:
- Jarvis commit SHA:
- Jarvis run mode:
- Local URL used:
- Loopback or LAN:
- LAN token behavior tested separately: yes/no

## Do Not Include

- Secrets.
- Tokens.
- Credentials.
- `.env` values.
- Private paths.
- Account identifiers.
- Real email addresses.
- Protected file contents.

## Endpoint Evidence Checklist

### 1. Local Research Agent

Endpoint: `POST /agents/research/local-brief`

- Request sent: yes/no
- Response received: yes/no
- agentId matched: yes/no
- Local-only status/mode present: yes/no
- Safety fields checked: yes/no
- No external/connector behavior observed: yes/no
- Notes:

### 2. File/Data Agent

Endpoint: `POST /agents/files/local-summary`

- Request sent: yes/no
- Response received: yes/no
- agentId matched: yes/no
- Local-only status/mode present: yes/no
- Safety fields checked: yes/no
- No external/connector behavior observed: yes/no
- Notes:

### 3. Local Planning Agent

Endpoint: `POST /agents/planning/local-plan`

- Request sent: yes/no
- Response received: yes/no
- agentId matched: yes/no
- Local-only status/mode present: yes/no
- Safety fields checked: yes/no
- No external/connector behavior observed: yes/no
- Notes:

### 4. Local Drafting Agent

Endpoint: `POST /agents/drafting/local-draft`

- Request sent: yes/no
- Response received: yes/no
- agentId matched: yes/no
- Local-only status/mode present: yes/no
- Safety fields checked: yes/no
- No external/connector behavior observed: yes/no
- Notes:

### 5. Local Review Agent

Endpoint: `POST /agents/review/local-review`

- Request sent: yes/no
- Response received: yes/no
- agentId matched: yes/no
- Local-only status/mode present: yes/no
- Safety fields checked: yes/no
- No external/connector behavior observed: yes/no
- Notes:

### 6. Local Decision Agent

Endpoint: `POST /agents/decision/local-decision`

- Request sent: yes/no
- Response received: yes/no
- agentId matched: yes/no
- Local-only status/mode present: yes/no
- Safety fields checked: yes/no
- No external/connector behavior observed: yes/no
- Notes:

### 7. Local Troubleshooting Agent

Endpoint: `POST /agents/troubleshooting/local-triage`

- Request sent: yes/no
- Response received: yes/no
- agentId matched: yes/no
- Local-only status/mode present: yes/no
- Safety fields checked: yes/no
- No external/connector behavior observed: yes/no
- Notes:

### 8. Local Summarization Agent

Endpoint: `POST /agents/summarization/local-summary`

- Request sent: yes/no
- Response received: yes/no
- agentId matched: yes/no
- Local-only status/mode present: yes/no
- Safety fields checked: yes/no
- No external/connector behavior observed: yes/no
- Notes:

### 9. Local Extraction Agent

Endpoint: `POST /agents/extraction/local-extract`

- Request sent: yes/no
- Response received: yes/no
- agentId matched: yes/no
- Local-only status/mode present: yes/no
- Safety fields checked: yes/no
- No external/connector behavior observed: yes/no
- Notes:

### 10. Local Classification Agent

Endpoint: `POST /agents/classification/local-classify`

- Request sent: yes/no
- Response received: yes/no
- agentId matched: yes/no
- Local-only status/mode present: yes/no
- Safety fields checked: yes/no
- No external/connector behavior observed: yes/no
- Notes:

### 11. Local Transformation Agent

Endpoint: `POST /agents/transformation/local-transform`

- Request sent: yes/no
- Response received: yes/no
- agentId matched: yes/no
- Local-only status/mode present: yes/no
- Safety fields checked: yes/no
- No external/connector behavior observed: yes/no
- Notes:

## Known Limitations Of This Evidence

- Does not prove CI validation.
- Does not prove full-suite validation.
- Does not prove clean Windows VM validation.
- Does not prove LAN token boundary unless separately tested.
- Does not prove private-alpha certification.
- Does not prove private-alpha readiness.
- Does not prove production readiness.
- Does not prove security certification.
