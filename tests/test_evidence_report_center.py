import inspect
import json

import pytest

from jarvis_core.evidence_report_center import EvidenceReportCenterService
import jarvis_core.evidence_report_center as evidence_module
import jarvis_core.redacted_diagnostics_agent as redacted_diagnostics_module


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def report_center(tmp_path):
    return EvidenceReportCenterService(tmp_path / "reports")


def by_id(index):
    return {report["reportId"]: report for report in index["reports"]}


def test_empty_reports_directory_returns_empty_index(tmp_path):
    index = report_center(tmp_path).index_reports()
    assert index["totalReports"] == 0
    assert index["reports"] == []
    assert index["reportCountsByType"] == {}


def test_indexes_known_report_metadata_types(tmp_path):
    service = report_center(tmp_path)
    root = service.reports_root
    write_text(root / "security-safety-Jarvis-20260101T000000Z.md", "# Security/Safety Review Summary\n\n## Verdict\npass\n")
    write_text(root / "validation-validation-run-abc-20260101T000000Z.md", "# Validation Run Summary\n\n## Verdict/Status\npassed\n")
    write_text(root / "private-alpha-readiness-snapshot-20260101T000000Z.md", "# Private-Alpha Readiness Snapshot\n\n- Overall Verdict: needs_evidence\n")
    write_text(root / "diagnostics-bundle-20260101T000000Z.md", "# Redacted Diagnostics Bundle\n\n## Warnings\n- None recorded.\n")
    write_text(root / "diagnostics-bundle-20260101T000000Z.json", json.dumps({"agentId": "redacted_diagnostics_agent", "bundleId": "bundle-1", "warnings": ["review"]}))
    reports = by_id(service.index_reports())
    assert reports["security-safety-Jarvis-20260101T000000Z.md"]["reportType"] == "security_safety_review"
    assert reports["validation-validation-run-abc-20260101T000000Z.md"]["reportType"] == "validation_report"
    assert reports["private-alpha-readiness-snapshot-20260101T000000Z.md"]["reportType"] == "private_alpha_readiness_snapshot"
    assert reports["diagnostics-bundle-20260101T000000Z.md"]["reportType"] == "redacted_diagnostics_bundle"
    assert reports["diagnostics-bundle-20260101T000000Z.json"]["reportType"] == "redacted_diagnostics_bundle"


def test_infers_unknown_report_type_from_extension(tmp_path):
    service = report_center(tmp_path)
    write_text(service.reports_root / "closeout.md", "# Closeout\n")
    write_text(service.reports_root / "metadata.json", "{}")
    reports = by_id(service.index_reports())
    assert reports["closeout.md"]["reportType"] == "markdown_report"
    assert reports["metadata.json"]["reportType"] == "json_report"


def test_extracts_heading_title_and_status_safely(tmp_path):
    service = report_center(tmp_path)
    write_text(service.reports_root / "validation-run-local.md", "# Validation Run Summary\n\n- Status: passed\n\nSafe summary text.\n")
    metadata = service.get_report_metadata("validation-run-local.md")
    assert metadata["title"] == "Validation Run Summary"
    assert metadata["status"] == "passed"
    assert "Safe summary text" in metadata["summary"]


def test_redacts_synthetic_secrets_from_summary_and_detail(tmp_path):
    service = report_center(tmp_path)
    raw_openai = "sk-" + "a" * 24
    raw_github = "ghp_" + "b" * 24
    raw_pat = "github_pat_" + "c" * 24
    raw_bearer = "d" * 24
    raw_password = "synthetic-password-value"
    win_path = "C:" + "/Users/" + "example/private/.env"
    linux_path = "/" + "home" + "/example/private/.env"
    mac_path = "/" + "Users" + "/example/private/.env"
    content = (
        "# Secret-ish Report\n\n"
        f"OPENAI_API_KEY={raw_openai} password: {raw_password} Bearer {raw_bearer} {raw_github} {raw_pat}\n"
        f"{win_path} {linux_path} {mac_path} user@example.test OneDrive - Example Organization\n"
    )
    write_text(service.reports_root / "security-safety-secret-20260101T000000Z.md", content)
    metadata_text = json.dumps(service.get_report_metadata("security-safety-secret-20260101T000000Z.md"), sort_keys=True)
    detail_text = json.dumps(service.get_report_detail("security-safety-secret-20260101T000000Z.md"), sort_keys=True)
    for raw in [raw_openai, raw_github, raw_pat, raw_bearer, raw_password, win_path, linux_path, mac_path, "user@example.test", "Example Organization"]:
        assert raw not in metadata_text
        assert raw not in detail_text
    assert "<redacted" in detail_text

def test_markdown_detail_omits_raw_findings_notes_evidence_and_logs(tmp_path):
    service = report_center(tmp_path)
    content = (
        "# Security/Safety Review Summary\n\n"
        "Safe overview line.\n\n"
        "## Findings\n"
        "- Finding: raw synthetic finding detail\n\n"
        "## Notes\n"
        "operator note that should not be exposed\n\n"
        "## Logs\n"
        "raw log line that should not be exposed\n\n"
        "Evidence: raw evidence value that should not be exposed\n"
    )
    write_text(service.reports_root / "security-safety-raw-20260101T000000Z.md", content)

    detail = service.get_report_detail("security-safety-raw-20260101T000000Z.md")
    detail_text = json.dumps(detail, sort_keys=True)

    assert detail["contentType"] == "text/markdown"
    assert "Safe overview line" in detail_text
    for raw in ["raw synthetic finding detail", "operator note", "raw log line", "raw evidence value"]:
        assert raw not in detail_text
    assert "omitted from this detail view" in detail["content"]


def test_blocks_traversal_report_id(tmp_path):
    service = report_center(tmp_path)
    with pytest.raises(PermissionError):
        service.get_report_detail("..%2Fsecret.md")


def test_blocks_symlink_escape(tmp_path):
    service = report_center(tmp_path)
    service.reports_root.mkdir(parents=True)
    outside = tmp_path / "outside.md"
    write_text(outside, "# Outside\n")
    link = service.reports_root / "security-safety-link-20260101T000000Z.md"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable")
    assert service.index_reports()["reports"] == []
    with pytest.raises(PermissionError):
        service.get_report_detail(link.name)


def test_skips_non_report_extensions(tmp_path):
    service = report_center(tmp_path)
    write_text(service.reports_root / "runtime.log", "log")
    write_text(service.reports_root / "notes.txt", "notes")
    write_text(service.reports_root / ".hidden.md", "# Hidden")
    write_text(service.reports_root / "backup.md.bak", "# Backup")
    assert service.index_reports()["reports"] == []


def test_blocks_oversized_markdown_and_json(tmp_path):
    service = report_center(tmp_path)
    write_text(service.reports_root / "security-safety-large-20260101T000000Z.md", "# Large\n" + ("x" * (70 * 1024)))
    write_text(service.reports_root / "diagnostics-bundle-large.json", json.dumps({"value": "x" * (260 * 1024)}))
    reports = by_id(service.index_reports())
    assert reports["security-safety-large-20260101T000000Z.md"]["readable"] is False
    assert reports["security-safety-large-20260101T000000Z.md"]["blockedReason"] == "size_limit"
    assert reports["diagnostics-bundle-large.json"]["readable"] is False
    assert reports["diagnostics-bundle-large.json"]["blockedReason"] == "size_limit"


def test_json_detail_returns_safe_metadata_only(tmp_path):
    service = report_center(tmp_path)
    raw_secret = "sk-" + "e" * 24
    write_text(service.reports_root / "diagnostics-bundle-20260101T000000Z.json", json.dumps({"agentId": "redacted_diagnostics_agent", "bundleId": "bundle-1", "warnings": [f"token={raw_secret}"], "nested": {"raw": raw_secret}}))
    detail = service.get_report_detail("diagnostics-bundle-20260101T000000Z.json")
    detail_text = json.dumps(detail, sort_keys=True)
    assert detail["metadataOnly"] is True
    assert "content" not in detail
    assert raw_secret not in detail_text
    assert "nested" not in detail_text


def test_no_file_deletion_external_calls_or_command_execution_implemented():
    source = inspect.getsource(evidence_module)
    assert "subprocess" not in source
    assert "requests" not in source
    assert ".unlink(" not in source
    assert "rmtree" not in source
    assert "remove(" not in source


def test_redacted_diagnostics_agent_uses_generic_identifier_patterns():
    source = inspect.getsource(redacted_diagnostics_module)
    forbidden = [
        "OneDrive - " + "North Dakota University System",
        "Russell-" + "Desktop",
        "russe" + "@",
        "/" + "home" + "/russe",
        "/" + "Users" + "/russe",
    ]
    assert all(value not in source for value in forbidden)


