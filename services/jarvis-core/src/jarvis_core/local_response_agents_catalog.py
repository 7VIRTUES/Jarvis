from __future__ import annotations

from copy import deepcopy
from typing import Any


LOCAL_RESPONSE_AGENTS_INDEX: list[dict[str, Any]] = [
    {
        "name": "Local Research Agent",
        "endpoint": "POST /agents/research/local-brief",
        "status": "implemented_local_only",
        "mode": "local_only_user_provided_notes",
        "docsLink": "/docs/local-research-agent.md",
        "responseMode": "response_only",
        "safetyNotes": [
            "Uses user-provided notes only.",
            "No browsing, paid APIs, connectors, account access, or file mutation.",
        ],
        "exampleRequestBody": {
            "topic": "Local alpha reviewer notes",
            "notes": "Reviewers need a concise local-only brief. Avoid external services and validation claims.",
            "sourceTitles": ["Reviewer notes"],
            "questions": ["What should reviewers focus on?"],
            "outputType": "brief",
        },
    },
    {
        "name": "File/Data Agent",
        "endpoint": "POST /agents/files/local-summary",
        "status": "implemented_local_only",
        "mode": "local_registered_project_metadata_only",
        "docsLink": "/docs/file-data-agent.md",
        "responseMode": "metadata_only",
        "safetyNotes": [
            "Summarizes registered-project metadata only.",
            "Requires a registered project and does not accept raw arbitrary local paths.",
            "No arbitrary path scanning, protected-content reads, uploads, command execution, or mutation.",
        ],
        "exampleRequestBody": {"projectName": "Jarvis"},
    },
    {
        "name": "Local Planning Agent",
        "endpoint": "POST /agents/planning/local-plan",
        "status": "implemented_local_only",
        "mode": "response_only_user_provided_planning",
        "docsLink": "/docs/local-planning-agent.md",
        "responseMode": "response_only",
        "safetyNotes": [
            "Uses user-provided planning inputs only.",
            "No persistent tasks, reminders, calendar/email items, files, database records, or external calls.",
        ],
        "exampleRequestBody": {
            "goal": "Prepare a local manual smoke checklist",
            "contextNotes": "The checklist should exercise response-only agents without claiming certification.",
            "constraints": ["No external services", "No task creation"],
            "resources": ["Existing local docs"],
            "blockers": ["Needs human review"],
            "timeframe": "One local session",
            "desiredOutputType": "checklist",
        },
    },
    {
        "name": "Local Drafting Agent",
        "endpoint": "POST /agents/drafting/local-draft",
        "status": "implemented_local_only",
        "mode": "response_only_user_provided_drafting",
        "docsLink": "/docs/local-drafting-agent.md",
        "responseMode": "response_only",
        "safetyNotes": [
            "Uses user-provided drafting inputs only.",
            "No draft persistence, email sending, posting, account access, file writes, or connectors.",
        ],
        "exampleRequestBody": {
            "purpose": "Draft a note for local reviewers",
            "audience": "Local manual testers",
            "notes": "Ask reviewers to try the local smoke examples and report confusing wording.",
            "tone": "clear",
            "format": "message",
            "constraints": ["No hype", "No certification claims"],
            "mustInclude": ["manual local checks only"],
            "mustAvoid": ["guaranteed"],
        },
    },
    {
        "name": "Local Review Agent",
        "endpoint": "POST /agents/review/local-review",
        "status": "implemented_local_only",
        "mode": "response_only_user_provided_review",
        "docsLink": "/docs/local-review-agent.md",
        "responseMode": "response_only",
        "safetyNotes": [
            "Uses user-provided review content only.",
            "No fact verification, repo inspection, tests, persistence, file access, or connectors.",
        ],
        "exampleRequestBody": {
            "subject": "Manual smoke runbook wording",
            "content": "The runbook should be clear that checks are local and manual. It should not claim CI, clean VM validation, or certification.",
            "reviewType": "safety",
            "audience": "Local maintainers",
            "criteria": ["Clear scope", "No validation overclaims"],
            "constraints": ["No external verification claims"],
            "severity": "balanced",
        },
    },
    {
        "name": "Local Decision Agent",
        "endpoint": "POST /agents/decision/local-decision",
        "status": "implemented_local_only",
        "mode": "response_only_user_provided_decision_support",
        "docsLink": "/docs/local-decision-agent.md",
        "responseMode": "response_only",
        "safetyNotes": [
            "Uses user-provided decision inputs only.",
            "No professional validation, purchases, sending, posting, persistence, file access, or external calls.",
        ],
        "exampleRequestBody": {
            "decision": "Choose a manual smoke check format",
            "options": ["Short checklist", "Long worksheet"],
            "criteria": ["Easy to repeat", "Low risk of overclaiming"],
            "constraints": ["No automation", "No external services"],
            "priorities": ["Clarity", "Safety"],
            "contextNotes": "The result should help local testers without creating persistent decisions.",
            "decisionStyle": "safest",
        },
    },
    {
        "name": "Local Troubleshooting Agent",
        "endpoint": "POST /agents/troubleshooting/local-triage",
        "status": "implemented_local_only",
        "mode": "response_only_user_provided_troubleshooting",
        "docsLink": "/docs/local-troubleshooting-agent.md",
        "responseMode": "response_only",
        "safetyNotes": [
            "Uses user-provided troubleshooting inputs only.",
            "No command execution, file/log reads, repo inspection, repair actions, downloads, uploads, or mutation.",
        ],
        "exampleRequestBody": {
            "problem": "A manual smoke response looks incomplete",
            "symptoms": ["Expected safety fields are missing from the response"],
            "errorMessages": ["No error message was shown"],
            "environmentNotes": "Local Jarvis Core manual smoke session on loopback.",
            "attemptedFixes": ["Refreshed the local API client"],
            "constraints": ["No command execution", "No file inspection"],
            "urgency": "normal",
            "troubleshootingType": "workflow_issue",
        },
    },
    {
        "name": "Local Summarization Agent",
        "endpoint": "POST /agents/summarization/local-summary",
        "status": "implemented_local_only",
        "mode": "response_only_user_provided_summarization",
        "docsLink": "/docs/local-summarization-agent.md",
        "responseMode": "response_only",
        "safetyNotes": [
            "Uses user-provided text only.",
            "No file reads, document retrieval, source/citation verification, persistence, repo inspection, or tests.",
        ],
        "exampleRequestBody": {
            "title": "Manual smoke notes",
            "content": "The local response agents returned structured outputs. Reviewers should check agent IDs, local-only status, and safety flags.",
            "summaryType": "bullets",
            "audience": "Local maintainers",
            "detailLevel": "medium",
            "focusAreas": ["safety fields", "manual checks"],
            "mustPreserve": ["local-only status"],
            "mustAvoid": ["certified"],
        },
    },
    {
        "name": "Local Extraction Agent",
        "endpoint": "POST /agents/extraction/local-extract",
        "status": "implemented_local_only",
        "mode": "response_only_user_provided_extraction",
        "docsLink": "/docs/local-extraction-agent.md",
        "responseMode": "response_only",
        "safetyNotes": [
            "Uses user-provided text only.",
            "No file reads, document retrieval, source/citation verification, task creation, persistence, repo inspection, or tests.",
        ],
        "exampleRequestBody": {
            "title": "Manual smoke findings",
            "content": "Agent ID should match. Status should be local-only. Safety flags should show no connectors, no persistence, and no mutation.",
            "extractionType": "requirements",
            "focusAreas": ["response checks", "safety boundaries"],
            "mustCapture": ["no connectors"],
            "mustIgnore": ["certified"],
            "detailLevel": "medium",
        },
    },
    {
        "name": "Local Classification Agent",
        "endpoint": "POST /agents/classification/local-classify",
        "status": "implemented_local_only",
        "mode": "response_only_user_provided_classification",
        "docsLink": "/docs/local-classification-agent.md",
        "responseMode": "response_only",
        "safetyNotes": [
            "Uses user-provided text and items only.",
            "No file reads, document retrieval, source/citation verification, task creation, agent calls, persistence, or certification.",
        ],
        "exampleRequestBody": {
            "title": "Manual smoke triage",
            "content": "README link updates are documentation work. Safety wording review is high priority.",
            "items": ["Check README link", "Review safety wording"],
            "classificationType": "priority",
            "labels": ["docs", "safety"],
            "criteria": ["manual review impact"],
            "constraints": ["no task creation"],
            "detailLevel": "medium",
        },
    },
    {
        "name": "Local Transformation Agent",
        "endpoint": "POST /agents/transformation/local-transform",
        "status": "implemented_local_only",
        "mode": "response_only_user_provided_transformation",
        "docsLink": "/docs/local-transformation-agent.md",
        "responseMode": "response_only",
        "safetyNotes": [
            "Uses user-provided text and items only.",
            "No file reads/writes, document/spreadsheet/deck/export creation, persistence, repo inspection, tests, or connectors.",
        ],
        "exampleRequestBody": {
            "title": "Manual smoke notes",
            "content": "Check agent ID. Confirm local-only status. Review safety flags.",
            "items": ["Check agent ID", "Confirm local-only status", "Review safety flags"],
            "targetFormat": "checklist",
            "audience": "Local maintainers",
            "constraints": ["No file export"],
            "mustPreserve": ["local-only status"],
            "mustAvoid": ["certified"],
            "detailLevel": "medium",
        },
    },
]

LOCAL_RESPONSE_AGENTS_GLOBAL_BOUNDARIES = [
    "No paid APIs.",
    "No connectors.",
    "No OAuth or account access.",
    "No browser automation.",
    "No cloud sync.",
    "No file mutation except existing Coding Agent workflows.",
    "No email sending, posting, or purchases.",
    "No task persistence for response-only agents.",
    "No claims of clean Windows VM validation, CI validation, private-alpha certification, production readiness, or security certification.",
]


def local_response_agents_index() -> list[dict[str, Any]]:
    return deepcopy(LOCAL_RESPONSE_AGENTS_INDEX)


def local_response_agents_global_boundaries() -> list[str]:
    return list(LOCAL_RESPONSE_AGENTS_GLOBAL_BOUNDARIES)


def local_response_agents_summary() -> dict[str, Any]:
    agents = local_response_agents_index()
    return {
        "status": "read_only_index",
        "agentCount": len(agents),
        "agents": agents,
        "globalBoundaries": local_response_agents_global_boundaries(),
        "docsLink": "/docs/local-response-agents-index.md",
        "addsAgents": False,
        "addsEndpoint": False,
        "mutation": False,
        "connectorExecution": False,
        "paidApis": False,
        "oauth": False,
        "accountAccess": False,
        "browserAutomation": False,
        "cloudSync": False,
        "emailSendingPostingPurchases": False,
        "taskPersistenceForResponseOnlyAgents": False,
        "certificationClaims": False,
    }
