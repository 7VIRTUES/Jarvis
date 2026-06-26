from pathlib import Path


CLOSEOUT = Path("docs/local-response-agents-closeout-status.md")
README = Path("README.md")
INDEX = Path("docs/local-response-agents-index.md")

EXPECTED_AGENTS = [
    "Local Research Agent",
    "File/Data Agent",
    "Local Planning Agent",
    "Local Drafting Agent",
    "Local Review Agent",
    "Local Decision Agent",
    "Local Troubleshooting Agent",
    "Local Summarization Agent",
    "Local Extraction Agent",
    "Local Classification Agent",
    "Local Transformation Agent",
]


def test_closeout_status_docs_file_exists():
    assert CLOSEOUT.exists()


def test_readme_links_closeout_status_note():
    readme_text = README.read_text(encoding="utf-8")

    assert "[Local Response Agents Closeout Status](docs/local-response-agents-closeout-status.md)" in readme_text


def test_index_page_links_closeout_status_note():
    index_text = INDEX.read_text(encoding="utf-8")

    assert "[Local Response Agents Closeout Status](local-response-agents-closeout-status.md)" in index_text


def test_closeout_note_lists_exactly_the_implemented_local_response_agents():
    closeout_text = CLOSEOUT.read_text(encoding="utf-8")
    completed_section = closeout_text.split("## Completed Local Response-Agent Set", 1)[1].split("## Supporting Docs", 1)[0]
    listed_agents = [line.removeprefix("- ") for line in completed_section.splitlines() if line.startswith("- ")]

    assert listed_agents == EXPECTED_AGENTS


def test_closeout_note_links_supporting_docs():
    closeout_text = CLOSEOUT.read_text(encoding="utf-8")

    assert "local-response-agents-index.md" in closeout_text
    assert "local-response-agents-smoke-runbook.md" in closeout_text
    assert "local-response-agents-smoke-evidence-template.md" in closeout_text


def test_closeout_note_includes_evidence_level():
    lower_closeout = CLOSEOUT.read_text(encoding="utf-8").lower()

    assert "local targeted tests only" in lower_closeout
    assert "github read-only verification after manual push" in lower_closeout
    assert "no ci run claimed" in lower_closeout
    assert "no full-suite validation claimed" in lower_closeout
    assert "no clean windows vm validation claimed" in lower_closeout


def test_closeout_note_includes_safety_boundaries():
    lower_closeout = CLOSEOUT.read_text(encoding="utf-8").lower()

    assert "response-only or metadata-only local behavior" in lower_closeout
    assert "no paid apis" in lower_closeout
    assert "no connectors" in lower_closeout
    assert "no oauth or account access" in lower_closeout
    assert "no browser automation" in lower_closeout
    assert "no cloud sync" in lower_closeout
    assert "no sending, posting, or purchases" in lower_closeout
    assert "no task persistence for response-only agents" in lower_closeout
    assert "no file mutation for response-only agents" in lower_closeout
    assert "no validation or certification claims" in lower_closeout


def test_closeout_note_says_it_does_not_start_future_work():
    lower_closeout = CLOSEOUT.read_text(encoding="utf-8").lower()

    assert "does not start v0.2" in lower_closeout
    assert "packaging" in lower_closeout
    assert "production tauri" in lower_closeout
    assert "full pairing" in lower_closeout
    assert "future connectors" in lower_closeout
    assert "private-alpha certification" in lower_closeout


def test_closeout_note_avoids_private_paths_and_sensitive_examples():
    closeout_text = CLOSEOUT.read_text(encoding="utf-8")
    lower_closeout = closeout_text.lower()
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

    assert all(item not in lower_closeout for item in forbidden)
    assert "@" not in closeout_text
