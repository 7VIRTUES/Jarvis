from pathlib import Path

import pytest

from jarvis_core.workspace_boundary import WorkspaceBoundaryValidator


def test_path_inside_project_is_allowed(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    source = project / "src" / "app.py"
    source.parent.mkdir()
    source.write_text("print('ok')\n", encoding="utf-8")

    decision = WorkspaceBoundaryValidator(project, tmp_path).check_path(source)

    assert decision.allowed is True
    assert decision.relative_path == "src/app.py"


def test_path_traversal_outside_project_is_blocked(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("outside\n", encoding="utf-8")

    decision = WorkspaceBoundaryValidator(project, tmp_path).check_path(project / ".." / "outside.txt")

    assert decision.allowed is False
    assert decision.status == "blocked"
    assert "escapes" in decision.reason


def test_symlink_escape_is_blocked_or_skipped_when_unavailable(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.txt").write_text("placeholder\n", encoding="utf-8")
    link = project / "linked-outside"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlinks unavailable: {exc}")

    decision = WorkspaceBoundaryValidator(project, tmp_path).check_path(link / "secret.txt")

    assert decision.allowed is False
    assert "escapes" in decision.reason


def test_protected_filename_is_blocked_by_path_only(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    protected = project / ".env"
    protected.write_text("SHOULD_NOT_BE_READ\n", encoding="utf-8")

    decision = WorkspaceBoundaryValidator(project, tmp_path).check_path(protected)

    assert decision.allowed is False
    assert decision.protected is True
    assert "protected file contents" in decision.reason


def test_runtime_cache_directory_is_skipped(tmp_path):
    project = tmp_path / "project"
    cache = project / "node_modules"
    cache.mkdir(parents=True)
    file_path = cache / "package.json"
    file_path.write_text("{}", encoding="utf-8")

    decision = WorkspaceBoundaryValidator(project, tmp_path).check_path(file_path)

    assert decision.allowed is False
    assert decision.skipped is True
    assert "runtime/cache" in decision.reason


def test_safe_metadata_allows_known_metadata_files(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    package_json = project / "package.json"
    package_json.write_text("{}", encoding="utf-8")

    decision = WorkspaceBoundaryValidator(project, tmp_path).safe_to_read_metadata(package_json)

    assert decision.allowed is True
    assert decision.relative_path == "package.json"


def test_safe_text_scan_rejects_binary_file(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    binary = project / "notes.txt"
    binary.write_bytes(b"hello\x00world")

    decision = WorkspaceBoundaryValidator(project, tmp_path).safe_to_scan_text(binary)

    assert decision.allowed is False
    assert decision.skipped is True
    assert "binary" in decision.reason
