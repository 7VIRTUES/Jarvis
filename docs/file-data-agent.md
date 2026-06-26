# File/Data Agent

The File/Data Agent is implemented as a local-only registered-project metadata summarizer.

## Scope

- Accepts a registered `projectName` only.
- Resolves project roots through the local project registry.
- Stays inside the registered project root.
- Skips protected file patterns.
- Skips runtime, dependency, cache, and build directories.
- Reads only bounded metadata.
- Reads bounded previews only for `README.md` and direct `docs/*.md` files when safe.
- Does not accept raw arbitrary paths.
- Does not scan the whole PC.
- Does not read protected file contents.
- Does not mutate files.
- Does not upload anything.
- Does not call external services.
- Does not execute shell commands.
- Does not use connectors, OAuth, account access, browser automation, or paid APIs.

## Endpoint

`POST /agents/files/local-summary`

Request body:

```json
{
  "projectName": "Jarvis"
}
```

The response includes safe local metadata such as file type counts, skipped directory counts, protected-skip counts, safe docs metadata, warnings, limitations, and explicit safety fields.

## Limitations

This agent provides a bounded local metadata summary only. It is not a file search engine, backup tool, sync tool, connector, secret scanner, or full data-ingestion agent.

## Related Docs

- [Local Response Agents Index](local-response-agents-index.md)
- [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md)
- [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)

These read-only docs and manual evidence aids do not prove validation or certification.
