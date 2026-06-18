import sqlite3
from pathlib import Path

import pytest
from fastapi import HTTPException

import jarvis_core.app as app_module
from jarvis_core.dashboard import DashboardService
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.project_profiles import ProjectProfileService
from jarvis_core.project_registry import ProjectRegistry
from jarvis_core.security_review_agent import SecurityReviewService


def test_dashboard_profile_api_returns_safe_profile_summaries(tmp_path, monkeypatch):
    project = registered_project(tmp_path, monkeypatch)
    (project / "package.json").write_text('{"scripts":{"test":"node test.js"}}', encoding="utf-8")

    profiles = app_module.dashboard_project_profiles()

    assert profiles == [
        {
            "projectName": "sample",
            "projectType": "node",
            "detectedLanguages": ["javascript"],
            "detectedFrameworks": [],
            "packageManager": "npm",
            "preferredCheckOrder": ["npm run test"],
            "gitClean": None,
            "docsPresence": {
                "publicReadiness": {
                    "docs/public-repo-readiness.md": True,
                    "docs/public-safety-boundaries.md": True,
                },
                "security": {
                    "README.md": True,
                    "SECURITY.md": True,
                    "CONTRIBUTING.md": True,
                },
            },
            "futureConnectorsPlaceholderOnly": None,
            "recommendedMode": "assist",
            "warningCount": 0,
            "blockedReasonCount": 0,
            "boundaryStatus": {
                "rootValidated": True,
                "protectedPatternsActive": True,
                "runtimeSkipDirsActive": True,
                "blockedReasonCount": 0,
                "warningCount": 0,
                "rootStatus": "allowed",
            },
        }
    ]
    assert "projectRoot" not in profiles[0]


def test_dashboard_profile_endpoint_is_guarded():
    route = route_for("/api/projects/profiles")
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}
    assert require_dashboard_lan_access in dependency_calls


def test_security_review_trigger_for_registered_project_returns_report_summary(tmp_path, monkeypatch):
    registered_project(tmp_path, monkeypatch)

    response = app_module.run_dashboard_project_security_review("sample")

    assert response["projectName"] == "sample"
    assert response["agentId"] == "security_safety_agent"
    assert response["reviewMode"] == "read_only"
    assert response["verdict"] in {"pass", "pass_with_warnings", "needs_review", "blocked"}
    assert response["reportId"].startswith("security-safety-sample-")
    assert response["reportPath"]
    assert "findingsBySeverity" in response


def test_security_review_trigger_rejects_unknown_project(tmp_path, monkeypatch):
    configure_services(tmp_path, monkeypatch)

    with pytest.raises(HTTPException) as exc_info:
        app_module.run_dashboard_project_security_review("missing")

    assert exc_info.value.status_code == 404


def test_security_review_dashboard_endpoint_rejects_out_of_bound_registered_path(tmp_path, monkeypatch):
    project = tmp_path / "project"
    project.mkdir()
    add_docs(project)
    configure_services(tmp_path / "allowed", monkeypatch)
    monkeypatch.setattr(app_module, "projects", FakeRegistry({"name": "sample", "path": str(project)}))

    with pytest.raises(HTTPException) as exc_info:
        app_module.run_dashboard_project_security_review("sample")

    assert exc_info.value.status_code == 400
    assert "allowed workspace root" in exc_info.value.detail


def test_dashboard_html_includes_profile_and_security_review_sections(tmp_path, monkeypatch):
    configure_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8").lower()

    assert 'id="project-profiles"' in page_text
    assert "project profiles" in page_text
    assert 'id="security-safety-review"' in page_text
    assert "security/safety review" in page_text
    assert "/api/projects/profiles" in page_text
    assert "/security-review" in page_text


def test_dashboard_html_does_not_expose_unsupported_future_connector_controls(tmp_path, monkeypatch):
    configure_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8").lower()

    assert "enable connectors" not in page_text
    assert "send email" not in page_text
    assert "payment" not in page_text
    assert "git push" not in page_text


def test_dashboard_api_does_not_include_raw_secret_values(tmp_path, monkeypatch):
    project = registered_project(tmp_path, monkeypatch)
    token = "sk-" + "test-placeholder-value"
    (project / "settings.py").write_text('OPENAI_API_KEY = "' + token + '"\n', encoding="utf-8")

    profile_text = str(app_module.dashboard_project_profiles())
    review_text = str(app_module.run_dashboard_project_security_review("sample"))

    assert token not in profile_text
    assert token not in review_text
    assert "<redacted>" not in review_text


def test_dashboard_api_does_not_read_protected_file_contents(tmp_path, monkeypatch):
    project = registered_project(tmp_path, monkeypatch)
    token = "sk-" + "test-placeholder-value"
    (project / ".env").write_text("OPENAI_API_KEY=" + token + "\n", encoding="utf-8")

    profile_text = str(app_module.dashboard_project_profiles())
    review = app_module.run_dashboard_project_security_review("sample")
    review_text = str(review)

    assert token not in profile_text
    assert token not in review_text
    assert review["findingCount"] >= 1


def test_dashboard_security_review_routes_are_guarded():
    protected_paths = {
        "/api/projects/{name}/security-review",
        "/api/projects/{name}/security-review/latest",
    }
    routes = {route.path: route for route in app_module.app.routes if getattr(route, "path", None) in protected_paths}

    assert set(routes) == protected_paths
    for route in routes.values():
        dependency_calls = {dependency.call for dependency in route.dependant.dependencies}
        assert require_dashboard_lan_access in dependency_calls


def test_latest_security_review_summary_uses_existing_report_metadata(tmp_path, monkeypatch):
    registered_project(tmp_path, monkeypatch)
    created = app_module.run_dashboard_project_security_review("sample")

    latest = app_module.latest_dashboard_project_security_review("sample")

    assert latest["available"] is True
    assert latest["reportId"] == created["reportId"]
    assert latest["sizeBytes"] > 0


def registered_project(tmp_path: Path, monkeypatch):
    project = tmp_path / "project"
    project.mkdir()
    add_docs(project)
    registry = configure_services(tmp_path, monkeypatch)
    registry.add_project("sample", project)
    return project


def configure_services(workspace_root: Path, monkeypatch) -> ProjectRegistry:
    workspace_root.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(":memory:")
    conn.execute("create table projects (name text unique, path text, created_at text default current_timestamp)")
    registry = ProjectRegistry(conn, workspace_root)
    data_root = workspace_root / "data" / "jarvis"
    monkeypatch.setattr(app_module, "projects", registry)
    monkeypatch.setattr(app_module, "project_profiles", ProjectProfileService(workspace_root, workspace_root / "connectors"))
    monkeypatch.setattr(app_module, "security_reviews", SecurityReviewService(data_root / "reports", workspace_root, workspace_root / "connectors"))
    monkeypatch.setattr(app_module, "DATA_ROOT", data_root)
    monkeypatch.setattr(app_module, "dashboard", DashboardService(conn, workspace_root, data_root, workspace_root / "connectors"))
    return registry


def add_docs(project: Path) -> None:
    for relative in [
        "README.md",
        "SECURITY.md",
        "CONTRIBUTING.md",
        "docs/public-repo-readiness.md",
        "docs/public-safety-boundaries.md",
    ]:
        path = project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("Local-only project documentation.\n", encoding="utf-8")


def route_for(path: str):
    for route in app_module.app.routes:
        if getattr(route, "path", None) == path:
            return route
    raise AssertionError(f"route not found: {path}")


class FakeRegistry:
    def __init__(self, project: dict[str, str]):
        self.project = project

    def get_project(self, name: str):
        return self.project if name == self.project["name"] else None

    def list_projects(self):
        return [self.project]
