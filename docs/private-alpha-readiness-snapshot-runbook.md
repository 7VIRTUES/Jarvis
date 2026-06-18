# Private-Alpha Readiness Snapshot Runbook

Use this runbook to create and interpret a local readiness snapshot before any future private-alpha packaging plan.

## Before VM Validation

1. Open the local Jarvis dashboard.
2. Review the Private-Alpha Readiness Snapshot section.
3. Confirm the verdict, blockers, warnings, and validation evidence status.
4. Use **Generate local readiness report** to create a local Markdown report.
5. Treat `needs_evidence` as expected if clean Windows VM validation has not been recorded yet.

The snapshot helps identify missing evidence. It does not replace the clean Windows VM validation runbook.

## After VM Validation Evidence Is Recorded

1. Record manual VM validation results through the Validation Agent workflow.
2. Generate the local validation report.
3. Generate a new private-alpha readiness snapshot report.
4. Compare the latest snapshot verdict, blockers, warnings, and recommended next actions.

Never treat the snapshot as production approval. It is local planning evidence only.

## Interpreting Blockers And Warnings

- Blockers mean a safety or readiness boundary needs attention before packaging planning continues.
- Warnings mean a human should review missing evidence, missing reports, or ambiguous readiness metadata.
- Missing validation evidence means the VM runbook still needs real manual evidence.
- Missing public-readiness docs means repository readiness is incomplete.

## Relationship To Future Packaging Planning

The snapshot can support a future ChatGPT/user planning decision about private-alpha packaging. It does not authorize or perform packaging work by itself.

Future real packaging, production Tauri, installer work, code signing, release automation, pairing, QR/mobile pairing, and production first-run setup still require separate planning and approval.

## Limitations

- The snapshot reads safe local metadata and existing local reports only.
- It does not run tests, inspect GitHub, or call external services.
- It does not scan the whole PC.
- It does not read protected secret file contents.
- It does not certify security or production readiness.
