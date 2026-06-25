import json
import inspect

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.db import init_db
from jarvis_core.file_data_agent import FileDataAgentService
from jarvis_core.project_registry import ProjectRegistry


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def app_services(tmp_path, monkeypatch):
    conn = init_db(tmp_path / "jarvis.sqlite")
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    project_root = workspace / "sample"
    project_root.mkdir()
    registry = ProjectRegistry(conn, workspace)
    registry.add_project("sample", project_root)
    service = FileDataAgentService(registry, workspace)
    monkeypatch.setattr(app_module, "file_data_agent", service)
    return conn, workspace, project_root, registry, service


def test_file_data_summary_uses_registered_project_only(tmp_path, monkeypatch):
    _conn, _workspace, project_root, _registry, service = app_services(tmp_path, monkeypatch)
    write_text(project_root / "README.md", "# Sample\n\nLocal project.")
    write_text(project_root / "src" / "app.py", "print('local')\n")

    summary = service.local_summary("sample")

    assert summary["agentId"] == "file_data_agent"
    assert summary["status"] == "local_only"
    assert summary["mode"] == "registered_project_metadata_only"
    assert summary["projectName"] == "sample"
    assert summary["projectRoot"] == str(project_root.resolve())
    assert summary["scannedFiles"] == 2
    assert summary["fileTypeCounts"] == {".md": 1, ".py": 1}
    assert summary["safety"]["registeredProjectsOnly"] is True
    assert summary["safety"]["rawPathInputAccepted"] is False


def test_file_data_endpoint_rejects_unknown_project(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    with pytest.raises(HTTPException) as exc_info:
        app_module.create_file_data_summary(app_module.FileDataSummaryInput(projectName="missing"))

    assert exc_info.value.status_code == 404
    assert "registered project not found" in exc_info.value.detail


def test_file_data_request_rejects_raw_path_input():
    with pytest.raises(ValidationError):
        app_module.FileDataSummaryInput.model_validate({"projectName": "sample", "path": "C:/dev/Jarvis"})


def test_file_data_summary_blocks_registered_path_outside_workspace(tmp_path, monkeypatch):
    conn, workspace, _project_root, _registry, service = app_services(tmp_path, monkeypatch)
    outside = tmp_path / "outside"
    outside.mkdir()
    conn.execute("insert into projects (name, path) values (?, ?)", ("outside", str(outside)))
    conn.commit()

    with pytest.raises(PermissionError) as exc_info:
        service.local_summary("outside")

    assert "allowed workspace root" in str(exc_info.value)
    assert not outside.resolve().is_relative_to(workspace.resolve())


def test_file_data_summary_skips_protected_files_without_reading_contents(tmp_path, monkeypatch):
    _conn, _workspace, project_root, _registry, service = app_services(tmp_path, monkeypatch)
    secret = "SUPER_SECRET_TOKEN_VALUE"
    write_text(project_root / ".env", f"SECRET={secret}\n")
    write_text(project_root / "notes.txt", "ordinary notes\n")

    summary = service.local_summary("sample")
    summary_text = json.dumps(summary)

    assert summary["scannedFiles"] == 1
    assert summary["skippedFiles"] == 1
    assert summary["protectedSkippedFiles"] == 1
    assert summary["fileTypeCounts"] == {".txt": 1}
    assert "Protected file patterns were detected and skipped." in summary["warnings"]
    assert secret not in summary_text


def test_file_data_summary_skips_runtime_and_noisy_directories(tmp_path, monkeypatch):
    _conn, _workspace, project_root, _registry, service = app_services(tmp_path, monkeypatch)
    write_text(project_root / "README.md", "# Sample\n")
    write_text(project_root / "node_modules" / "pkg" / "index.js", "module.exports = {}\n")
    write_text(project_root / ".next" / "cache" / "page.js", "cache\n")
    write_text(project_root / ".jarvis" / "runtime" / "state.json", "{}\n")
    write_text(project_root / "coverage" / "coverage.json", "{}\n")

    summary = service.local_summary("sample")

    assert summary["fileTypeCounts"] == {".md": 1}
    assert summary["runtimeSkippedDirs"] == 4
    assert {"node_modules", ".next", ".jarvis", "coverage"}.issubset(set(summary["skippedDirList"]))
    assert "Runtime, dependency, cache, or build directories were skipped." in summary["warnings"]


def test_file_data_summary_returns_bounded_readme_and_direct_docs_metadata(tmp_path, monkeypatch):
    _conn, _workspace, project_root, _registry, service = app_services(tmp_path, monkeypatch)
    write_text(project_root / "README.md", "# Sample Project\n\n" + ("A" * 800))
    write_text(project_root / "docs" / "guide.md", "# Guide\n\nSafe docs text.")
    write_text(project_root / "docs" / "nested" / "deep.md", "# Nested\n\nShould not be included.")
    write_text(project_root / "docs" / ".env", "SECRET=hidden\n")

    summary = service.local_summary("sample")
    docs = {doc["relativePath"]: doc for doc in summary["docsDetected"]}
    summary_text = json.dumps(summary)

    assert set(docs) == {"README.md", "docs/guide.md"}
    assert docs["README.md"]["title"] == "Sample Project"
    assert docs["docs/guide.md"]["title"] == "Guide"
    assert len(docs["README.md"]["preview"]) <= 400
    assert "Should not be included" not in summary_text
    assert "SECRET=hidden" not in summary_text


def test_file_data_agent_source_has_no_external_shell_or_mutation_behavior():
    source = inspect.getsource(__import__("jarvis_core.file_data_agent").file_data_agent).lower()
    forbidden = [
        "requests",
        "httpx",
        "urllib.request",
        "socket",
        "subprocess",
        "open(",
        ".write(",
        "write_text",
        "unlink(",
        "remove(",
        "rmdir(",
        "openai",
        "anthropic",
        "gemini",
    ]

    assert all(token not in source for token in forbidden)
