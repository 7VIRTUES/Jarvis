import json

import pytest
from fastapi import HTTPException

import jarvis_core.app as app_module
from jarvis_core.dashboard import DashboardService
from jarvis_core.db import init_db
from jarvis_core.docs_center import DocsCenterService
from jarvis_core.lan_security import require_dashboard_lan_access


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def app_services(tmp_path, monkeypatch):
    conn = init_db(tmp_path / "jarvis.sqlite")
    workspace = tmp_path / "workspace"
    data_root = tmp_path / "data" / "jarvis"
    connector_root = workspace / "connectors"
    dashboard = DashboardService(conn, workspace, data_root, connector_root)
    docs_center = DocsCenterService(workspace)
    monkeypatch.setattr(app_module, "dashboard", dashboard)
    monkeypatch.setattr(app_module, "docs_center", docs_center)
    return dashboard, docs_center


def test_docs_index_endpoint_returns_metadata(tmp_path, monkeypatch):
    _dashboard, service = app_services(tmp_path, monkeypatch)
    write_text(service.workspace_root / "README.md", "# Jarvis\n\nLocal docs.")

    index = app_module.get_docs_index()

    assert index["totalDocs"] == 1
    assert index["docs"][0]["docId"] == "README.md"
    assert index["docs"][0]["category"] == "README"


def test_doc_detail_endpoint_returns_redacted_markdown(tmp_path, monkeypatch):
    _dashboard, service = app_services(tmp_path, monkeypatch)
    raw_secret = "github_pat_" + "a" * 24
    write_text(service.docs_root / "secret.md", f"# Secret\n\naccess_token={raw_secret}\n")

    detail = app_module.get_doc_detail("secret.md")

    assert detail["contentType"] == "text/markdown"
    assert raw_secret not in json.dumps(detail)
    assert "<redacted" in detail["content"]


def test_doc_metadata_endpoint_blocks_traversal(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    with pytest.raises(HTTPException) as exc_info:
        app_module.get_doc_metadata("..%2FREADME.md")

    assert exc_info.value.status_code == 400
    assert "single Markdown filename" in exc_info.value.detail


def test_dashboard_summary_includes_docs_center(tmp_path, monkeypatch):
    _dashboard, service = app_services(tmp_path, monkeypatch)
    write_text(service.workspace_root / "README.md", "# Jarvis\n\nLocal docs.")

    summary = app_module.dashboard_summary()
    center = summary["docsCenter"]

    assert summary["capabilities"]["docsCenter"] == "local_docs_metadata_only"
    assert center["agentId"] == "docs_runbook_center_agent"
    assert center["totalDocs"] == 1
    assert center["docMutation"] is False
    assert center["externalServices"] is False
    assert center["uploads"] is False
    assert center["certification"] is False


def test_dashboard_docs_center_section_exists(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8").lower()

    assert 'id="docs-runbook-center"' in page_text
    assert "docs/runbook center" in page_text
    assert "refresh docs index" in page_text
    assert "/docs/index" in page_text
    assert "approved local markdown docs only" in page_text


def test_dashboard_docs_center_forbidden_labels_absent(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8").lower()
    start = page_text.index('id="docs-runbook-center"')
    end = page_text.index('id="project-profiles"')
    section = page_text[start:end]
    forbidden = ["delete", "upload", "send", "share", "publish", "certify", "fix", "run", "edit"]

    assert all(f">{label}<" not in section for label in forbidden)
    assert ">refresh docs index<" in section


def test_docs_endpoints_are_guarded_by_dashboard_lan_guard():
    protected_paths = {
        "/docs/index",
        "/docs/{doc_id}",
        "/docs/{doc_id}/metadata",
    }
    routes = {route.path: route for route in app_module.app.routes if getattr(route, "path", None) in protected_paths}

    assert set(routes) == protected_paths
    for route in routes.values():
        dependency_calls = {dependency.call for dependency in route.dependant.dependencies}
        assert require_dashboard_lan_access in dependency_calls
