from pathlib import Path


RUNBOOK = Path("docs/local-response-agents-smoke-runbook.md")
README = Path("README.md")
INDEX = Path("docs/local-response-agents-index.md")

EXPECTED_ENDPOINTS = [
    "POST /agents/research/local-brief",
    "POST /agents/files/local-summary",
    "POST /agents/planning/local-plan",
    "POST /agents/drafting/local-draft",
    "POST /agents/review/local-review",
    "POST /agents/decision/local-decision",
    "POST /agents/troubleshooting/local-triage",
    "POST /agents/summarization/local-summary",
    "POST /agents/extraction/local-extract",
    "POST /agents/classification/local-classify",
    "POST /agents/transformation/local-transform",
]

EXPECTED_AGENT_IDS = [
    "local_research_agent",
    "file_data_agent",
    "local_planning_agent",
    "local_drafting_agent",
    "local_review_agent",
    "local_decision_agent",
    "local_troubleshooting_agent",
    "local_summarization_agent",
    "local_extraction_agent",
    "local_classification_agent",
    "local_transformation_agent",
]


def test_smoke_runbook_docs_file_exists():
    assert RUNBOOK.exists()


def test_smoke_runbook_includes_exactly_the_expected_endpoint_strings():
    doc_text = RUNBOOK.read_text(encoding="utf-8")

    assert [endpoint for endpoint in EXPECTED_ENDPOINTS if endpoint in doc_text] == EXPECTED_ENDPOINTS
    assert doc_text.count("POST /agents/") == 11


def test_smoke_runbook_includes_json_examples_for_all_agents():
    doc_text = RUNBOOK.read_text(encoding="utf-8")

    assert doc_text.count("```json") == 11
    for agent_id in EXPECTED_AGENT_IDS:
        assert agent_id in doc_text


def test_smoke_runbook_file_data_requires_registered_project_and_no_raw_paths():
    doc_text = RUNBOOK.read_text(encoding="utf-8")
    lower_doc = doc_text.lower()

    assert "requires a registered project" in lower_doc
    assert "registered `projectname` only" in lower_doc
    assert "does not accept raw arbitrary paths" in lower_doc
    assert '"projectName": "Jarvis"' in doc_text
    assert "C:\\" not in doc_text
    assert "/users/" not in lower_doc


def test_smoke_runbook_includes_global_boundaries():
    lower_doc = RUNBOOK.read_text(encoding="utf-8").lower()

    assert "no paid apis" in lower_doc
    assert "no connectors" in lower_doc
    assert "no oauth or account access" in lower_doc
    assert "no browser automation" in lower_doc
    assert "no cloud sync" in lower_doc
    assert "no sending, posting, or purchases" in lower_doc
    assert "no task persistence for response-only agents" in lower_doc


def test_smoke_runbook_includes_what_this_does_not_prove_items():
    lower_doc = RUNBOOK.read_text(encoding="utf-8").lower()

    assert "what this does not prove" in lower_doc
    assert "does not prove ci validation" in lower_doc
    assert "does not prove full-suite validation" in lower_doc
    assert "does not prove clean windows vm validation" in lower_doc
    assert "does not prove lan token boundary" in lower_doc
    assert "does not prove private-alpha certification" in lower_doc
    assert "does not prove production readiness" in lower_doc


def test_readme_links_smoke_runbook():
    readme_text = README.read_text(encoding="utf-8")

    assert "[Local Response Agents Manual Smoke Runbook](docs/local-response-agents-smoke-runbook.md)" in readme_text


def test_index_page_links_smoke_runbook():
    index_text = INDEX.read_text(encoding="utf-8")

    assert "[Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md)" in index_text


def test_smoke_runbook_avoids_secrets_credentials_and_private_local_paths():
    doc_text = RUNBOOK.read_text(encoding="utf-8")
    lower_doc = doc_text.lower()
    forbidden = [
        ".env",
        "api_key",
        "apikey",
        "secret=",
        "token=",
        "password",
        "credential",
        "bearer ",
        "c:\\users\\",
        "c:/users/",
    ]

    assert all(item not in lower_doc for item in forbidden)
    assert "@" not in doc_text
