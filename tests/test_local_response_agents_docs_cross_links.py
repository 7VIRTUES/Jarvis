from pathlib import Path


AGENT_DOCS = [
    Path("docs/local-research-agent.md"),
    Path("docs/file-data-agent.md"),
    Path("docs/local-planning-agent.md"),
    Path("docs/local-drafting-agent.md"),
    Path("docs/local-review-agent.md"),
    Path("docs/local-decision-agent.md"),
    Path("docs/local-troubleshooting-agent.md"),
    Path("docs/local-summarization-agent.md"),
    Path("docs/local-extraction-agent.md"),
    Path("docs/local-classification-agent.md"),
    Path("docs/local-transformation-agent.md"),
]


def test_all_individual_local_response_agent_docs_exist():
    assert all(path.exists() for path in AGENT_DOCS)


def test_each_agent_doc_links_to_local_response_agents_index():
    for path in AGENT_DOCS:
        doc_text = path.read_text(encoding="utf-8")

        assert "local-response-agents-index.md" in doc_text


def test_each_agent_doc_links_to_manual_smoke_runbook():
    for path in AGENT_DOCS:
        doc_text = path.read_text(encoding="utf-8")

        assert "local-response-agents-smoke-runbook.md" in doc_text


def test_each_agent_doc_links_to_smoke_evidence_template():
    for path in AGENT_DOCS:
        doc_text = path.read_text(encoding="utf-8")

        assert "local-response-agents-smoke-evidence-template.md" in doc_text


def test_each_agent_doc_says_smoke_and_evidence_docs_do_not_prove_validation_or_certification():
    for path in AGENT_DOCS:
        lower_doc = path.read_text(encoding="utf-8").lower()

        assert "manual evidence aids" in lower_doc
        assert "do not prove validation or certification" in lower_doc


def test_agent_docs_do_not_include_private_paths_or_sensitive_examples():
    forbidden = [
        "c:\\users\\",
        "c:/users/",
        ".env",
        "sk-",
        "api_key",
        "apikey",
        "secret=",
        "token=",
        "password:",
        "credential:",
        "credentials:",
    ]

    for path in AGENT_DOCS:
        doc_text = path.read_text(encoding="utf-8")
        lower_doc = doc_text.lower()

        assert all(item not in lower_doc for item in forbidden)
        assert "@" not in doc_text
