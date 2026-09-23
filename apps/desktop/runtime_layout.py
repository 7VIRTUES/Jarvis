"""Fixed desktop paths shared by preparation, launcher, and Jarvis Core.

No path is accepted from the environment or the UI. Installed resources carry a
bundle-only marker; Windows supplies the per-user LocalAppData known folder.
"""

import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import uuid


RESOURCE_MARKER = "jarvis-desktop-resources-v1"
APP_DIRECTORY = "local.jarvis.desktop"


def local_app_data() -> Path:
    if os.name != "nt":
        raise RuntimeError("Installed Jarvis desktop requires Windows.")
    # FOLDERID_LocalAppData, queried from Windows rather than LOCALAPPDATA/HOME.
    folder_id = (ctypes.c_ubyte * 16).from_buffer_copy(
        uuid.UUID("f1b32785-6fba-4fcf-9d55-7b8e7f157091").bytes_le
    )
    shell = ctypes.WinDLL("shell32", use_last_error=True)
    ole = ctypes.WinDLL("ole32", use_last_error=True)
    shell.SHGetKnownFolderPath.argtypes = [
        ctypes.c_void_p, wintypes.DWORD, wintypes.HANDLE,
        ctypes.POINTER(ctypes.c_void_p),
    ]
    shell.SHGetKnownFolderPath.restype = ctypes.c_long
    ole.CoTaskMemFree.argtypes = [ctypes.c_void_p]
    ole.CoTaskMemFree.restype = None
    result = ctypes.c_void_p()
    try:
        if shell.SHGetKnownFolderPath(ctypes.byref(folder_id), 0, None, ctypes.byref(result)) != 0:
            raise RuntimeError("Windows could not resolve the Jarvis application-data folder.")
        path = Path(ctypes.wstring_at(result))
        if not path.is_absolute():
            raise RuntimeError("Windows returned an invalid application-data folder.")
        return path.resolve()
    finally:
        if result.value:
            ole.CoTaskMemFree(result)


class RuntimeLayout:
    def __init__(self, resources: Path):
        self.resources = resources.resolve()
        marker = self.resources / "desktop-resources.version"
        self.installed = marker.is_file()
        if self.installed and marker.read_text(encoding="utf-8").strip() != RESOURCE_MARKER:
            raise RuntimeError("The packaged Jarvis resource layout is unsupported.")
        mode = "installed" if self.installed else "repository"
        if os.environ.get("JARVIS_DESKTOP_LAYOUT", mode) != mode:
            raise RuntimeError("Desktop resource layout does not match the launcher.")
        self.runtime = self.resources
        self.data = self.resources / "data" / "jarvis"
        if self.installed:
            user_root = local_app_data() / APP_DIRECTORY
            self.runtime = user_root / "runtime"
            self.data = user_root / "data" / "jarvis"
            # Refuse junction/symlink redirection beneath the known user folder.
            for path in (
                self.runtime / ".venv" / "Scripts" / "python.exe",
                self.data / "jarvis.sqlite",
                self.data / "logs",
                self.data / "reports",
                self.runtime / "ollama" / "models",
            ):
                if path.resolve() != path:
                    raise RuntimeError("Jarvis runtime/data paths must not be redirected.")
            for path in (self.runtime, self.data):
                if path.is_relative_to(self.resources) or self.resources.is_relative_to(path):
                    raise RuntimeError("Writable Jarvis state must be outside packaged resources.")
        self.venv = self.runtime / ".venv"
        self.python = self.venv / "Scripts" / "python.exe"

    def environment(self) -> dict[str, str]:
        env = dict(os.environ)
        env["JARVIS_DESKTOP_LAYOUT"] = "installed" if self.installed else "repository"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return env

    def ollama_environment(self) -> dict[str, str]:
        env = self.environment()
        env["OLLAMA_HOST"] = "127.0.0.1:11434"
        if self.installed:
            env["OLLAMA_MODELS"] = str(self.runtime / "ollama" / "models")
        return env

    def prepare_directories(self) -> None:
        # Never seed, replace, migrate, or clear existing user data on upgrade.
        self.runtime.mkdir(parents=True, exist_ok=True)


def resolve_layout(resources: Path) -> RuntimeLayout:
    return RuntimeLayout(resources)
