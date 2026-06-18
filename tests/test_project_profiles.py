import json
import sqlite3
from pathlib import Path

import pytest
from fastapi import HTTPException

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.project_profiles import ProjectProfileService
from jarvis_core.project_registry import ProjectRegistry


def test_clean_synthetic_python_project_profile_is_generated(tmp_path):
    project = tmp_path / "python-project"
    project.mkdir()
    (project / "pyproject.toml").write_text("[project]\nname = 'sample'\n", encoding="utf-8")
    (project / "requirements.txt").write_text("fastapi\npytest\n", encoding="utf-8")
    (project / "tests").mkdir()
    add_docs(project)

    profile = service(tmp_path).generate_profile(project, "sample")

    assert profile.root_validated is True
    assert profile.project_type == "python"
    assert profile.detected_languages == ["python"]
    assert "fastapi" in profile.detected_frameworks
    assert "pytest" in profile.detected_frameworks
    assert profile.preferred_check_order == ["python -m pytest"]
    assert profile.recommended_mode == "assist"


def test_clean_node_project_detects_scripts_and_check_order(tmp_path):
    project = tmp_path / "node-project"
    project.mkdir()
    (project / "package.json").write_text(
        json.dumps({"scripts": {"build": "vite build", "test": "vitest", "lint": "eslint .", "typecheck": "tsc --noEmit"}, "devDependencies": {"vite": "1.0.0"}}),
        encoding="utf-8",
    )
    add_docs(project)

    profile = service(tmp_path).generate_profile(project, "node")

    assert profile.project_type == "node"
    assert profile.package_manager == "npm"
    assert profile.package_scripts["test"] == "vitest"
    assert profile.preferred_check_order == ["npm run typecheck", "npm run lint", "npm run test", "npm run build"]
    assert "vite" in profile.detected_frameworks


def test_path_outside_workspace_returns_blocked_profile(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    outside_root = tmp_path / "outside-root"
    outside_root.mkdir()

    profile = ProjectProfileService(project).generate_profile(outside_root, "outside")

    assert profile.root_validated is False
    assert profile.project_type == "unknown"
    assert "allowed workspace root" in profile.blocked_reasons[0]


def test_symlink_escape_outside_project_is_blocked_or_skipped(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "package.json").write_text(json.dumps({"scripts": {"test": "node outside.js"}}), encoding="utf-8")
    link = project / "package.json"
    try:
        link.symlink_to(outside / "package.json")
    except OSError as exc:
        pytest.skip(f"symlinks unavailable: {exc}")

    profile = service(tmp_path).generate_profile(project, "symlink")

    assert profile.package_scripts == {}


def test_protected_file_contents_are_not_read(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    token = "sk-" + "test-placeholder-value"
    (project / ".env").write_text("OPENAI_API_KEY=" + token + "\n", encoding="utf-8")

    profile = service(tmp_path).generate_profile(project, "protected")

    assert token not in str(profile.to_dict())
    assert ".env" in profile.protected_patterns


def test_runtime_cache_directories_do_not_influence_profile(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    node_modules = project / "node_modules"
    node_modules.mkdir()
    (node_modules / "package.json").write_text(json.dumps({"scripts": {"build": "should-not-count"}}), encoding="utf-8")

    profile = service(tmp_path).generate_profile(project, "runtime")

    assert profile.package_scripts == {}
    assert profile.project_type == "unknown"


def test_missing_optional_docs_create_warnings_not_blockers(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "pyproject.toml").write_text("[project]\nname = 'sample'\n", encoding="utf-8")

    profile = service(tmp_path).generate_profile(project, "warnings")

    assert profile.root_validated is True
    assert profile.blocked_reasons == []
    assert profile.warnings
    assert profile.recommended_mode == "observe"


def test_public_readiness_docs_presence_is_detected(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    add_docs(project)

    profile = service(tmp_path).generate_profile(project, "docs")

    assert profile.public_readiness_docs_present["docs/public-repo-readiness.md"] is True
    assert profile.public_readiness_docs_present["docs/public-safety-boundaries.md"] is True
    assert profile.security_docs_present["SECURITY.md"] is True


def test_connector_placeholder_status_is_detected(tmp_path):
    project = tmp_path / "project"
    placeholders = project / "connectors" / "placeholders"
    placeholders.mkdir(parents=True)
    (placeholders / "gmail.json").write_text(json.dumps(connector()), encoding="utf-8")

    profile = service(tmp_path).generate_profile(project, "connectors")

    assert profile.future_connectors_placeholder_only is True


def test_profile_endpoint_uses_registered_project(tmp_path, monkeypatch):
    project = tmp_path / "project"
    project.mkdir()
    add_docs(project)
    conn = sqlite3.connect(":memory:")
    conn.execute("create table projects (name text unique, path text, created_at text default current_timestamp)")
    registry = ProjectRegistry(conn, tmp_path)
    registry.add_project("sample", project)
    monkeypatch.setattr(app_module, "projects", registry)
    monkeypatch.setattr(app_module, "project_profiles", service(tmp_path))

    response = app_module.get_project_profile("sample")

    assert response["projectName"] == "sample"
    assert response["rootValidated"] is True


def test_profile_endpoint_rejects_unknown_project(tmp_path, monkeypatch):
    conn = sqlite3.connect(":memory:")
    conn.execute("create table projects (name text unique, path text, created_at text default current_timestamp)")
    monkeypatch.setattr(app_module, "projects", ProjectRegistry(conn, tmp_path))
    monkeypatch.setattr(app_module, "project_profiles", service(tmp_path))

    with pytest.raises(HTTPException) as exc_info:
        app_module.get_project_profile("missing")

    assert exc_info.value.status_code == 404


def test_profile_endpoint_rejects_out_of_bound_registered_project(tmp_path, monkeypatch):
    project = tmp_path / "project"
    project.mkdir()
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    conn = sqlite3.connect(":memory:")
    conn.execute("create table projects (name text unique, path text, created_at text default current_timestamp)")
    registry = ProjectRegistry(conn, tmp_path)
    registry.add_project("sample", project)
    monkeypatch.setattr(app_module, "projects", registry)
    monkeypatch.setattr(app_module, "project_profiles", ProjectProfileService(allowed))

    with pytest.raises(HTTPException) as exc_info:
        app_module.get_project_profile("sample")

    assert exc_info.value.status_code == 400


def test_profile_routes_use_dashboard_lan_guard():
    protected_paths = {"/projects/{name}/profile", "/projects/{name}/profile/refresh"}
    routes = {route.path: route for route in app_module.app.routes if getattr(route, "path", None) in protected_paths}

    assert set(routes) == protected_paths
    for route in routes.values():
        dependency_calls = {dependency.call for dependency in route.dependant.dependencies}
        assert require_dashboard_lan_access in dependency_calls


def service(workspace_root: Path) -> ProjectProfileService:
    return ProjectProfileService(workspace_root, workspace_root / "connectors")


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


def connector() -> dict[str, object]:
    return {
        "id": "gmail",
        "provider": "Gmail",
        "implemented": False,
        "defaultEnabled": False,
        "readinessLevel": "placeholder_only",
    }
