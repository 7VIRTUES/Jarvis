from __future__ import annotations

from pathlib import Path

from .codex_constants import ALLOWED_SANDBOX_MODE
from .permissions import is_protected_path


def validate_codex_project_paths(project_path: Path, prompt_path: str, output_path: str, sandbox_mode: str) -> tuple[str | None, Path | None, Path | None, Path | None]:
    if sandbox_mode != ALLOWED_SANDBOX_MODE:
        return "sandbox mode must be workspace-write", None, None, None
    try:
        project_root = project_path.resolve()
        prompts_root = project_root / ".jarvis" / "prompts"
        reports_root = project_root / ".jarvis" / "reports"
        if prompts_root.exists() and prompts_root.is_symlink():
            return ".jarvis/prompts root must not be a symlink", None, None, None
        if reports_root.exists() and reports_root.is_symlink():
            return ".jarvis/reports root must not be a symlink", None, None, None
        prompts_root_resolved = prompts_root.resolve(strict=False)
        reports_root_resolved = reports_root.resolve(strict=False)
        if not prompts_root_resolved.is_relative_to(project_root):
            return ".jarvis/prompts root must stay inside registered project", None, None, None
        if not reports_root_resolved.is_relative_to(project_root):
            return ".jarvis/reports root must stay inside registered project", None, None, None
        prompt = (project_root / prompt_path).resolve(strict=False)
        output = (project_root / output_path).resolve(strict=False)
    except (OSError, RuntimeError, ValueError):
        return "codex prompt/output path validation failed", None, None, None

    if not prompt.is_relative_to(prompts_root_resolved) or not prompt.is_relative_to(project_root):
        return "prompt path must stay under .jarvis/prompts and registered project", None, None, None
    if not output.is_relative_to(reports_root_resolved) or not output.is_relative_to(project_root):
        return "output path must stay under .jarvis/reports and registered project", None, None, None
    if is_protected_path(prompt) or is_protected_path(output):
        return "protected prompt or output paths are blocked", None, None, None
    return None, project_root, prompt, output

