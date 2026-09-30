from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DESKTOP_ROOT = REPO_ROOT / "apps" / "desktop"


def test_desktop_tauri_project_structure_exists():
    readme = DESKTOP_ROOT / "README.md"
    tauri_conf = DESKTOP_ROOT / "src-tauri" / "tauri.conf.json"
    cargo_toml = DESKTOP_ROOT / "src-tauri" / "Cargo.toml"

    assert readme.exists()
    assert tauri_conf.exists()
    assert cargo_toml.exists()
    assert not (DESKTOP_ROOT / "package.json").exists()


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
