from fastapi import HTTPException

import jarvis_core.app as app_module
from jarvis_core.dashboard import DashboardService
from jarvis_core.db import init_db
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.validation_agent import ValidationAgentService


def validation_app_services(tmp_path, monkeypatch):
    conn = init_db(tmp_path / "jarvis.sqlite")
    reports_root = tmp_path / "data" / "jarvis" / "reports"
    validation_agent = ValidationAgentService(conn, reports_root)
    dashboard = DashboardService(conn, tmp_path, tmp_path / "data" / "jarvis", tmp_path / "connectors")
    monkeypatch.setattr(app_module, "validation_agent", validation_agent)
    monkeypatch.setattr(app_module, "dashboard", dashboard)
    return validation_agent, dashboard


def test_validation_endpoints_are_guarded_by_dashboard_lan_guard():
    protected_paths = {
        "/validation/runbooks",
        "/validation/runbooks/{runbook_id}",
        "/validation/runs",
        "/validation/runs/{run_id}",
        "/validation/runs/{run_id}/steps/{step_id}",
        "/validation/runs/{run_id}/complete",
        "/validation/runs/{run_id}/report",
    }

    routes = {route.path: route for route in app_module.app.routes if getattr(route, "path", None) in protected_paths}

    assert set(routes) == protected_paths
    for route in routes.values():
        dependency_calls = {dependency.call for dependency in route.dependant.dependencies}
        assert require_dashboard_lan_access in dependency_calls


def test_list_runbooks_endpoint_works(tmp_path, monkeypatch):
    validation_app_services(tmp_path, monkeypatch)

    runbooks = app_module.list_validation_runbooks()

    runbook_ids = {runbook["runbookId"] for runbook in runbooks}
    assert "clean_windows_vm_validation" in runbook_ids
    assert len(runbooks) >= 8


def test_create_list_get_run_endpoints_work(tmp_path, monkeypatch):
    validation_app_services(tmp_path, monkeypatch)

    created = app_module.create_validation_run(
        app_module.ValidationRunInput(runbookId="clean_windows_vm_validation", targetEnvironment="Clean Windows VM")
    )
    runs = app_module.list_validation_runs()
    fetched = app_module.get_validation_run(created["runId"])

    assert created["status"] == "in_progress"
    assert runs[0]["runId"] == created["runId"]
    assert fetched["runId"] == created["runId"]
    assert fetched["stepResults"]


def test_step_update_endpoint_works(tmp_path, monkeypatch):
    validation_app_services(tmp_path, monkeypatch)
    run = app_module.create_validation_run(app_module.ValidationRunInput(runbookId="clean_windows_vm_validation"))

    updated = app_module.update_validation_step_result(
        run["runId"],
        "confirm_vm_environment",
        app_module.ValidationStepResultInput(status="passed", notes="manual pass", evidence="safe evidence"),
    )
    result = next(result for result in updated["stepResults"] if result["stepId"] == "confirm_vm_environment")

    assert result["status"] == "passed"
    assert result["notes"] == "manual pass"


def test_report_endpoint_works(tmp_path, monkeypatch):
    validation_app_services(tmp_path, monkeypatch)
    run = app_module.create_validation_run(app_module.ValidationRunInput(runbookId="clean_windows_vm_validation"))

    report = app_module.write_validation_report(run["runId"])

    assert report["reportId"].startswith("validation-validation-run-")
    assert (tmp_path / "data" / "jarvis" / "reports" / report["reportId"]).exists()


def test_unknown_runbook_endpoint_returns_404(tmp_path, monkeypatch):
    validation_app_services(tmp_path, monkeypatch)

    try:
        app_module.get_validation_runbook("missing")
    except HTTPException as exc:
        assert exc.status_code == 404
    else:
        raise AssertionError("missing runbook should return 404")


def test_unknown_run_endpoint_returns_404(tmp_path, monkeypatch):
    validation_app_services(tmp_path, monkeypatch)

    try:
        app_module.get_validation_run("missing")
    except HTTPException as exc:
        assert exc.status_code == 404
    else:
        raise AssertionError("missing run should return 404")


def test_invalid_step_status_endpoint_returns_400(tmp_path, monkeypatch):
    validation_app_services(tmp_path, monkeypatch)
    run = app_module.create_validation_run(app_module.ValidationRunInput(runbookId="clean_windows_vm_validation"))

    try:
        app_module.update_validation_step_result(
            run["runId"],
            "confirm_vm_environment",
            app_module.ValidationStepResultInput(status="running"),
        )
    except HTTPException as exc:
        assert exc.status_code == 400
    else:
        raise AssertionError("invalid step status should return 400")


def test_dashboard_summary_includes_validation_section(tmp_path, monkeypatch):
    validation_app_services(tmp_path, monkeypatch)
    app_module.create_validation_run(app_module.ValidationRunInput(runbookId="clean_windows_vm_validation"))

    summary = app_module.dashboard_summary()
    validation = summary["validationAgent"]

    assert summary["capabilities"]["validationAgent"] == "local_evidence_tracking"
    assert summary["counts"]["validationRuns"] == 1
    assert validation["agentId"] == "validation_agent"
    assert validation["availableRunbooksCount"] == len(app_module.list_validation_runbooks())
    assert validation["availableRunbooksCount"] >= 8
    assert validation["lastRunStatus"] == "in_progress"
    assert validation["commandExecution"] is False
    assert validation["virtualBoxAutomation"] is False
    assert validation["installerCreation"] is False
    assert validation["gitWrites"] is False
    assert validation["fileDeletion"] is False


def test_dashboard_html_includes_validation_section(tmp_path, monkeypatch):
    validation_app_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8").lower()

    assert 'id="validation-agent-status"' in page_text
    assert "validation agent" in page_text
    assert "manual evidence only" in page_text
    assert "/validation/runbooks" in page_text
    assert "/validation/runs" in page_text
    assert "run vm validation" not in page_text
    assert "build installer" not in page_text
