from __future__ import annotations

from pathlib import Path


ALLOWED_SANDBOX_MODE = "workspace-write"
PROMPT_RELATIVE = Path(".jarvis") / "prompts" / "current-task.md"
OUTPUT_RELATIVE = Path(".jarvis") / "reports" / "latest-codex-output.md"
COMMAND_TEMPLATE = [
    "codex",
    "exec",
    "--cd",
    "{PROJECT_PATH}",
    "--sandbox",
    "workspace-write",
    "--ask-for-approval",
    "never",
    "--output-last-message",
    "{OUTPUT_PATH}",
    "Read {PROMPT_PATH} and complete the task exactly.",
]

