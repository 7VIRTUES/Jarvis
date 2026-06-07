from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DESKTOP_ROOT = REPO_ROOT / "apps" / "desktop"


def test_desktop_placeholder_docs_exist_without_tauri_project_files():
    readme = DESKTOP_ROOT / "README.md"
    placeholder = DESKTOP_ROOT / "TAURI_PLACEHOLDER.md"

    assert readme.exists()
    assert placeholder.exists()
    assert not (DESKTOP_ROOT / "package.json").exists()
    assert not (DESKTOP_ROOT / "src-tauri" / "tauri.conf.json").exists()
    assert not (DESKTOP_ROOT / "src-tauri" / "Cargo.toml").exists()


def test_desktop_placeholder_docs_do_not_claim_working_launch_or_install():
    text = "\n".join(
        [
            (DESKTOP_ROOT / "README.md").read_text(encoding="utf-8"),
            (DESKTOP_ROOT / "TAURI_PLACEHOLDER.md").read_text(encoding="utf-8"),
        ]
    ).lower()

    assert "placeholder" in text
    assert "not implemented as a production desktop app" in text
    assert "no tauri dependencies" in text
    assert "no launch, install, update, or service-control commands" in text
