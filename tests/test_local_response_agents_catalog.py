import re

from jarvis_core.local_response_agents_catalog import (
    local_response_agents_global_boundaries,
    local_response_agents_index,
    local_response_agents_summary,
)


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

REQUIRED_FIELDS = {
    "name",
    "endpoint",
    "status",
    "mode",
    "docsLink",
    "responseMode",
    "safetyNotes",
    "exampleRequestBody",
}


def test_catalog_exposes_exactly_11_agents_with_required_fields():
    agents = local_response_agents_index()

    assert len(agents) == 11
    for agent in agents:
        assert REQUIRED_FIELDS <= set(agent)
        assert agent["name"]
        assert agent["endpoint"].startswith("POST /agents/")
        assert agent["status"] == "implemented_local_only"
        assert agent["mode"]
        assert agent["docsLink"].startswith("/docs/")
        assert agent["docsLink"].endswith(".md")
        assert agent["responseMode"] in {"response_only", "metadata_only"}
        assert agent["safetyNotes"]
        assert isinstance(agent["exampleRequestBody"], dict)
        assert agent["exampleRequestBody"]


def test_catalog_includes_all_expected_endpoints_once():
    endpoints = [agent["endpoint"] for agent in local_response_agents_index()]

    assert endpoints == EXPECTED_ENDPOINTS
    assert len(set(endpoints)) == len(EXPECTED_ENDPOINTS)


def test_catalog_global_boundaries_cover_required_safety_limits():
    boundaries_text = " ".join(local_response_agents_global_boundaries()).lower()

    assert "no paid apis" in boundaries_text
    assert "no connectors" in boundaries_text
    assert "no oauth or account access" in boundaries_text
    assert "no browser automation" in boundaries_text
    assert "no cloud sync" in boundaries_text
    assert "no email sending, posting, or purchases" in boundaries_text
    assert "no task persistence for response-only agents" in boundaries_text
    assert "certification" in boundaries_text


def test_catalog_example_request_bodies_are_safe_local_examples():
    forbidden_fragments = [
        ".env",
        "c:\\",
        "c:/",
        "/users/",
        "api_key",
        "apikey",
        "secret=",
        "token=",
        "password",
        "credential",
        "account id",
        "account_id",
        "rm -rf",
        "del /",
        "format ",
        "shutdown",
        "http://",
        "https://",
    ]

    for agent in local_response_agents_index():
        example_text = str(agent["exampleRequestBody"]).lower()

        assert all(fragment not in example_text for fragment in forbidden_fragments)
        assert not re.search(r"[\w.+-]+@[\w.-]+\.[a-z]{2,}", example_text)


def test_file_data_example_uses_only_registered_project_name():
    file_data_agent = next(agent for agent in local_response_agents_index() if agent["name"] == "File/Data Agent")

    assert file_data_agent["exampleRequestBody"] == {"projectName": "Jarvis"}
    assert any("registered project" in note.lower() for note in file_data_agent["safetyNotes"])
    assert any("raw arbitrary local paths" in note.lower() for note in file_data_agent["safetyNotes"])


def test_catalog_summary_preserves_dashboard_index_shape():
    summary = local_response_agents_summary()

    assert summary["status"] == "read_only_index"
    assert summary["agentCount"] == 11
    assert summary["agents"] == local_response_agents_index()
    assert summary["globalBoundaries"] == local_response_agents_global_boundaries()
    assert summary["docsLink"] == "/docs/local-response-agents-index.md"
    assert summary["addsAgents"] is False
    assert summary["addsEndpoint"] is False
    assert summary["mutation"] is False
    assert summary["connectorExecution"] is False
    assert summary["paidApis"] is False
    assert summary["certificationClaims"] is False
