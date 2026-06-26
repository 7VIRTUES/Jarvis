# Local Research Agent

The Local Research Agent is implemented as a local-only Jarvis agent for turning explicit user-provided notes into a structured research brief.

## Scope

- Uses only notes provided in the request.
- Does not browse the web.
- Does not fetch sources.
- Does not verify sources.
- Does not fabricate citations.
- Does not use paid APIs.
- Does not use connectors.
- Does not access accounts.
- Does not mutate files.
- Does not read local files.

## Endpoint

`POST /agents/research/local-brief`

The endpoint accepts a topic, user-provided notes, optional source titles, optional questions, and an optional output type.

Supported output types:

- `brief`
- `outline`
- `comparison`
- `reading_plan`

## Limitations

The output is based only on user-provided notes. Source titles are treated as unverified labels, not as verified citations or evidence.

This is not a full external Research Agent yet. It does not connect to external services, paid AI APIs, OAuth accounts, source databases, browser automation, email, posting, or future connectors.

## Related Docs

- [Local Response Agents Index](local-response-agents-index.md)
- [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md)
- [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)

These read-only docs and manual evidence aids do not prove validation or certification.
