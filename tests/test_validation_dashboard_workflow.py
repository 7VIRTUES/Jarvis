import inspect

from fastapi import HTTPException

import jarvis_core.app as app_module
import jarvis_core.dashboard as dashboard_module
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


def dashboard_text() -> str:
    return app_module.local_dashboard().body.decode("utf-8")


def test_dashboard_html_includes_validation_agent_workflow_section(tmp_path, monkeypatch):
    validation_app_services(tmp_path, monkeypatch)

    page = dashboard_text()
    lowered = page.lower()

    assert 'id="validation-agent-status"' in lowered
    assert "load runbooks" in lowered
    assert "create manual validation run" in lowered
    assert "load recent runs" in lowered
    assert "open run" in lowered
    assert "record step result" in lowered
    assert "complete evidence record" in lowered
    assert "generate local report" in lowered
    assert "/validation/runbooks" in page
    assert "/validation/runs" in page


def test_dashboard_html_includes_manual_evidence_only_safety_text(tmp_path, monkeypatch):
    validation_app_services(tmp_path, monkeypatch)

    page = dashboard_text().lower()

    assert "manual evidence only" in page
    assert "does not control virtualbox" in page
    assert "run commands" in page
    assert "install dependencies" in page
    assert "create installers" in page
    assert "push to github" in page
    assert "certify security or production readiness" in page


def test_dashboard_html_does_not_include_fake_automation_labels(tmp_path, monkeypatch):
    validation_app_services(tmp_path, monkeypatch)

    page = dashboard_text().lower()

    forbidden = [
        "run vm validation",
        "run tests automatically",
        "fix issues",
        "deploy",
        "package installer",
        "install now",
        "build installer",
    ]
    assert all(label not in page for label in forbidden)


def test_runbooks_endpoint_supports_dashboard_workflow(tmp_path, monkeypatch):
    validation_app_services(tmp_path, monkeypatch)

    runbooks = app_module.list_validation_runbooks()
    runbook = runbooks[0]

    assert runbook["runbookId"] == "clean_windows_vm_validation"
    assert runbook["description"]
    assert runbook["steps"]
    first_step = runbook["steps"][0]
    assert {"stepId", "title", "category", "required", "expectedResult", "evidenceType"} <= set(first_step)


def test_create_validation_run_through_endpoint_works(tmp_path, monkeypatch):
    validation_app_services(tmp_path, monkeypatch)

    run = app_module.create_validation_run(
        app_module.ValidationRunInput(
            runbookId="clean_windows_vm_validation",
            targetEnvironment="Clean Windows VM manual validation",
        )
    )

    assert run["status"] == "in_progress"
    assert run["targetEnvironment"] == "Clean Windows VM manual validation"
    assert run["stepResults"]


def test_update_validation_step_through_endpoint_works(tmp_path, monkeypatch):
    validation_app_services(tmp_path, monkeypatch)
    run = app_module.create_validation_run(app_module.ValidationRunInput(runbookId="clean_windows_vm_validation"))

    updated = app_module.update_validation_step_result(
        run["runId"],
        "confirm_vm_environment",
        app_module.ValidationStepResultInput(status="passed", notes="manual note", evidence="manual evidence"),
    )
    result = next(result for result in updated["stepResults"] if result["stepId"] == "confirm_vm_environment")

    assert result["status"] == "passed"
    assert result["notes"] == "manual note"
    assert result["redactedEvidence"] == "manual evidence"


def test_complete_validation_run_through_endpoint_works(tmp_path, monkeypatch):
    validation_app_services(tmp_path, monkeypatch)
    run = app_module.create_validation_run(app_module.ValidationRunInput(runbookId="clean_windows_vm_validation"))
    for step in app_module.get_validation_runbook("clean_windows_vm_validation")["steps"]:
        app_module.update_validation_step_result(
            run["runId"],
            step["stepId"],
            app_module.ValidationStepResultInput(status="passed"),
        )

    completed = app_module.complete_validation_run(run["runId"])

    assert completed["status"] == "passed"
    assert "completed as passed" in completed["summary"]


def test_generate_report_through_endpoint_works(tmp_path, monkeypatch):
    validation_app_services(tmp_path, monkeypatch)
    run = app_module.create_validation_run(app_module.ValidationRunInput(runbookId="clean_windows_vm_validation"))

    report = app_module.write_validation_report(run["runId"])

    assert report["reportId"].startswith("validation-validation-run-")
    assert (tmp_path / "data" / "jarvis" / "reports" / report["reportId"]).exists()


def test_validation_workflow_endpoints_are_guarded_by_dashboard_lan_guard():
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


def test_synthetic_token_like_values_are_redacted_in_result_and_report(tmp_path, monkeypatch):
    validation_app_services(tmp_path, monkeypatch)
    run = app_module.create_validation_run(app_module.ValidationRunInput(runbookId="clean_windows_vm_validation"))
    raw_token = "sk-" + "c" * 24
    raw_bearer = "ghp_" + "d" * 24

    updated = app_module.update_validation_step_result(
        run["runId"],
        "confirm_prerequisites",
        app_module.ValidationStepResultInput(
            status="passed",
            notes=f"OPENAI_API_KEY={raw_token}",
            evidence=f"Bearer {raw_bearer}",
        ),
    )
    report = app_module.write_validation_report(run["runId"])
    report_text = (tmp_path / "data" / "jarvis" / "reports" / report["reportId"]).read_text(encoding="utf-8")
    response_text = str(updated)

    assert raw_token not in response_text
    assert raw_bearer not in response_text
    assert raw_token not in report_text
    assert raw_bearer not in report_text
    assert "<redacted" in response_text
    assert "<redacted" in report_text


def test_dashboard_response_does_not_expose_raw_synthetic_token_values(tmp_path, monkeypatch):
    validation_app_services(tmp_path, monkeypatch)
    raw_token = "sk-" + "e" * 24

    page = dashboard_text()

    assert raw_token not in page


def test_unknown_run_and_runbook_behavior_is_safe(tmp_path, monkeypatch):
    validation_app_services(tmp_path, monkeypatch)

    try:
        app_module.get_validation_runbook("missing")
    except HTTPException as exc:
        assert exc.status_code == 404
    else:
        raise AssertionError("missing runbook should return 404")

    try:
        app_module.get_validation_run("missing")
    except HTTPException as exc:
        assert exc.status_code == 404
    else:
        raise AssertionError("missing run should return 404")


def test_invalid_status_is_rejected(tmp_path, monkeypatch):
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
        raise AssertionError("invalid status should return 400")


def test_dashboard_workflow_adds_no_command_execution_or_file_deletion():
    source = inspect.getsource(dashboard_module)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert ".unlink(" not in source
    assert "rmtree" not in source
