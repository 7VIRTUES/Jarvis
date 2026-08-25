from __future__ import annotations

import os
from pathlib import Path
import subprocess

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_shortcut_files_exist():
    assert (REPO_ROOT / "install-jarvis-shortcut.cmd").is_file()
    assert (REPO_ROOT / "remove-jarvis-shortcut.cmd").is_file()
    assert (REPO_ROOT / "scripts" / "install_jarvis_shortcut.ps1").is_file()
    assert (REPO_ROOT / "scripts" / "remove_jarvis_shortcut.ps1").is_file()


def test_cmd_wrappers_use_safe_powershell_invocation():
    install_cmd = (REPO_ROOT / "install-jarvis-shortcut.cmd").read_text(encoding="utf-8")
    remove_cmd = (REPO_ROOT / "remove-jarvis-shortcut.cmd").read_text(encoding="utf-8")

    assert "-NoProfile" in install_cmd
    assert "-ExecutionPolicy Bypass" in install_cmd
    assert "install_jarvis_shortcut.ps1" in install_cmd

    assert "-NoProfile" in remove_cmd
    assert "-ExecutionPolicy Bypass" in remove_cmd
    assert "remove_jarvis_shortcut.ps1" in remove_cmd


def test_shortcut_scripts_have_no_dangerous_mutations():
    installer_text = (REPO_ROOT / "scripts" / "install_jarvis_shortcut.ps1").read_text(encoding="utf-8").lower()
    remover_text = (REPO_ROOT / "scripts" / "remove_jarvis_shortcut.ps1").read_text(encoding="utf-8").lower()

    for forbidden in (
        "hklm",
        "hkcu:",
        "registry::",
        "set-itemproperty",
        "new-service",
        "sc.exe",
        "schtasks",
        "register-scheduledtask",
        "runas",
        "administrator",
        "startup",
    ):
        assert forbidden not in installer_text
        assert forbidden not in remover_text


@pytest.mark.skipif(os.name != "nt", reason="Windows shortcut tests require Windows PowerShell and WScript.Shell")
def test_shortcut_install_idempotent_and_remove_flow(tmp_path: Path):
    desktop_dir = tmp_path / "Desktop"
    start_dir = tmp_path / "StartMenu"
    desktop_dir.mkdir(parents=True, exist_ok=True)
    start_dir.mkdir(parents=True, exist_ok=True)

    unrelated_file = desktop_dir / "Unrelated.txt"
    unrelated_file.write_text("Do not touch this file.\n", encoding="utf-8")

    install_cmd = [
        str(REPO_ROOT / "install-jarvis-shortcut.cmd"),
        "-DesktopPath",
        str(desktop_dir),
        "-StartMenuProgramsPath",
        str(start_dir),
    ]

    # 1. Install
    result = subprocess.run(install_cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert "Jarvis shortcuts installed successfully." in result.stdout

    desktop_lnk = desktop_dir / "Jarvis.lnk"
    start_lnk = start_dir / "Jarvis" / "Jarvis.lnk"

    assert desktop_lnk.is_file()
    assert start_lnk.is_file()
    assert unrelated_file.is_file()

    # Verify shortcut COM properties using PowerShell WScript.Shell
    inspect_script = f"""
    $shell = New-Object -ComObject WScript.Shell
    $d = $shell.CreateShortcut('{desktop_lnk}')
    Write-Output "TargetPath:$($d.TargetPath)"
    Write-Output "WorkingDir:$($d.WorkingDirectory)"
    Write-Output "Description:$($d.Description)"
    Write-Output "WindowStyle:$($d.WindowStyle)"
    """
    inspect_result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", inspect_script],
        capture_output=True,
        text=True,
        check=False,
    )
    assert inspect_result.returncode == 0
    stdout = inspect_result.stdout
    assert f"TargetPath:{REPO_ROOT / 'jarvis.cmd'}" in stdout
    assert f"WorkingDir:{REPO_ROOT}" in stdout
    assert "Description:Jarvis PC Local" in stdout
    assert "WindowStyle:7" in stdout

    # 2. Re-install (idempotency check: must not create duplicate files)
    reinstall_result = subprocess.run(install_cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    assert reinstall_result.returncode == 0
    assert "Jarvis shortcuts installed successfully." in reinstall_result.stdout
    assert desktop_lnk.is_file()
    assert not (desktop_dir / "Jarvis (1).lnk").exists()

    # 3. Remove
    remove_cmd = [
        str(REPO_ROOT / "remove-jarvis-shortcut.cmd"),
        "-DesktopPath",
        str(desktop_dir),
        "-StartMenuProgramsPath",
        str(start_dir),
    ]
    remove_result = subprocess.run(remove_cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    assert remove_result.returncode == 0
    assert "Jarvis shortcuts removed successfully." in remove_result.stdout

    assert not desktop_lnk.exists()
    assert not start_lnk.exists()
    assert not (start_dir / "Jarvis").exists()
    assert unrelated_file.is_file()  # Preserved!

    # 4. Safe removal no-op
    remove_noop = subprocess.run(remove_cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    assert remove_noop.returncode == 0
    assert "No Jarvis shortcuts were found to remove." in remove_noop.stdout
