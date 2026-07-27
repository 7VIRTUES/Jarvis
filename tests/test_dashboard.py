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
    assert summary["phase"]["current"] == "v0.1D Batch 2"
    assert summary["capabilities"]["unsupportedControlsExposed"] is False
    assert summary["capabilities"]["settings"] == "read_only_status"
    assert summary["capabilities"]["stopTask"] == "jarvis_task_queue_state_only"
    assert summary["capabilities"]["desktopShell"] == "placeholder_only"
    assert summary["capabilities"]["firstRunWizard"] == "placeholder_only"
    assert summary["capabilities"]["privateAlphaPackaging"] == "placeholder_only"
    assert summary["safety"]["paidApis"] is False
    assert summary["safety"]["connectorExecution"] is False
    assert summary["safety"]["arbitraryProcessKill"] is False
    assert summary["safety"]["desktopShell"]["autoUpdaterEnabled"] is False
    assert summary["settings"]["settingsEditable"] is False
    assert summary["lanProtection"]["lanProtectionImplemented"] is True
    assert summary["stopTask"]["pidAccepted"] is False
    assert summary["desktopShell"]["tauriShellImplemented"] is False
    assert summary["firstRunWizard"]["setupStatePersistenceImplemented"] is False
    assert summary["privateAlphaPackaging"]["installerBuildImplemented"] is False


def test_settings_summary_endpoint_returns_safe_read_only_status_data(tmp_path, monkeypatch):
    dashboard_service(tmp_path, monkeypatch)

    settings = app_module.settings_summary()

    assert settings["appName"] == "Jarvis PC Local"
    assert settings["phase"] == "v0.1D"
    assert settings["currentSlice"] == "Memory Center dashboard and private-session UX"
    assert settings["localFirst"] is True
    assert settings["settingsEditable"] is False
    assert settings["settingsPersistence"] == "not_implemented_in_this_slice"
    assert settings["autonomyMode"] == "supervised_local_only"
    assert settings["safetyMode"] == "local_dashboard_with_approval_gated_memory"


def test_settings_summary_confirms_paid_ai_and_browser_automation_disabled(tmp_path, monkeypatch):
    dashboard_service(tmp_path, monkeypatch)

    settings = app_module.settings_summary()

    assert settings["paidAiApisEnabled"] is False
    assert settings["browserAutomationEnabled"] is False


def test_settings_summary_confirms_external_connectors_disabled(tmp_path, monkeypatch):
    dashboard_service(tmp_path, monkeypatch)

    settings = app_module.settings_summary()

    assert settings["externalConnectorsEnabled"] is False
    assert settings["nonCodingConnectorsImplemented"] is False


def test_settings_summary_marks_lan_pairing_future_and_stop_task_boundary(tmp_path, monkeypatch):
    dashboard_service(tmp_path, monkeypatch)

    settings = app_module.settings_summary()

    assert settings["lanPairingStatus"] == "not_implemented_yet"
    assert settings["tokenProtectionStatus"] == "implemented_for_dashboard_api"
    assert settings["lanProtection"]["nonLoopbackRequiresToken"] is True
    assert settings["lanSetup"]["setupPageLoopbackOnly"] is True
    assert settings["stopTaskStatus"] == "implemented_for_jarvis_task_queue_state_only"
    assert settings["stopTask"]["osProcessControl"] is False
    assert settings["stopTask"]["pidAccepted"] is False
    assert settings["tauriShellStatus"] == "placeholder_only"
    assert settings["firstRunWizardStatus"] == "placeholder_only"
    assert settings["installerStatus"] == "not_implemented_yet"
    assert settings["privateAlphaPackagingStatus"] == "placeholder_only"


def test_settings_summary_reports_desktop_shell_placeholder_status(tmp_path, monkeypatch):
    dashboard_service(tmp_path, monkeypatch)

    settings = app_module.settings_summary()
    desktop = settings["desktopShell"]

    assert settings["desktopShellStatus"] == "placeholder_only"
    assert settings["tauriShellStatus"] == "placeholder_only"
    assert settings["tauriShellImplemented"] is False
    assert settings["tauriDependenciesInstalled"] is False
    assert settings["installerPackagingStatus"] == "placeholder_only"
    assert settings["autoUpdaterEnabled"] is False
    assert settings["telemetryEnabled"] is False
    assert desktop["desktopShellStatus"] == "placeholder_only"
    assert desktop["productionDesktopAppImplemented"] is False
    assert desktop["desktopLaunchControlAvailable"] is False
    assert desktop["desktopInstallControlAvailable"] is False
    assert desktop["lanTokenProtectionMustBeRespected"] is True
    assert desktop["safeActionRuntimeMustBeRespected"] is True


def test_settings_summary_reports_first_run_placeholder_status(tmp_path, monkeypatch):
    dashboard_service(tmp_path, monkeypatch)

    settings = app_module.settings_summary()
    first_run = settings["firstRunWizard"]

    assert settings["firstRunWizardStatus"] == "placeholder_only"
    assert settings["firstRunWizardImplemented"] is False
    assert settings["setupStatePersistenceImplemented"] is False
    assert settings["writesConfigFiles"] is False
    assert settings["tokenGenerationImplemented"] is False
    assert settings["tokenPersistenceImplemented"] is False
    assert settings["accountSetupImplemented"] is False
    assert settings["oauthImplemented"] is False
    assert settings["cloudSyncEnabled"] is False
    assert settings["telemetryEnabled"] is False
    assert settings["autoUpdaterEnabled"] is False
    assert first_run["firstRunWizardStatus"] == "placeholder_only"
    assert first_run["checklistIsInformationalOnly"] is True
    assert first_run["mutationEndpointsImplemented"] is False


def test_settings_summary_reports_packaging_placeholder_status(tmp_path, monkeypatch):
    dashboard_service(tmp_path, monkeypatch)

    settings = app_module.settings_summary()
    packaging = settings["privateAlphaPackaging"]

    assert settings["privateAlphaPackagingStatus"] == "placeholder_only"
    assert settings["installerPackagingStatus"] == "placeholder_only"
    assert settings["installerBuildImplemented"] is False
    assert settings["installerArtifactAvailable"] is False
    assert settings["codeSigningImplemented"] is False
    assert settings["autoUpdaterEnabled"] is False
    assert settings["telemetryEnabled"] is False
    assert settings["publicReleaseReady"] is False
    assert settings["vmValidationRequired"] is True
    assert settings["vmValidationStatus"] == "not_run_in_this_slice"
    assert settings["manualLocalRunCurrentPath"] is True
    assert settings["githubReleaseAutomationEnabled"] is False
    assert packaging["documentationOnly"] is True
    assert packaging["githubReleaseAutomationEnabled"] is False
    assert packaging["freshWindowsVmRequiredBeforePrivateAlpha"] is True


def test_settings_summary_shows_lan_protection_without_token_value(tmp_path, monkeypatch):
    token = "z" * 20
    monkeypatch.setenv("JARVIS_LAN_DASHBOARD_TOKEN", token)
    dashboard_service(tmp_path, monkeypatch)

    settings = app_module.settings_summary()
    settings_text = str(settings)

    assert settings["lanProtection"]["lanProtectionImplemented"] is True
    assert settings["lanProtection"]["lanTokenConfigured"] is True
    assert settings["lanProtection"]["lanTokenValidLength"] is True
    assert settings["lanProtection"]["queryStringTokensAccepted"] is False
    assert settings["lanProtection"]["tokenValueExposed"] is False
    assert token not in settings_text


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
    page_text = page.body.decode("utf-8").lower()

    assert all(action["available"] is False for action in summary["unsupportedActions"])
    assert 'id="stop-task-button" type="button" disabled' in page_text
    assert "git push" not in page_text
    assert 'id="proposal-form"' not in page_text
    assert 'id="memory-edit-form"' not in page_text
    assert "launch desktop" not in page_text
    assert "install tauri" not in page_text
    assert "update app" not in page_text
    assert "install now" not in page_text
    assert "build installer" not in page_text
    assert "publish release" not in page_text
    assert "download installer" not in page_text
    assert "sign build" not in page_text
    assert "generate token" not in page_text
    assert "create account" not in page_text
    assert "finish setup" not in page_text
    assert "auto-updater enabled" not in page_text
    assert "taskkill" not in page_text
    assert "process name" not in page_text


def test_dashboard_html_includes_settings_status_section(tmp_path, monkeypatch):
    dashboard_service(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8").lower()

    assert 'id="settings-status"' in page_text
    assert "settings / status" in page_text
    assert 'id="lan-protection"' in page_text
    assert "lan protection" in page_text
    assert 'id="stop-task-control"' in page_text
    assert "active task / stop task" in page_text
    assert 'id="desktop-shell-status"' in page_text
    assert "desktop shell / tauri" in page_text
    assert 'id="first-run-status"' in page_text
    assert "first-run / setup" in page_text
    assert 'id="private-alpha-packaging-status"' in page_text
    assert "private alpha / packaging" in page_text
    assert "/setup/first-run" in page_text
    assert "/api/tasks/" in page_text
    assert "/setup/lan" in page_text
    assert "/api/dashboard/summary" in page_text


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


def test_dashboard_reports_truthful_memory_capability_metadata(tmp_path, monkeypatch):
    dashboard_service(tmp_path, monkeypatch)

    summary = app_module.dashboard_summary()
    settings = app_module.settings_summary()

    assert summary["capabilities"]["dashboard"] == "local_operations_with_explicit_memory_controls"
    assert summary["capabilities"]["memoryCenter"] == "explicit_user_controlled_persistence"
    assert settings["memoryCenterStatus"] == "implemented_approval_gated"
    assert settings["durableMemoryPersistenceImplemented"] is True
    assert settings["automaticMemorySavingEnabled"] is False
    assert settings["memoryApprovalRequired"] is True
    assert settings["memoryAgentRetrievalImplemented"] is False
    assert settings["privateSessionPersistenceImplemented"] is False
    assert settings["automaticLearningEnabled"] is False
    assert settings["memoryCenterEndpoint"] == "/memory"
    assert settings["settingsEditable"] is False
    assert settings["externalConnectorsEnabled"] is False
    assert settings["nonCodingConnectorsImplemented"] is False


def test_main_dashboard_has_memory_center_card_and_status_section(tmp_path, monkeypatch):
    dashboard_service(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8")

    assert "Local operations dashboard with explicit approval-gated memory controls" in page_text
    assert '<a href="/memory">Open Memory Center</a>' in page_text
    assert "Approval-gated local memory management." in page_text
    assert 'id="memory-center"' in page_text
    assert 'data-section-title="Memory Center"' in page_text
    assert 'id="memory-center-status"' in page_text
    assert 'id="memory-center-metrics"' in page_text
    assert 'id="memory-center-refresh-button"' in page_text
    assert "Persistent local feature with explicit user actions only." in page_text
    assert "New memories remain pending and inactive until approved." in page_text
    assert "Automatic response-agent retrieval is not yet enabled." in page_text
    assert "fetch('/api/memory/summary')" in page_text
    assert "async function loadMemoryCenterSummary()" in page_text
    assert "function renderMemoryCenterSummary(summary)" in page_text


def test_main_dashboard_does_not_expose_memory_mutation_forms(tmp_path, monkeypatch):
    dashboard_service(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8")

    forbidden = (
        "/api/memories/proposals",
        "/api/memories/{memory_id}",
        "Approve memory",
        "Reject memory",
        "Disable memory",
        "Enable memory",
        "Delete permanently",
        'id="proposal-form"',
        'id="memory-edit-form"',
        'id="delete-confirm-input"',
    )
    assert all(item not in page_text for item in forbidden)
    assert "fetch('/api/memory/summary')" in page_text


def test_existing_dashboard_boundaries_remain_unchanged_with_memory_center(tmp_path, monkeypatch):
    dashboard_service(tmp_path, monkeypatch)

    summary = app_module.dashboard_summary()

    assert summary["capabilities"]["settings"] == "read_only_status"
    assert summary["capabilities"]["connectors"] == "placeholder_summary_only"
    assert summary["capabilities"]["stopTask"] == "jarvis_task_queue_state_only"
    assert summary["capabilities"]["desktopShell"] == "placeholder_only"
    assert summary["capabilities"]["privateAlphaPackaging"] == "placeholder_only"
    assert summary["safety"]["connectorExecution"] is False
    assert summary["safety"]["paidApis"] is False
