import json

import jarvis_core.app as app_module
from jarvis_core.db import init_db
from jarvis_core.validation_agent import ValidationAgentService


NEW_RUNBOOK_IDS = {
    "clean_vm_core_service_smoke",
    "clean_vm_dashboard_loopback_smoke",
    "clean_vm_lan_guard_smoke",
    "clean_vm_codex_available_scenario",
    "clean_vm_codex_missing_scenario",
    "clean_vm_future_connectors_disabled",
    "clean_vm_backup_restore_reminder",
}


def service(tmp_path):
    conn = init_db(tmp_path / "jarvis.sqlite")
    return ValidationAgentService(conn, tmp_path / "reports")


def new_runbooks(tmp_path):
    runbooks = service(tmp_path).list_runbooks()
    return [runbook for runbook in runbooks if runbook["runbookId"] in NEW_RUNBOOK_IDS]


def test_new_runbook_ids_are_listed(tmp_path):
    runbook_ids = {runbook["runbookId"] for runbook in service(tmp_path).list_runbooks()}

    assert NEW_RUNBOOK_IDS <= runbook_ids


def test_each_new_runbook_is_manual_only(tmp_path):
    for runbook in new_runbooks(tmp_path):
        notes = " ".join(runbook["safetyNotes"]).lower()
        non_goals = " ".join(runbook["nonGoals"]).lower()

        assert "manual-only" in notes
        assert "does not run commands" in notes
        assert "vm automation" in non_goals
        assert "readiness certification" in non_goals


def test_each_new_runbook_has_ordered_steps(tmp_path):
    for runbook in new_runbooks(tmp_path):
        step_ids = [step["stepId"] for step in runbook["steps"]]

        assert len(step_ids) >= 2
        assert step_ids == list(dict.fromkeys(step_ids))
        assert all(step_id.startswith("record_") for step_id in step_ids)


def test_each_new_runbook_has_expected_evidence_fields(tmp_path):
    for runbook in new_runbooks(tmp_path):
        for step in runbook["steps"]:
            assert step["evidenceType"]
            assert "Evidence fields:" in step["expectedResult"]
            assert "Pass:" in step["expectedResult"]
            assert "Fail:" in step["expectedResult"]
            assert "Warning:" in step["expectedResult"]


def test_no_new_runbook_claims_automatic_validation_or_completion(tmp_path):
    text = json.dumps(new_runbooks(tmp_path), sort_keys=True).lower()

    assert "automatic validation" not in text
    assert "automatically validated" not in text
    assert "validation is complete" not in text
    assert "claim validation completion" not in text


def test_new_runbook_instructions_do_not_include_automation_behaviors(tmp_path):
    forbidden = [
        "control virtualbox",
        "control vmware",
        "control hyper-v",
        "detect vm software",
        "build installer",
        "create installer",
        "external service",
        "upload evidence",
        "share evidence",
        "execute command",
    ]
    instruction_text = " ".join(
        step["instructions"].lower()
        for runbook in new_runbooks(tmp_path)
        for step in runbook["steps"]
    )

    assert all(term not in instruction_text for term in forbidden)


def test_existing_validation_runbook_endpoint_still_returns_runbooks(tmp_path, monkeypatch):
    validation = service(tmp_path)
    monkeypatch.setattr(app_module, "validation_agent", validation)

    runbooks = app_module.list_validation_runbooks()
    runbook_ids = {runbook["runbookId"] for runbook in runbooks}

    assert "clean_windows_vm_validation" in runbook_ids
    assert NEW_RUNBOOK_IDS <= runbook_ids
