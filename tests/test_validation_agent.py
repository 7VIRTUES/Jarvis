import inspect

import pytest

from jarvis_core.db import init_db
from jarvis_core.validation_agent import ValidationAgentService
import jarvis_core.validation_agent as validation_agent_module


def validation_service(tmp_path):
    conn = init_db(tmp_path / "jarvis.sqlite")
    return ValidationAgentService(conn, tmp_path / "data" / "jarvis" / "reports")


def test_builtin_clean_windows_vm_validation_runbook_exists(tmp_path):
    service = validation_service(tmp_path)

    runbook = service.get_runbook("clean_windows_vm_validation")

    assert runbook["runbookId"] == "clean_windows_vm_validation"
    assert runbook["title"] == "Clean Windows VM Validation"
    assert runbook["targetEnvironment"].startswith("Clean Windows VM")
    assert runbook["steps"]
    assert "VirtualBox automation" in runbook["nonGoals"]


def test_runbook_steps_include_expected_vm_validation_categories(tmp_path):
    service = validation_service(tmp_path)

    runbook = service.get_runbook("clean_windows_vm_validation")
    categories = {step["category"] for step in runbook["steps"]}
    step_ids = {step["stepId"] for step in runbook["steps"]}

    assert {"environment", "install", "tests", "service", "dashboard", "LAN", "security", "connectors", "backup"} <= categories
    assert {
        "confirm_vm_environment",
        "confirm_prerequisites",
        "clone_repo",
        "python_setup",
        "unit_integration_tests",
        "service_startup",
        "dashboard_loopback",
        "profile_security_dashboard",
        "lan_token_boundary",
        "future_connector_boundary",
        "public_repo_safety",
        "backup_readiness",
    } <= step_ids


def test_create_validation_run(tmp_path):
    service = validation_service(tmp_path)

    run = service.create_run("clean_windows_vm_validation", "Clean Windows 11 VM")

    assert run["runbookId"] == "clean_windows_vm_validation"
    assert run["status"] == "in_progress"
    assert run["targetEnvironment"] == "Clean Windows 11 VM"
    assert len(run["stepResults"]) == len(service.get_runbook("clean_windows_vm_validation")["steps"])
    assert all(result["status"] == "not_started" for result in run["stepResults"])


def test_update_step_result(tmp_path):
    service = validation_service(tmp_path)
    run = service.create_run("clean_windows_vm_validation", "Clean Windows VM")

    updated = service.update_step_result(
        run["runId"],
        "confirm_vm_environment",
        "passed",
        notes="Windows version recorded",
        evidence="Manual summary only",
    )
    result = next(result for result in updated["stepResults"] if result["stepId"] == "confirm_vm_environment")

    assert result["status"] == "passed"
    assert result["notes"] == "Windows version recorded"
    assert result["redactedEvidence"] == "Manual summary only"


def test_invalid_status_rejected(tmp_path):
    service = validation_service(tmp_path)
    run = service.create_run("clean_windows_vm_validation", "Clean Windows VM")

    with pytest.raises(ValueError):
        service.update_step_result(run["runId"], "confirm_vm_environment", "running")


def test_unknown_runbook_rejected(tmp_path):
    service = validation_service(tmp_path)

    with pytest.raises(KeyError):
        service.create_run("missing_runbook", "Clean Windows VM")


def test_unknown_run_rejected(tmp_path):
    service = validation_service(tmp_path)

    with pytest.raises(KeyError):
        service.get_run("missing-run")


def test_completion_computes_passed_status(tmp_path):
    service = validation_service(tmp_path)
    run = service.create_run("clean_windows_vm_validation", "Clean Windows VM")

    for step in service.get_runbook("clean_windows_vm_validation")["steps"]:
        service.update_step_result(run["runId"], step["stepId"], "passed")

    completed = service.complete_run(run["runId"])

    assert completed["status"] == "passed"
    assert "completed as passed" in completed["summary"]


def test_completion_computes_failed_status(tmp_path):
    service = validation_service(tmp_path)
    run = service.create_run("clean_windows_vm_validation", "Clean Windows VM")
    service.update_step_result(run["runId"], "unit_integration_tests", "failed", notes="pytest failed")

    completed = service.complete_run(run["runId"])

    assert completed["status"] == "failed"


def test_completion_computes_blocked_status(tmp_path):
    service = validation_service(tmp_path)
    run = service.create_run("clean_windows_vm_validation", "Clean Windows VM")
    service.update_step_result(run["runId"], "service_startup", "blocked", notes="manual blocker")

    completed = service.complete_run(run["runId"])

    assert completed["status"] == "blocked"


def test_report_generation_works(tmp_path):
    service = validation_service(tmp_path)
    run = service.create_run("clean_windows_vm_validation", "Clean Windows VM")
    service.update_step_result(run["runId"], "confirm_vm_environment", "passed", notes="Windows version recorded")
    service.complete_run(run["runId"])

    report = service.write_markdown_report(run["runId"])
    report_path = tmp_path / "data" / "jarvis" / "reports" / report["reportId"]

    assert report["reportId"].startswith("validation-validation-run-")
    assert report_path.exists()
    text = report_path.read_text(encoding="utf-8")
    assert "# Validation Run Summary" in text
    assert "## Safety Boundaries" in text
    assert "not certification" in text


def test_report_redacts_likely_secrets_and_tokens(tmp_path):
    service = validation_service(tmp_path)
    run = service.create_run("clean_windows_vm_validation", "Clean Windows VM")
    raw_token = "sk-" + "a" * 24
    raw_password = "CorrectHorseBatteryStaple"
    service.update_step_result(
        run["runId"],
        "confirm_prerequisites",
        "passed",
        notes=f"OPENAI_API_KEY={raw_token}",
        evidence=f"password: {raw_password}",
    )

    report = service.write_markdown_report(run["runId"])
    text = (tmp_path / "data" / "jarvis" / "reports" / report["reportId"]).read_text(encoding="utf-8")

    assert raw_token not in text
    assert raw_password not in text
    assert "<redacted" in text


def test_evidence_does_not_store_raw_secret_values(tmp_path):
    service = validation_service(tmp_path)
    run = service.create_run("clean_windows_vm_validation", "Clean Windows VM")
    raw_token = "ghp_" + "b" * 24

    service.update_step_result(run["runId"], "clone_repo", "passed", evidence=f"Bearer {raw_token}")
    stored = service.conn.execute(
        "select notes, redacted_evidence from validation_step_results where run_id = ? and step_id = ?",
        (run["runId"], "clone_repo"),
    ).fetchone()

    assert raw_token not in stored[0]
    assert raw_token not in stored[1]
    assert "Bearer <redacted>" in stored[1]


def test_validation_agent_does_not_implement_command_execution_or_file_deletion():
    source = inspect.getsource(validation_agent_module)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert ".unlink(" not in source
    assert "rmtree" not in source


def test_validation_agent_does_not_read_protected_file_contents(tmp_path):
    service = validation_service(tmp_path)
    protected = tmp_path / ".env"
    protected.write_text("OPENAI_API_KEY=sk-should-not-be-read-by-validation-agent", encoding="utf-8")
    run = service.create_run("clean_windows_vm_validation", "Clean Windows VM")

    report = service.write_markdown_report(run["runId"])
    text = (tmp_path / "data" / "jarvis" / "reports" / report["reportId"]).read_text(encoding="utf-8")

    assert "sk-should-not-be-read-by-validation-agent" not in text
