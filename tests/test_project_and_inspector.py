import sqlite3
from pathlib import Path

import pytest

from jarvis_core.inspector import inspect_project, plan_checks, write_markdown_report
from jarvis_core.project_registry import ProjectRegistry


def test_project_registry_validates_paths(tmp_path):
    conn = sqlite3.connect(":memory:")
    conn.execute("create table projects (name text unique, path text, created_at text default current_timestamp)")
    registry = ProjectRegistry(conn, tmp_path)
    project = tmp_path / "project"
    project.mkdir()

    saved = registry.add_project("sample", project)
    assert saved["path"] == str(project.resolve())
    assert registry.get_project("sample")["name"] == "sample"

    with pytest.raises(ValueError):
        registry.add_project("missing", tmp_path / "missing")

    with pytest.raises(ValueError):
        registry.add_project("outside", Path.cwd().anchor)


def test_package_json_scripts_are_detected(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "package.json").write_text(
        '{"scripts":{"build":"vite build","typecheck":"tsc --noEmit","test":"node test.js"}}',
        encoding="utf-8",
    )

    inspection = inspect_project(project)
    assert inspection["packageJson"] is True
    assert inspection["packageScripts"]["typecheck"] == "tsc --noEmit"
    assert inspection["checkPlan"] == ["npm run typecheck", "npm run test", "npm run build"]


def test_protected_file_detection_skips_runtime_dirs(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / ".env").write_text("SHOULD_NOT_BE_READ", encoding="utf-8")
    data_dir = project / "data"
    data_dir.mkdir()
    (data_dir / ".env").write_text("RUNTIME_SECRET", encoding="utf-8")

    inspection = inspect_project(project)

    assert inspection["protectedFilesPresent"] == [".env"]


def test_check_planner_uses_preferred_order():
    assert plan_checks({"build": "x", "lint": "x", "test": "x", "typecheck": "x"}) == [
        "npm run typecheck",
        "npm run lint",
        "npm run test",
        "npm run build",
    ]


def test_report_required_sections_validate(tmp_path):
    inspection = {
        "path": str(tmp_path),
        "git": {"available": True, "isRepository": False},
        "packageScripts": {"test": "pytest"},
        "protectedFilesPresent": [".env"],
        "checkPlan": ["npm run test"],
        "codexCli": {"available": False},
    }
    report = write_markdown_report(inspection, tmp_path / "report.md")
    text = report.read_text(encoding="utf-8")
    for section in ["## Project", "## Git", "## Package Scripts", "## Protected Files Present", "## Check Plan", "## Codex CLI"]:
        assert section in text
