import inspect
import json

import pytest

from jarvis_core.docs_center import DocsCenterService
import jarvis_core.docs_center as docs_module


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def docs_service(tmp_path):
    return DocsCenterService(tmp_path / "workspace")


def by_id(index):
    return {doc["docId"]: doc for doc in index["docs"]}


def test_indexes_readme_and_direct_docs_markdown(tmp_path):
    service = docs_service(tmp_path)
    write_text(service.workspace_root / "README.md", "# Jarvis\n\nLocal assistant docs.")
    write_text(service.docs_root / "validation-agent.md", "# Validation Agent\n\nManual validation docs.")

    index = service.index_docs()
    docs = by_id(index)

    assert index["totalDocs"] == 2
    assert docs["README.md"]["category"] == "README"
    assert docs["validation-agent.md"]["category"] == "validation"


def test_does_not_index_subdirectories(tmp_path):
    service = docs_service(tmp_path)
    write_text(service.workspace_root / "README.md", "# Jarvis\n")
    write_text(service.docs_root / "nested" / "hidden.md", "# Hidden\n")

    docs = by_id(service.index_docs())

    assert "README.md" in docs
    assert "hidden.md" not in docs


def test_categorizes_docs(tmp_path):
    service = docs_service(tmp_path)
    for name in [
        "safety.md",
        "chatgpt-codex-workflow.md",
        "redacted-diagnostics-agent.md",
        "evidence-report-center.md",
        "agent-manifest-health-center.md",
        "project-profiles.md",
        "private-alpha-packaging.md",
        "architecture.md",
        "notes.md",
    ]:
        write_text(service.docs_root / name, f"# {name}\n\nSummary.")

    docs = by_id(service.index_docs())

    assert docs["safety.md"]["category"] == "safety"
    assert docs["chatgpt-codex-workflow.md"]["category"] == "workflow"
    assert docs["redacted-diagnostics-agent.md"]["category"] == "diagnostics"
    assert docs["evidence-report-center.md"]["category"] == "evidence"
    assert docs["agent-manifest-health-center.md"]["category"] == "manifest"
    assert docs["project-profiles.md"]["category"] == "project profile"
    assert docs["private-alpha-packaging.md"]["category"] == "packaging/readiness"
    assert docs["architecture.md"]["category"] == "architecture"
    assert docs["notes.md"]["category"] == "other"


def test_extracts_title_and_summary(tmp_path):
    service = docs_service(tmp_path)
    write_text(service.docs_root / "runbook.md", "# Runbook Title\n\nFirst safe summary line.\n\nSecond line.")

    metadata = service.get_doc_metadata("runbook.md")

    assert metadata["title"] == "Runbook Title"
    assert "First safe summary line" in metadata["summary"]


def test_redacts_synthetic_secrets_and_private_paths(tmp_path):
    service = docs_service(tmp_path)
    raw_secret = "sk-" + "a" * 24
    raw_pat = "github_pat_" + "b" * 24
    win_path = "C:" + "/Users/example/private/.env"
    linux_path = "/" + "home" + "/example/private/.env"
    mac_path = "/" + "Users" + "/example/private/.env"
    content = f"# Secret Doc\n\nOPENAI_API_KEY={raw_secret} access_token={raw_pat} {win_path} {linux_path} {mac_path} user@example.test OneDrive - Example Org"
    write_text(service.docs_root / "secret.md", content)

    metadata_text = json.dumps(service.get_doc_metadata("secret.md"), sort_keys=True)
    detail_text = json.dumps(service.get_doc_detail("secret.md"), sort_keys=True)

    for raw in [raw_secret, raw_pat, win_path, linux_path, mac_path, "user@example.test", "Example Org"]:
        assert raw not in metadata_text
        assert raw not in detail_text
    assert "<redacted" in detail_text


def test_blocks_traversal_doc_id(tmp_path):
    service = docs_service(tmp_path)

    with pytest.raises(PermissionError):
        service.get_doc_detail("..%2FREADME.md")


def test_blocks_symlink_escape(tmp_path):
    service = docs_service(tmp_path)
    service.docs_root.mkdir(parents=True)
    outside = tmp_path / "outside.md"
    write_text(outside, "# Outside\n")
    link = service.docs_root / "escape.md"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable")

    assert "escape.md" not in by_id(service.index_docs())
    with pytest.raises(PermissionError):
        service.get_doc_detail("escape.md")


def test_skips_non_md_temp_hidden_and_backup_files(tmp_path):
    service = docs_service(tmp_path)
    write_text(service.docs_root / ".hidden.md", "# Hidden")
    write_text(service.docs_root / "draft.md.tmp", "# Temp")
    write_text(service.docs_root / "backup.md.bak", "# Backup")
    write_text(service.docs_root / "notes.txt", "notes")

    assert service.index_docs()["docs"] == []


def test_no_doc_mutation_external_calls_or_upload_behavior_implemented():
    source = inspect.getsource(docs_module)

    assert "subprocess" not in source
    assert "requests" not in source
    assert ".write_text(" not in source
    assert ".unlink(" not in source
    assert "rmtree" not in source
    assert "remove(" not in source
