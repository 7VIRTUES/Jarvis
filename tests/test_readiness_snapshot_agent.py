import inspect

from jarvis_core.db import init_db
import jarvis_core.readiness_snapshot_agent as readiness_module
from jarvis_core.readiness_snapshot_agent import PrivateAlphaReadinessSnapshotService
from jarvis_core.validation_agent import ValidationAgentService


PLACEHOLDER_CONNECTOR_JSON = """{
  "id": "github",
  "provider": "GitHub",
  "implemented": false,
  "defaultEnabled": false,
  "readinessLevel": "placeholder_only",
  "costMode": "official_free_quota",
  "authType": "oauth_future",
  "privacyClass": "external_account",
  "dataAccess": "none_in_current_v0.1",
  "approvalRequired": true,
  "tokenStorage": "not_implemented",
  "dataRetention": "none",
  "notes": "Placeholder only."
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
    write_text(
        workspace / "connectors" / "placeholders" / "github.json",
        PLACEHOLDER_CONNECTOR_JSON,
    )
    write_text(
        workspace / "connectors" / "agents" / "security-safety-agent.json",
        '{"id":"security_safety_agent","implemented":true}',
    )
    write_text(
        workspace / "services" / "jarvis-core" / "src" / "jarvis_core" / "project_profiles.py",
        "project profile capability",
    )
    write_text(
        workspace / "services" / "jarvis-core" / "src" / "jarvis_core" / "workspace_boundary.py",
        "workspace boundary validator",
    )
    write_text(
        workspace / "services" / "jarvis-core" / "src" / "jarvis_core" / "dashboard.py",
        "api_reports /api/reports settings-status project-profiles security-safety-review validation-agent-status Generate local report private-alpha-readiness-snapshot",
    )
    return workspace


def readiness_service(tmp_path):
    conn = init_db(tmp_path / "jarvis.sqlite")
    workspace = create_workspace(tmp_path)
    reports_root = tmp_path / "data" / "jarvis" / "reports"
    return PrivateAlphaReadinessSnapshotService(conn, reports_root, workspace, workspace / "connectors")


def test_snapshot_service_generates_overall_snapshot(tmp_path):
    service = readiness_service(tmp_path)

    snapshot = service.generate_snapshot()

    assert snapshot["agentId"] == "private_alpha_readiness_agent"
    assert snapshot["mode"] == "local_readiness_snapshot"
    assert snapshot["overallVerdict"] in {"ready_for_manual_vm_validation", "needs_evidence", "needs_review", "blocked"}
    assert "sections" in snapshot
    assert "production_ready" not in str(snapshot)


def test_snapshot_includes_v01_milestone_closed_status(tmp_path):
    service = readiness_service(tmp_path)

    milestone = service.generate_snapshot()["sections"]["current_milestone_status"]["items"]

    assert milestone["v0.1A"] == "closed"
    assert milestone["v0.1B"] == "closed"
    assert milestone["v0.1C"] == "closed"
    assert milestone["v0.2BroadlyStarted"] is False


def test_missing_vm_validation_evidence_needs_evidence_not_production_ready(tmp_path):
    service = readiness_service(tmp_path)

    snapshot = service.generate_snapshot()
    validation = snapshot["sections"]["validation_evidence"]["items"]

    assert validation["cleanWindowsVmValidationEvidenceStatus"] == "missing"
    assert snapshot["overallVerdict"] in {"needs_evidence", "ready_for_manual_vm_validation"}
    assert snapshot["overallVerdict"] != "production_ready"


def test_snapshot_includes_explicit_non_release_boundary(tmp_path):
    service = readiness_service(tmp_path)

    boundary = service.generate_snapshot()["sections"]["explicit_non_release_boundary"]["items"]

    assert boundary["installerArtifact"] is False
    assert boundary["productionTauri"] is False
    assert boundary["publicReleaseBuild"] is False
    assert boundary["githubReleaseAutomation"] is False
    assert boundary["certifiesProductionReadiness"] is False
    assert boundary["certifiesSecurity"] is False


def test_snapshot_detects_public_readiness_docs_presence(tmp_path):
    service = readiness_service(tmp_path)

    public_docs = service.generate_snapshot()["sections"]["public_repository_readiness"]["items"]

    assert public_docs["docsStatus"] == "present"
    assert not public_docs["missingDocs"]
    assert public_docs["docs"]["README.md"] is True
    assert public_docs["docs"]["docs/public-safety-boundaries.md"] is True


def test_snapshot_detects_connector_placeholder_boundary(tmp_path):
    service = readiness_service(tmp_path)

    connector = service.generate_snapshot()["sections"]["connector_and_cost_boundary"]["items"]

    assert connector["futureConnectorsPlaceholderOnly"] is True
    assert connector["paidAiApisImplemented"] is False
    assert connector["browserAutomationImplemented"] is False
    assert connector["externalAccountConnectorsImplemented"] is False


def test_snapshot_report_generation_works(tmp_path):
    service = readiness_service(tmp_path)

    report = service.write_markdown_report()
    report_path = tmp_path / "data" / "jarvis" / "reports" / report["reportId"]

    assert report["reportId"].startswith("private-alpha-readiness-snapshot-")
    assert report_path.exists()
    text = report_path.read_text(encoding="utf-8")
    assert "# Private-Alpha Readiness Snapshot" in text
    assert "## Connector and Cost Boundary" in text
    assert "This is not production certification" in text


def test_generated_report_does_not_include_raw_synthetic_token_values(tmp_path):
    service = readiness_service(tmp_path)
    validation = ValidationAgentService(service.conn, service.reports_root)
    run = validation.create_run("clean_windows_vm_validation", "Clean Windows VM")
    raw_token = "sk-" + "f" * 24
    validation.update_step_result(
        run["runId"],
        "confirm_prerequisites",
        "passed",
        notes=f"OPENAI_API_KEY={raw_token}",
        evidence=f"Bearer ghp_{'g' * 24}",
    )

    report = service.write_markdown_report()
    text = (tmp_path / "data" / "jarvis" / "reports" / report["reportId"]).read_text(encoding="utf-8")

    assert raw_token not in text
    assert "ghp_" + "g" * 24 not in text
    assert "rawValidationNotesIncluded" in text
    assert "rawValidationEvidenceIncluded" in text


def test_protected_filename_detection_metadata_does_not_read_contents(tmp_path):
    service = readiness_service(tmp_path)
    raw_token = "sk-" + "h" * 24
    write_text(service.workspace_root / ".env", f"OPENAI_API_KEY={raw_token}")

    snapshot = service.generate_snapshot()
    boundary = snapshot["sections"]["project_profile_workspace_boundary_status"]["items"]

    assert boundary["trackedProtectedFilenameCheck"]["contentsRead"] is False
    assert raw_token not in str(snapshot)


def test_readiness_snapshot_agent_does_not_implement_command_execution_or_file_deletion():
    source = inspect.getsource(readiness_module)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert ".unlink(" not in source
    assert "rmtree" not in source


def test_readiness_snapshot_agent_does_not_call_external_services():
    source = inspect.getsource(readiness_module)

    assert "requests" not in source
    assert "httpx" not in source
    assert "urllib.request" not in source
    assert "openai" not in source.lower()
    assert "anthropic" not in source.lower()
