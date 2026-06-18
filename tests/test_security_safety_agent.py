import json
from pathlib import Path

import pytest
from fastapi import HTTPException

import jarvis_core.app as app_module
from jarvis_core.db import init_db
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.project_registry import ProjectRegistry
from jarvis_core.security_review_agent import SecurityReviewService


def test_clean_synthetic_project_returns_pass_or_warnings(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    for relative in [
        "README.md",
        "SECURITY.md",
        "CONTRIBUTING.md",
        "docs/public-repo-readiness.md",
        "docs/public-safety-boundaries.md",
    ]:
        path = project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("Local-only placeholder docs.\n", encoding="utf-8")

    result = service(tmp_path).review_project(project, "clean")

    assert result.verdict in {"pass", "pass_with_warnings"}
    assert result.protected_file_scan["matchedCount"] == 0
    assert result.secret_pattern_scan["matchedCount"] == 0
    assert result.private_path_scan["matchedCount"] == 0


def test_protected_filename_is_reported_without_reading_contents(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    protected = project / ".env"
    protected.write_text("OPENAI_API_KEY=" + fake_token() + "\n", encoding="utf-8")

    result = service(tmp_path).review_project(project, "protected")
    report_text = service(tmp_path).markdown_report(result)

    assert ".env" in result.protected_file_scan["matchedPaths"]
    assert result.protected_file_scan["contentsRead"] is False
    assert result.secret_pattern_scan["matchedCount"] == 0
    assert fake_token() not in report_text


def test_likely_secret_pattern_is_detected_with_redacted_value(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "settings.py").write_text('OPENAI_API_KEY = "' + fake_token() + '"\n', encoding="utf-8")

    result = service(tmp_path).review_project(project, "secret")
    match = result.secret_pattern_scan["matches"][0]
    report_text = service(tmp_path).markdown_report(result)

    assert match["match"] == "openai_api_key"
    assert match["snippet"] == 'OPENAI_API_KEY = "<redacted>"'
    assert fake_token() not in str(result.to_dict())
    assert fake_token() not in report_text


def test_private_local_path_is_detected_and_redacted(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    private_path = "C:" + "/Users/" + "Someone" + "/Jarvis"
    (project / "notes.md").write_text(f"Local path: {private_path}\n", encoding="utf-8")

    result = service(tmp_path).review_project(project, "private-path")
    match = result.private_path_scan["matches"][0]

    assert match["match"] == "windows_user_path"
    assert "<redacted-user-path>" in match["snippet"]
    assert private_path not in str(result.to_dict())


def test_future_connector_enabled_or_implemented_is_reported(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    connectors = project / "connectors" / "placeholders"
    connectors.mkdir(parents=True)
    (connectors / "gmail.json").write_text(json.dumps(connector(implemented=True)), encoding="utf-8")

    result = service(tmp_path).review_project(project, "connector")

    assert result.verdict == "blocked"
    assert result.connector_placeholder_scan["unexpectedEnabledOrImplemented"][0]["implemented"] is True
    assert any(finding.category == "connector_placeholder" for finding in result.findings)


def test_missing_public_readiness_docs_are_reported(tmp_path):
    project = tmp_path / "project"
    project.mkdir()

    result = service(tmp_path).review_project(project, "missing-docs")

    assert "README.md" in result.public_readiness_docs_scan["missing"]
    assert any(finding.category == "public_readiness_docs" for finding in result.findings)


def test_boundary_wording_is_not_treated_as_unsafe_public_claim(tmp_path):
    project = tmp_path / "project"
    docs = project / "docs"
    docs.mkdir(parents=True)
    (docs / "safety.md").write_text(
        "No production-ready release is included.\n"
        "OAuth is not implemented.\n"
        "Cloud sync is not included.\n"
        "Telemetry is disabled.\n",
        encoding="utf-8",
    )

    result = service(tmp_path).review_project(project, "boundary-docs")

    assert result.public_release_claim_scan["riskyClaimCount"] == 0
    assert result.public_release_claim_scan["acceptableBoundaryReferenceCount"] == 4
    assert not [finding for finding in result.findings if finding.category == "public_release_claim"]


def test_report_generation_excludes_raw_secret_values(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    token = fake_token()
    (project / "settings.py").write_text('client_secret = "' + token + '"\n', encoding="utf-8")
    review_service = service(tmp_path)

    result = review_service.review_project(project, "report-secret")
    report_path = review_service.write_markdown_report(result)
    report_text = report_path.read_text(encoding="utf-8")

    assert result.report_id.startswith("security-safety-report-secret-")
    assert token not in report_text
    assert "<redacted>" in report_text


def test_scanner_skips_protected_file_contents(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    token = fake_token()
    (project / "id_rsa").write_text("Bearer " + token + "\n", encoding="utf-8")

    result = service(tmp_path).review_project(project, "skip-protected")

    assert "id_rsa" in result.protected_file_scan["matchedPaths"]
    assert result.secret_pattern_scan["matchedCount"] == 0
    assert token not in str(result.to_dict())


def test_scanner_skips_dependency_runtime_and_cache_dirs(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    for directory in ["node_modules", "data", ".pytest_cache"]:
        path = project / directory
        path.mkdir()
        (path / "settings.py").write_text('secret_key = "' + fake_token() + '"\n', encoding="utf-8")

    result = service(tmp_path).review_project(project, "skip-dirs")

    assert result.secret_pattern_scan["matchedCount"] == 0


def test_security_review_endpoint_uses_registered_project_and_gets_report(tmp_path, monkeypatch):
    project = tmp_path / "project"
    project.mkdir()
    (project / "README.md").write_text("No production-ready release.\n", encoding="utf-8")
    conn = init_db(tmp_path / "jarvis.sqlite")
    registry = ProjectRegistry(conn, tmp_path)
    registry.add_project("sample", project)
    review_service = service(tmp_path)
    monkeypatch.setattr(app_module, "projects", registry)
    monkeypatch.setattr(app_module, "security_reviews", review_service)

    response = app_module.create_security_review(app_module.SecurityReviewInput(projectName="sample"))
    fetched = app_module.get_security_review(response["reportId"])

    assert response["metadata"]["agentId"] == "security_safety_agent"
    assert response["metadata"]["projectName"] == "sample"
    assert response["reportId"].startswith("security-safety-sample-")
    assert "Security/Safety Review Summary" in fetched["content"]


def test_security_review_endpoint_rejects_out_of_scope_path(tmp_path, monkeypatch):
    review_service = service(tmp_path)
    monkeypatch.setattr(app_module, "security_reviews", review_service)

    with pytest.raises(HTTPException) as exc_info:
        app_module.create_security_review(app_module.SecurityReviewInput(projectPath=str(Path.cwd().anchor)))

    assert exc_info.value.status_code == 400
    assert "allowed workspace root" in exc_info.value.detail


def test_security_review_routes_use_dashboard_lan_guard():
    protected_paths = {"/security/reviews", "/security/reviews/{review_id:path}"}
    routes = {route.path: route for route in app_module.app.routes if getattr(route, "path", None) in protected_paths}

    assert set(routes) == protected_paths
    for route in routes.values():
        dependency_calls = {dependency.call for dependency in route.dependant.dependencies}
        assert require_dashboard_lan_access in dependency_calls


def service(workspace_root: Path) -> SecurityReviewService:
    return SecurityReviewService(workspace_root / "data" / "jarvis" / "reports", workspace_root, workspace_root / "connectors")


def fake_token() -> str:
    return "sk-" + "test-placeholder-value"


def connector(implemented: bool = False, default_enabled: bool = False) -> dict[str, object]:
    return {
        "id": "gmail",
        "provider": "Gmail",
        "implemented": implemented,
        "defaultEnabled": default_enabled,
        "readinessLevel": "placeholder_only",
        "costMode": "disabled",
        "authType": "not_implemented",
        "privacyClass": "external_account",
        "dataAccess": "none",
        "approvalRequired": True,
        "tokenStorage": "not_implemented",
        "dataRetention": "none",
        "notes": "Placeholder only.",
    }
