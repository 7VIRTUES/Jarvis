import subprocess

from jarvis_core.post_execution_review import build_safe_check_plan, review_post_codex_diff
from jarvis_core.reports import REQUIRED_IMPLEMENTATION_REPORT_SECTIONS, missing_implementation_report_sections


def init_repo(path):
    path.mkdir()
    subprocess.run(["git", "init"], cwd=path, shell=False, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "jarvis@example.invalid"], cwd=path, shell=False, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Jarvis Tests"], cwd=path, shell=False, check=True, capture_output=True, text=True)


def commit_all(path, message="baseline"):
    subprocess.run(["git", "add", "."], cwd=path, shell=False, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", message], cwd=path, shell=False, check=True, capture_output=True, text=True)


def test_diff_within_risk_budget_allows_check_planning(tmp_path):
    project = tmp_path / "project"
    init_repo(project)
    (project / "package.json").write_text(
        '{"scripts":{"test":"node test.js","lint":"eslint .","build":"vite build","typecheck":"tsc --noEmit"}}',
        encoding="utf-8",
    )
    (project / "src.txt").write_text("before\n", encoding="utf-8")
    commit_all(project)
    (project / "src.txt").write_text("before\nafter\n", encoding="utf-8")

    review = review_post_codex_diff(
        project,
        {"test": "node test.js", "lint": "eslint .", "build": "vite build", "typecheck": "tsc --noEmit"},
    )

    assert review["checksMayProceed"] is True
    assert review["requiresUserReview"] is False
    assert [check["name"] for check in review["checkPlan"]["checks"]] == ["typecheck", "lint", "test", "build"]


def test_too_many_changed_files_stops_workflow(tmp_path):
    project = tmp_path / "project"
    init_repo(project)
    for index in range(3):
        (project / f"file-{index}.txt").write_text("baseline\n", encoding="utf-8")
    commit_all(project)
    for index in range(3):
        (project / f"file-{index}.txt").write_text("changed\n", encoding="utf-8")

    review = review_post_codex_diff(project, {}, budget={"maxChangedFiles": 2})

    assert review["checksMayProceed"] is False
    assert review["requiresUserReview"] is True
    assert any("changedFiles=3" in reason for reason in review["reasons"])


def test_too_many_diff_lines_stops_workflow(tmp_path):
    project = tmp_path / "project"
    init_repo(project)
    (project / "big.txt").write_text("one\n", encoding="utf-8")
    commit_all(project)
    (project / "big.txt").write_text("\n".join(str(index) for index in range(12)) + "\n", encoding="utf-8")

    review = review_post_codex_diff(project, {}, budget={"maxDiffLines": 5})

    assert review["checksMayProceed"] is False
    assert review["diffLines"] > 5
    assert any("diffLines=" in reason for reason in review["reasons"])


def test_untracked_file_lines_count_toward_diff_budget(tmp_path):
    project = tmp_path / "project"
    init_repo(project)
    (project / "README.md").write_text("baseline\n", encoding="utf-8")
    commit_all(project)
    (project / "new.txt").write_text("\n".join(str(index) for index in range(8)) + "\n", encoding="utf-8")

    review = review_post_codex_diff(project, {}, budget={"maxDiffLines": 5})

    assert review["checksMayProceed"] is False
    assert review["diffLines"] == 8


def test_protected_file_change_stops_workflow_without_reading_contents(tmp_path):
    project = tmp_path / "project"
    init_repo(project)
    (project / "README.md").write_text("baseline\n", encoding="utf-8")
    commit_all(project)
    (project / ".env").write_text("SECRET_VALUE_SHOULD_NOT_APPEAR=1\n", encoding="utf-8")

    review = review_post_codex_diff(project, {})

    assert review["checksMayProceed"] is False
    assert review["protectedFilesChanged"] == [".env"]
    assert "SECRET_VALUE_SHOULD_NOT_APPEAR" not in str(review)


def test_dependency_file_change_stops_workflow_for_review(tmp_path):
    project = tmp_path / "project"
    init_repo(project)
    (project / "package.json").write_text('{"scripts":{"test":"node test.js"}}\n', encoding="utf-8")
    commit_all(project)
    (project / "package.json").write_text('{"scripts":{"test":"node test.js"},"dependencies":{"x":"1.0.0"}}\n', encoding="utf-8")

    review = review_post_codex_diff(project, {"test": "node test.js"})

    assert review["checksMayProceed"] is False
    assert review["dependencyFilesChanged"] == ["package.json"]
    assert any("dependency/package" in reason for reason in review["reasons"])


def test_safe_check_plan_uses_only_detected_scripts_and_empty_reason():
    plan = build_safe_check_plan({"test": "node test.js", "start": "vite"})
    empty = build_safe_check_plan({})

    assert [check["command"] for check in plan["checks"]] == ["npm run test"]
    assert empty["checks"] == []
    assert empty["reason"] == "no detected package scripts for safe checks"


def test_final_report_required_sections_are_enforced():
    report = "\n".join(f"## {section}" for section in REQUIRED_IMPLEMENTATION_REPORT_SECTIONS)

    assert missing_implementation_report_sections(report) == []
    assert "What each file change did" in missing_implementation_report_sections("## Summary")
