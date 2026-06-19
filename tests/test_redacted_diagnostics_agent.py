import inspect
import json

from jarvis_core.db import init_db
from jarvis_core.redacted_diagnostics_agent import RedactedDiagnosticsBundleService
from jarvis_core.validation_agent import ValidationAgentService
import jarvis_core.redacted_diagnostics_agent as redacted_diagnostics_module


PLACEHOLDER_CONNECTOR_JSON = """{
  "id": "gmail",
  "provider": "Gmail",
  "implemented": false,
  "defaultEnabled": false,
  "readinessLevel": "placeholder_only"
}"""


def write_text(path, text="placeholder"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def create_workspace(tmp_path):
    workspace = tmp_path / "workspace"
    for relative in [
        "README.md",
        "SECURITY.md",
        "CONTRIBUTING.md",
        "docs/public-repo-readiness.md",
        "docs/public-safety-boundaries.md",
        "docs/security-safety-agent.md",
        "docs/project-profiles.md",
        "docs/dashboard-profile-security-surfaces.md",
        "docs/validation-agent.md",
        "docs/validation-dashboard-workflow.md",
        "docs/vm-validation-runbook.md",
    ]:
        write_text(workspace / relative, "Jarvis local readiness boundary. This is not production-ready.")
    write_text(workspace / "connectors" / "placeholders" / "gmail.json", PLACEHOLDER_CONNECTOR_JSON)
    write_text(workspace / "connectors" / "agents" / "redacted-diagnostics-agent.json", '{"implemented":true}')
    write_text(workspace / "connectors" / "agents" / "security-safety-agent.json", '{"implemented":true}')
    write_text(workspace / "services" / "jarvis-core" / "src" / "jarvis_core" / "project_profiles.py", "profile")
    write_text(workspace / "services" / "jarvis-core" / "src" / "jarvis_core" / "workspace_boundary.py", "boundary")
    write_text(
        workspace / "services" / "jarvis-core" / "src" / "jarvis_core" / "dashboard.py",
        "api_reports /api/reports settings-status project-profiles security-safety-review validation-agent-status Generate local report private-alpha-readiness-snapshot redacted-diagnostics-bundle",
    )
    return workspace


def diagnostics_service(tmp_path):
    conn = init_db(tmp_path / "jarvis.sqlite")
    workspace = create_workspace(tmp_path)
    reports_root = tmp_path / "data" / "jarvis" / "reports"
    service = RedactedDiagnosticsBundleService(conn, reports_root, workspace, workspace / "connectors")
    return service, conn, workspace, reports_root


def test_diagnostics_bundle_generation_works(tmp_path):
    service, conn, _workspace, _reports_root = diagnostics_service(tmp_path)
    conn.execute("insert into projects (name, path, created_at) values (?, ?, ?)", ("Jarvis", "C:/safe/Jarvis", "2026-01-01T00:00:00Z"))
    conn.commit()

    bundle = service.generate_bundle()

    assert bundle["agentId"] == "redacted_diagnostics_agent"
    assert bundle["mode"] == "local_redacted_diagnostics"
    assert bundle["summary"]["localOnly"] is True
    assert bundle["summary"]["commandExecution"] is False
    assert bundle["sections"]["appMetadata"]["appName"] == "Jarvis PC Local"
    assert bundle["sections"]["dashboardSafetySettingsSummary"]["safety"]["paidApis"] is False
    assert bundle["sections"]["projectProfileSummary"]["registeredProjectCount"] == 1


def test_report_generation_writes_markdown_and_json(tmp_path):
    service, _conn, _workspace, reports_root = diagnostics_service(tmp_path)

    report = service.write_reports()

    assert report["reportId"].startswith("diagnostics-bundle-")
    assert report["jsonReportId"].startswith("diagnostics-bundle-")
    markdown = reports_root / report["reportId"]
    json_report = reports_root / report["jsonReportId"]
    assert markdown.exists()
    assert json_report.exists()
    assert "# Redacted Diagnostics Bundle" in markdown.read_text(encoding="utf-8")
    loaded = json.loads(json_report.read_text(encoding="utf-8"))
    assert loaded["agentId"] == "redacted_diagnostics_agent"


def test_latest_report_metadata_endpoint_data_works(tmp_path):
    service, _conn, _workspace, _reports_root = diagnostics_service(tmp_path)

    report = service.write_reports()
    latest = service.get_latest_report_metadata()

    assert latest["available"] is True
    assert latest["reportId"] == report["reportId"]
    assert latest["jsonReportId"] == report["jsonReportId"]


def test_bundle_redacts_synthetic_secret_and_path_values(tmp_path):
    service, conn, _workspace, _reports_root = diagnostics_service(tmp_path)
    raw_openai = "sk-" + "a" * 24
    raw_github = "ghp_" + "b" * 24
    raw_password = "synthetic-password-value"
    private_path = "C:" + "/Users/" + "synthetic-user/Documents/Jarvis"
    conn.execute(
        "insert into projects (name, path, created_at) values (?, ?, ?)",
        (
            f"OPENAI_API_KEY={raw_openai} password: {raw_password} Bearer {raw_github} {private_path}",
            "C:/safe/Jarvis",
            "2026-01-01T00:00:00Z",
        ),
    )
    conn.commit()

    text = json.dumps(service.generate_bundle(), sort_keys=True)

    assert raw_openai not in text
    assert raw_github not in text
    assert raw_password not in text
    assert private_path not in text
    assert "<redacted" in text


def test_bundle_does_not_include_raw_synthetic_validation_evidence_secret(tmp_path):
    service, conn, _workspace, _reports_root = diagnostics_service(tmp_path)
    validation = ValidationAgentService(conn, service.reports_root)
    raw_secret = "github_pat_" + "c" * 24
    run = validation.create_run("clean_windows_vm_validation", "Clean Windows VM")
    validation.update_step_result(run["runId"], "clone_repo", "passed", evidence=f"access_token={raw_secret}")

    text = json.dumps(service.generate_bundle(), sort_keys=True)

    assert raw_secret not in text
    assert '"rawValidationEvidenceIncluded": false' in text


def test_bundle_does_not_include_protected_file_contents(tmp_path):
    service, _conn, workspace, _reports_root = diagnostics_service(tmp_path)
    raw_secret = "sk-" + "d" * 24
    write_text(workspace / ".env", f"OPENAI_API_KEY={raw_secret}")

    text = json.dumps(service.generate_bundle(), sort_keys=True)

    assert raw_secret not in text


def test_bundle_includes_validation_readiness_security_and_connector_metadata(tmp_path):
    service, conn, _workspace, reports_root = diagnostics_service(tmp_path)
    validation = ValidationAgentService(conn, reports_root)
    run = validation.create_run("clean_windows_vm_validation", "Clean Windows VM")
    validation.update_step_result(run["runId"], "confirm_vm_environment", "passed")
    write_text(reports_root / "security-safety-Jarvis-20260101T000000Z.md", "# Security/Safety Review Summary\n\n## Verdict\npass\n")

    bundle = service.generate_bundle()
    sections = bundle["sections"]

    assert sections["validationEvidenceSummary"]["validationRunCount"] == 1
    assert sections["readinessSnapshotMetadata"]["agentId"] == "private_alpha_readiness_agent"
    assert sections["securityReviewMetadata"]["latestSecurityReviewVerdict"] == "pass"
    assert sections["connectorBoundarySummary"]["futureConnectorsDisabledPlaceholders"] is True


def test_redacted_diagnostics_agent_does_not_implement_unsafe_actions():
    source = inspect.getsource(redacted_diagnostics_module)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert "requests" not in source
    assert ".unlink(" not in source
    assert "rmtree" not in source
    assert "shutil" not in source
