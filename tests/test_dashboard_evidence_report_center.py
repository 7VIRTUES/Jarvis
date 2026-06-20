import json

import pytest
from fastapi import HTTPException

import jarvis_core.app as app_module
from jarvis_core.dashboard import DashboardService
from jarvis_core.db import init_db
from jarvis_core.evidence_report_center import EvidenceReportCenterService
from jarvis_core.lan_security import require_dashboard_lan_access


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def evidence_app_services(tmp_path, monkeypatch):
    conn = init_db(tmp_path / "jarvis.sqlite")
    workspace = tmp_path / "workspace"
    data_root = tmp_path / "data" / "jarvis"
    connector_root = workspace / "connectors"
    dashboard = DashboardService(conn, workspace, data_root, connector_root)
    evidence = EvidenceReportCenterService(data_root / "reports")
    monkeypatch.setattr(app_module, "dashboard", dashboard)
    monkeypatch.setattr(app_module, "evidence_reports", evidence)
    return dashboard, evidence


def test_evidence_report_index_endpoint_returns_metadata(tmp_path, monkeypatch):
    _dashboard, evidence = evidence_app_services(tmp_path, monkeypatch)
    write_text(evidence.reports_root / "security-safety-Jarvis-20260101T000000Z.md", "# Security/Safety Review Summary\n\n## Verdict\npass\n")

    index = app_module.list_evidence_reports()

    assert index["totalReports"] == 1
    assert index["reports"][0]["reportType"] == "security_safety_review"
    assert index["reports"][0]["safeDetailEndpoint"].startswith("/evidence/reports/")


def test_evidence_report_detail_endpoint_returns_redacted_markdown(tmp_path, monkeypatch):
    _dashboard, evidence = evidence_app_services(tmp_path, monkeypatch)
    raw_secret = "github_pat_" + "a" * 24
    write_text(evidence.reports_root / "security-safety-Jarvis-20260101T000000Z.md", f"# Report\n\naccess_token={raw_secret}\n")

    detail = app_module.get_evidence_report_detail("security-safety-Jarvis-20260101T000000Z.md")

    assert detail["contentType"] == "text/markdown"
    assert raw_secret not in json.dumps(detail)
    assert "<redacted" in detail["content"]


def test_evidence_report_metadata_endpoint_blocks_traversal(tmp_path, monkeypatch):
    evidence_app_services(tmp_path, monkeypatch)

    with pytest.raises(HTTPException) as exc_info:
        app_module.get_evidence_report_metadata("..%2Fsecret.md")

    assert exc_info.value.status_code == 400
    assert "single Markdown or JSON report filename" in exc_info.value.detail


def test_dashboard_summary_includes_evidence_report_center(tmp_path, monkeypatch):
    _dashboard, evidence = evidence_app_services(tmp_path, monkeypatch)
    write_text(evidence.reports_root / "diagnostics-bundle-20260101T000000Z.json", json.dumps({"agentId": "redacted_diagnostics_agent"}))

    summary = app_module.dashboard_summary()
    center = summary["evidenceReportCenter"]

    assert summary["capabilities"]["evidenceReportCenter"] == "local_report_metadata_only"
    assert center["agentId"] == "evidence_report_center_agent"
    assert center["uploads"] is False
    assert center["commandExecution"] is False
    assert center["fileDeletion"] is False
    assert center["arbitraryFilesystemBrowsing"] is False
    assert center["protectedSecretReads"] is False
    assert center["certification"] is False


def test_dashboard_report_center_section_appears(tmp_path, monkeypatch):
    evidence_app_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8").lower()

    assert 'id="evidence-report-center"' in page_text
    assert "evidence report center" in page_text
    assert "refresh report index" in page_text
    assert "/evidence/reports" in page_text
    assert "local report metadata only" in page_text
    assert "metadata view only" in page_text
    assert "no report mutation, network transfer, publication, or readiness attestation is available" in page_text
    assert "redacts summaries" in page_text


def test_dashboard_report_center_does_not_include_forbidden_controls(tmp_path, monkeypatch):
    evidence_app_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8").lower()
    forbidden_button_labels = [
        "delete report",
        "upload report",
        "send report",
        "share report",
        "publish report",
        "certify report",
        "fix report",
        "run report",
    ]

    assert all(f">{label}<" not in page_text for label in forbidden_button_labels)
    assert ">refresh report index<" in page_text


def test_evidence_report_endpoints_are_guarded_by_dashboard_lan_guard():
    protected_paths = {
        "/evidence/reports",
        "/evidence/reports/{report_id}",
        "/evidence/reports/{report_id}/metadata",
    }
    routes = {route.path: route for route in app_module.app.routes if getattr(route, "path", None) in protected_paths}

    assert set(routes) == protected_paths
    for route in routes.values():
        dependency_calls = {dependency.call for dependency in route.dependant.dependencies}
        assert require_dashboard_lan_access in dependency_calls


