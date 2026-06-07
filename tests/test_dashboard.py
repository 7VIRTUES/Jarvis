import json

import pytest
from fastapi import HTTPException

import jarvis_core.app as app_module
from jarvis_core.dashboard import DashboardService
from jarvis_core.db import init_db


def dashboard_service(tmp_path, monkeypatch):
    conn = init_db(tmp_path / "jarvis.sqlite")
    service = DashboardService(conn, tmp_path, tmp_path / "data" / "jarvis", tmp_path / "connectors")
    monkeypatch.setattr(app_module, "dashboard", service)
    return service


def test_dashboard_summary_endpoint_returns_safe_status_data(tmp_path, monkeypatch):
    dashboard_service(tmp_path, monkeypatch)

    summary = app_module.dashboard_summary()

    assert summary["app"]["mode"] == "local"
    assert summary["phase"]["current"] == "v0.1C Slice 1"
    assert summary["capabilities"]["unsupportedControlsExposed"] is False
    assert summary["safety"]["paidApis"] is False
    assert summary["safety"]["connectorExecution"] is False


def test_reports_list_endpoint_works_when_reports_exist(tmp_path, monkeypatch):
    service = dashboard_service(tmp_path, monkeypatch)
    service.reports_root.mkdir(parents=True)
    (service.reports_root / "alpha.md").write_text("# Alpha\n\nReport body.", encoding="utf-8")

    reports = app_module.list_dashboard_reports()
    assert reports[0]["id"] == "alpha.md"
    assert reports[0]["title"] == "alpha"
    assert reports[0]["sizeBytes"] > 0


def test_reports_list_endpoint_handles_no_reports_cleanly(tmp_path, monkeypatch):
    dashboard_service(tmp_path, monkeypatch)

    assert app_module.list_dashboard_reports() == []


def test_report_detail_endpoint_reads_allowed_report(tmp_path, monkeypatch):
    service = dashboard_service(tmp_path, monkeypatch)
    service.reports_root.mkdir(parents=True)
    (service.reports_root / "closeout.md").write_text("# Closeout\n\nValidated.", encoding="utf-8")

    response = app_module.get_dashboard_report("closeout.md")

    assert response["content"] == "# Closeout\n\nValidated."


def test_report_detail_endpoint_blocks_path_traversal(tmp_path, monkeypatch):
    service = dashboard_service(tmp_path, monkeypatch)
    service.reports_root.mkdir(parents=True)
    (tmp_path / "secret.md").write_text("# Outside", encoding="utf-8")

    with pytest.raises(HTTPException) as exc_info:
        app_module.get_dashboard_report("..%2Fsecret.md")

    assert exc_info.value.status_code == 400
    assert "single Markdown file name" in exc_info.value.detail


def test_report_detail_endpoint_blocks_absolute_paths(tmp_path, monkeypatch):
    dashboard_service(tmp_path, monkeypatch)

    with pytest.raises(HTTPException) as exc_info:
        app_module.get_dashboard_report("C:%2Foutside.md")
    assert exc_info.value.status_code == 400
    assert "single Markdown file name" in exc_info.value.detail


def test_report_detail_endpoint_returns_404_for_missing_report(tmp_path, monkeypatch):
    dashboard_service(tmp_path, monkeypatch)

    with pytest.raises(HTTPException) as exc_info:
        app_module.get_dashboard_report("missing.md")
    assert exc_info.value.status_code == 404
    assert "report not found" in exc_info.value.detail


def test_connector_summary_keeps_future_connectors_placeholder_only(tmp_path, monkeypatch):
    dashboard_service(tmp_path, monkeypatch)
    placeholders = tmp_path / "connectors" / "placeholders"
    placeholders.mkdir(parents=True)
    (placeholders / "gmail.json").write_text(json.dumps(_connector("gmail", "Gmail")), encoding="utf-8")

    connectors = app_module.dashboard_summary()["connectors"]
    assert connectors == [
        {
            "id": "gmail",
            "provider": "Gmail",
            "implemented": False,
            "defaultEnabled": False,
            "readinessLevel": "placeholder_only",
            "availableInDashboard": False,
            "status": "placeholder_only",
        }
    ]


def test_unsupported_controls_are_not_exposed_as_working_automation(tmp_path, monkeypatch):
    dashboard_service(tmp_path, monkeypatch)

    summary = app_module.dashboard_summary()
    page = app_module.local_dashboard()

    assert all(action["available"] is False for action in summary["unsupportedActions"])
    assert "<button" not in page.body.decode("utf-8").lower()
    assert "git push" not in page.body.decode("utf-8").lower()


def _connector(connector_id: str, provider: str) -> dict[str, object]:
    return {
        "id": connector_id,
        "provider": provider,
        "implemented": False,
        "defaultEnabled": False,
        "readinessLevel": "placeholder_only",
        "costMode": "disabled",
        "authType": "not_implemented",
        "privacyClass": "external_account",
        "dataAccess": "none_in_v0.1C",
        "approvalRequired": True,
        "tokenStorage": "not_implemented",
        "dataRetention": "none",
        "notes": "Placeholder only.",
    }
