from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass
from pathlib import Path


PROTECTED_PATTERNS = [
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "id_rsa",
    "id_ed25519",
    "service-account*.json",
    "firebase-adminsdk*",
    "supabase-service-role*",
    "*password*manager*export*",
    "*cookies*",
    "*session*store*",
    "*token*cache*",
]

BLOCKED_COMMAND_PATTERNS = [
    r"\bgit\s+push\b",
    r"\bgit\s+merge\b",
    r"\bgit\s+reset\s+--hard\b",
    r"\brm\s+-rf\b",
    r"\bdel\s+/s\b",
    r"\bformat\b",
    r"\bdiskpart\b",
    r"\breg\s+delete\b",
    r"\bdisable-windowsdefender\b",
    r"\bset-executionpolicy\s+unrestricted\b",
]

PAYMENT_OR_PUBLIC_ACTIONS = {"send_email", "public_post", "payment_action"}
SECRET_OR_BROWSER_ACTIONS = {"read_secret", "password_manager_access", "browser_session_access"}
ALLOWED_ACTION_TYPES = {
    "command",
    "inspect_project",
    "write_report",
    "codex.plan_execution",
    "codex.prepare_prompt",
    "codex.preview_command",
    "codex.execute_approved_plan",
}
BLOCKED_CODEX_ACTIONS = {"codex.execute", "codex.exec", "codex.run", "run_codex_exec_workspace_write"}


@dataclass(frozen=True)
class PolicyCheckResult:
    allowed: bool
    status: str
    reason: str


def is_protected_path(path: Path | str) -> bool:
    name = Path(path).name.lower()
    full = str(path).replace("\\", "/").lower()
    return any(fnmatch.fnmatch(name, pattern.lower()) or fnmatch.fnmatch(full, pattern.lower()) for pattern in PROTECTED_PATTERNS)


def check_command(command: str) -> PolicyCheckResult:
    normalized = " ".join(command.strip().lower().split())
    if not normalized:
        return PolicyCheckResult(False, "blocked", "empty commands are not executable actions")
    for pattern in BLOCKED_COMMAND_PATTERNS:
        if re.search(pattern, normalized):
            return PolicyCheckResult(False, "blocked", f"blocked command pattern: {pattern}")
    if "://" in normalized and re.search(r"\b(powershell|pwsh|cmd|bash|sh)\b", normalized):
        return PolicyCheckResult(False, "blocked", "unknown downloaded script execution is blocked")
    if re.search(r"\b(remove-item|erase|rmdir)\b", normalized):
        return PolicyCheckResult(False, "blocked", "file deletion automation is blocked in v0.1A")
    return PolicyCheckResult(True, "allowed", "command is allowed by v0.1A policy")


def check_action(action_type: str, target: str | None = None) -> PolicyCheckResult:
    if action_type == "command":
        if not target:
            return PolicyCheckResult(False, "blocked", "command actions require a target command")
        return check_command(target)
    if action_type in PAYMENT_OR_PUBLIC_ACTIONS | SECRET_OR_BROWSER_ACTIONS:
        return PolicyCheckResult(False, "blocked", f"{action_type} is blocked in v0.1A")
    if action_type in {"codex_execute", "browser_automation", "connector_execute"}:
        return PolicyCheckResult(False, "blocked", f"{action_type} is outside v0.1A scope")
    if action_type in BLOCKED_CODEX_ACTIONS:
        return PolicyCheckResult(False, "blocked", f"{action_type} is not implemented in current v0.1 scope")
    if action_type in {"sensitive_write", "external_connector"}:
        return PolicyCheckResult(False, "approval_required", f"{action_type} requires approval before future implementation")
    if action_type not in ALLOWED_ACTION_TYPES:
        return PolicyCheckResult(False, "blocked", f"unknown action type is blocked: {action_type}")
    return PolicyCheckResult(True, "allowed", "action is allowed by v0.1A policy")
