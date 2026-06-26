from pathlib import Path

import jarvis_core.app as app_module
from jarvis_core.dashboard import DashboardService
from jarvis_core.db import init_db


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


def app_services(tmp_path, monkeypatch):
    conn = init_db(tmp_path / "jarvis.sqlite")
    workspace = tmp_path / "workspace"
    data_root = tmp_path / "data" / "jarvis"
    connector_root = workspace / "connectors"
    dashboard = DashboardService(conn, workspace, data_root, connector_root)
    monkeypatch.setattr(app_module, "dashboard", dashboard)
    return dashboard


def test_dashboard_summary_exposes_local_response_agents_index(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    summary = app_module.dashboard_summary()
    index = summary["localResponseAgentsIndex"]

    assert summary["capabilities"]["localResponseAgentsIndex"] == "read_only_index"
    assert summary["safety"]["localResponseAgentsIndex"]["connectorExecution"] is False
    assert index["status"] == "read_only_index"
    assert index["agentCount"] == 11
    assert index["docsLink"] == "/docs/local-response-agents-index.md"
    assert index["addsAgents"] is False
    assert index["addsEndpoint"] is False
    assert index["mutation"] is False
    assert index["certificationClaims"] is False


def test_dashboard_index_includes_exactly_the_implemented_local_agents(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    agents = app_module.dashboard_summary()["localResponseAgentsIndex"]["agents"]

    assert [agent["name"] for agent in agents] == EXPECTED_AGENTS
    assert all(agent["status"] == "implemented_local_only" for agent in agents)
    assert all(agent["endpoint"].startswith("POST /agents/") for agent in agents)
    assert all(agent["docsLink"].startswith("/docs/") for agent in agents)
    assert all(agent["docsLink"].endswith(".md") for agent in agents)
    assert {agent["responseMode"] for agent in agents} == {"response_only", "metadata_only"}
    assert all(isinstance(agent["exampleRequestBody"], dict) for agent in agents)
    assert all(agent["exampleRequestBody"] for agent in agents)


def test_dashboard_index_global_boundaries_cover_required_safety_limits(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    index = app_module.dashboard_summary()["localResponseAgentsIndex"]
    boundaries_text = " ".join(index["globalBoundaries"]).lower()

    assert "no paid apis" in boundaries_text
    assert "no connectors" in boundaries_text
    assert "no oauth or account access" in boundaries_text
    assert "no browser automation" in boundaries_text
    assert "no cloud sync" in boundaries_text
    assert "no file mutation except existing coding agent workflows" in boundaries_text
    assert "no email sending, posting, or purchases" in boundaries_text
    assert "no task persistence for response-only agents" in boundaries_text
    assert "no claims of clean windows vm validation" in boundaries_text
    assert "ci validation" in boundaries_text
    assert "private-alpha certification" in boundaries_text
    assert index["paidApis"] is False
    assert index["connectorExecution"] is False
    assert index["oauth"] is False
    assert index["accountAccess"] is False
    assert index["browserAutomation"] is False
    assert index["cloudSync"] is False
    assert index["emailSendingPostingPurchases"] is False
    assert index["taskPersistenceForResponseOnlyAgents"] is False


def test_dashboard_index_agent_entries_include_safe_example_request_bodies(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    agents = app_module.dashboard_summary()["localResponseAgentsIndex"]["agents"]
    file_data_agent = next(agent for agent in agents if agent["name"] == "File/Data Agent")
    examples_text = str([agent["exampleRequestBody"] for agent in agents]).lower()

    assert file_data_agent["exampleRequestBody"] == {"projectName": "Jarvis"}
    assert ".env" not in examples_text
    assert "token=" not in examples_text
    assert "credential" not in examples_text
    assert "c:\\" not in examples_text
    assert "@" not in examples_text


def test_dashboard_html_includes_local_response_agents_index_section_and_link(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8")

    assert 'id="local-response-agents-index"' in page_text
    assert "Local Response Agents Index" in page_text
    assert "Read-only inventory." in page_text
    assert "/docs/local-response-agents-index.md" in page_text
    assert "renderLocalResponseAgentsIndex(summary.localResponseAgentsIndex)" in page_text
    assert "local-response-agents-index-status" in page_text


def test_docs_page_includes_agents_and_global_boundaries():
    doc_text = Path("docs/local-response-agents-index.md").read_text(encoding="utf-8")
    lower_doc = doc_text.lower()

    for agent_name in EXPECTED_AGENTS:
        assert agent_name in doc_text

    assert doc_text.count("implemented_local_only") == 11
    assert "No paid APIs." in doc_text
    assert "No connectors." in doc_text
    assert "No OAuth or account access." in doc_text
    assert "No browser automation." in doc_text
    assert "No cloud sync." in doc_text
    assert "No email sending, posting, or purchases." in doc_text
    assert "No task persistence for response-only agents." in doc_text
    assert "No claims of clean Windows VM validation" in doc_text
    assert "CI validation" in doc_text
    assert "private-alpha certification" in doc_text
    assert "production readiness" in lower_doc
    assert "security certification" in lower_doc
