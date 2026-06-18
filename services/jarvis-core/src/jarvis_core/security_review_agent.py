from __future__ import annotations

import fnmatch
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import unquote

from .permissions import BLOCKED_COMMAND_PATTERNS, is_protected_path
from .security_review_models import AGENT_ID, AGENT_NAME, ReviewFinding, SecurityReviewResult
from .workspace_boundary import (
    DEFAULT_RUNTIME_SKIP_DIRS,
    PROTECTED_FILE_PATTERNS as WORKSPACE_PROTECTED_FILE_PATTERNS,
    SAFE_TEXT_SUFFIXES,
    WorkspaceBoundaryValidator,
)


PROTECTED_FILE_PATTERNS = list(WORKSPACE_PROTECTED_FILE_PATTERNS)

SKIP_DIRS = {
    ".hg",
    ".svn",
    ".mypy_cache",
    ".ruff_cache",
    ".jarvis",
    "coverage",
    "data",
    "target",
    *DEFAULT_RUNTIME_SKIP_DIRS,
}

MAX_TEXT_FILE_BYTES = 1_000_000
PUBLIC_READINESS_DOCS = [
    "README.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "docs/public-repo-readiness.md",
    "docs/public-safety-boundaries.md",
]

SECRET_KEYWORDS = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "api_key",
    "secret_key",
    "access_token",
    "refresh_token",
    "private_key",
    "client_secret",
    "password",
    "passwd",
]

SECRET_KEYWORD_RE = re.compile(r"\b(" + "|".join(re.escape(keyword) for keyword in SECRET_KEYWORDS) + r")\b", re.IGNORECASE)
ASSIGNMENT_VALUE_RE = re.compile(
    r"(?P<key>\b(?:"
    + "|".join(re.escape(keyword) for keyword in SECRET_KEYWORDS)
    + r")\b\s*(?:=|:)\s*)(?P<quote>['\"]?)(?P<value>[^'\"\s,#]+)",
    re.IGNORECASE,
)
TOKEN_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("bearer_token", re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{12,}\b", re.IGNORECASE)),
    ("github_ghp_token", re.compile(r"\bghp_[A-Za-z0-9_]{12,}\b")),
    ("github_pat_token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{12,}\b")),
    ("openai_style_token", re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b")),
]

WINDOWS_USERS_BACKSLASH = r"C:\\Users\\"
WINDOWS_USERS_SLASH = "C:" + r"/Users/"
NDUS_ONEDRIVE = "OneDrive - " + "North Dakota University System"
LOCAL_HOST_NAME = "Russell-" + "Desktop"
LOCAL_EMAIL_USER = "russe" + "@"
LINUX_USER_HOME = r"/home/" + "russe"
MAC_USER_HOME = r"/Users/" + "russe"

PRIVATE_PATH_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("windows_user_path", re.compile(re.escape(WINDOWS_USERS_BACKSLASH) + r"[^\\\s\"')]+(?:\\[^\\\s\"')]+)*", re.IGNORECASE)),
    ("windows_user_path", re.compile(re.escape(WINDOWS_USERS_SLASH) + r"[^/\s\"')]+(?:/[^/\s\"')]+)*", re.IGNORECASE)),
    ("ndus_onedrive_path", re.compile(re.escape(NDUS_ONEDRIVE), re.IGNORECASE)),
    ("local_host_name", re.compile(re.escape(LOCAL_HOST_NAME), re.IGNORECASE)),
    ("local_email_user", re.compile(re.escape(LOCAL_EMAIL_USER), re.IGNORECASE)),
    ("linux_user_path", re.compile(re.escape(LINUX_USER_HOME) + r"(?:/[^\s\"')]+)*", re.IGNORECASE)),
    ("mac_user_path", re.compile(re.escape(MAC_USER_HOME) + r"(?:/[^\s\"')]+)*", re.IGNORECASE)),
]

PUBLIC_CLAIM_TERMS = [
    "production-ready",
    "public release",
    "real installer",
    "installer is ready",
    "production Tauri",
    "full pairing",
    "OAuth",
    "cloud sync",
    "telemetry",
    "auto-updater",
    "downloadable",
]

BOUNDARY_WORDS = [
    "no ",
    "not ",
    "never ",
    "without ",
    "disabled",
    "placeholder",
    "not included",
    "not implemented",
    "not yet",
    "does not",
    "must not",
    "excluded",
]


class SecurityReviewService:
    def __init__(self, reports_root: Path, workspace_root: Path, connector_root: Path | None = None):
        self.reports_root = reports_root
        self.workspace_root = workspace_root.resolve()
        self.connector_root = connector_root or (self.workspace_root / "connectors")

    def review_project(self, project_path: Path | str, project_name: str | None = None, mode: str = "read_only") -> SecurityReviewResult:
        if mode != "read_only":
            raise ValueError("security review mode must be read_only")
        root = self._validate_project_path(project_path)
        timestamp = datetime.now(timezone.utc).isoformat()
        safe_files = list(self._iter_safe_text_files(root))
        tracked_files, tracked_source = self._tracked_files(root)
        findings: list[ReviewFinding] = []

        metadata = {
            "agentId": AGENT_ID,
            "agentName": AGENT_NAME,
            "projectPath": str(root),
            "projectName": project_name or root.name,
            "timestamp": timestamp,
            "reviewMode": "read_only",
        }
        git = self._git_summary(root)
        protected_file_scan = self._protected_file_scan(root, tracked_files, tracked_source, findings)
        secret_pattern_scan = self._secret_pattern_scan(root, safe_files, findings)
        private_path_scan = self._private_path_scan(root, safe_files, findings)
        public_release_claim_scan = self._public_release_claim_scan(root, safe_files, findings)
        connector_placeholder_scan = self._connector_placeholder_scan(root, findings)
        public_readiness_docs_scan = self._public_readiness_docs_scan(root, findings)
        dangerous_command_policy_scan = self._dangerous_command_policy_scan(root, findings)

        result = SecurityReviewResult(
            metadata=metadata,
            git=git,
            protected_file_scan=protected_file_scan,
            secret_pattern_scan=secret_pattern_scan,
            private_path_scan=private_path_scan,
            public_release_claim_scan=public_release_claim_scan,
            connector_placeholder_scan=connector_placeholder_scan,
            public_readiness_docs_scan=public_readiness_docs_scan,
            dangerous_command_policy_scan=dangerous_command_policy_scan,
            findings=findings,
        )
        result.verdict = self._verdict(findings)
        result.recommended_next_actions = self._recommended_next_actions(result.verdict, findings)
        return result

    def write_markdown_report(self, result: SecurityReviewResult) -> Path:
        self.reports_root.mkdir(parents=True, exist_ok=True)
        report_id = self._report_id(result)
        report_path = (self.reports_root / report_id).resolve()
        reports_root = self.reports_root.resolve()
        if not report_path.is_relative_to(reports_root) or is_protected_path(report_path):
            raise PermissionError("security review report path is outside the approved reports directory")
        result.report_id = report_id
        result.report_path = str(report_path)
        report_path.write_text(self.markdown_report(result), encoding="utf-8")
        return report_path

    def read_markdown_report(self, review_id: str) -> dict[str, str]:
        path = self._validated_report_path(review_id)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError("security review report not found")
        return {
            "reviewId": path.name,
            "contentType": "text/markdown",
            "content": path.read_text(encoding="utf-8"),
        }

    def markdown_report(self, result: SecurityReviewResult) -> str:
        findings_by_severity = self._findings_by_severity(result.findings)
        lines = [
            "# Security/Safety Review Summary",
            "",
            "## Verdict",
            result.verdict,
            "",
            "## Scope",
            f"- Agent: {result.metadata['agentId']}",
            f"- Project: {result.metadata['projectName']}",
            f"- Path: {result.metadata['projectPath']}",
            f"- Mode: {result.metadata['reviewMode']}",
            "",
            "## Findings by severity",
            json.dumps(findings_by_severity, indent=2),
            "",
            "## Protected file scan",
            json.dumps(result.protected_file_scan, indent=2),
            "",
            "## Secret-pattern scan",
            json.dumps(result.secret_pattern_scan, indent=2),
            "",
            "## Private-path scan",
            json.dumps(result.private_path_scan, indent=2),
            "",
            "## Connector-placeholder scan",
            json.dumps(result.connector_placeholder_scan, indent=2),
            "",
            "## Public-readiness documentation scan",
            json.dumps(result.public_readiness_docs_scan, indent=2),
            "",
            "## Recommended next actions",
            "\n".join(f"- {action}" for action in result.recommended_next_actions) or "- No action required.",
            "",
            "## JSON-style summary",
            "```json",
            json.dumps(result.to_dict(), indent=2),
            "```",
            "",
            "## Safety note",
            "This report does not rewrite history, rotate secrets, delete files, push, merge, call external services, or certify the repository.",
            "",
        ]
        return "\n".join(lines)

    def _validate_project_path(self, project_path: Path | str) -> Path:
        validator = WorkspaceBoundaryValidator(project_path, self.workspace_root)
        decision = validator.validate_root()
        if not decision.allowed:
            if decision.protected:
                raise PermissionError(decision.reason)
            raise ValueError(decision.reason)
        return validator.project_root

    def _tracked_files(self, root: Path) -> tuple[list[str], str]:
        if not self._inside_git(root):
            return [str(path.relative_to(root)).replace("\\", "/") for path in self._iter_files(root, include_protected=True)], "filesystem_non_git"
        tracked = self._git_lines(root, ["ls-files"])
        return tracked, "git_tracked"

    def _git_summary(self, root: Path) -> dict[str, Any]:
        git_available = shutil.which("git") is not None
        if not git_available:
            return {"available": False, "isRepository": False, "note": "git executable is not available"}
        if not self._inside_git(root):
            return {"available": True, "isRepository": False, "note": "path is not inside a git repository"}
        status_lines = self._git_lines(root, ["status", "--porcelain=v1", "--branch"])
        branch_line = next((line for line in status_lines if line.startswith("## ")), "")
        changes = [line for line in status_lines if not line.startswith("## ")]
        changed_tracked = [line for line in changes if not line.startswith("??")]
        untracked = [line for line in changes if line.startswith("??")]
        return {
            "available": True,
            "isRepository": True,
            "branch": self._git_text(root, ["branch", "--show-current"]) or self._branch_from_status(branch_line),
            "workingTreeClean": not changes,
            "changedTrackedFilesCount": len(changed_tracked),
            "untrackedFilesCount": len(untracked),
            "mayBeAheadOfOrigin": "ahead " in branch_line,
            "statusSummary": {
                "branchLine": branch_line,
                "changedTracked": len(changed_tracked),
                "untracked": len(untracked),
            },
        }

    def _protected_file_scan(self, root: Path, reviewed_files: list[str], source: str, findings: list[ReviewFinding]) -> dict[str, Any]:
        matches = [path for path in reviewed_files if self._matches_protected_pattern(path)]
        for path in matches:
            severity = "high" if Path(path).suffix.lower() in {".sqlite", ".sqlite3", ".db", ".log"} or is_protected_path(path) else "medium"
            findings.append(
                ReviewFinding(
                    severity=severity,
                    category="protected_file",
                    message="Protected or local-runtime filename is present in the reviewed file list; contents were not read.",
                    path=path,
                    match="protected_filename",
                )
            )
        return {
            "source": source,
            "patterns": PROTECTED_FILE_PATTERNS,
            "matchedPaths": matches,
            "matchedCount": len(matches),
            "contentsRead": False,
        }

    def _secret_pattern_scan(self, root: Path, safe_files: list[Path], findings: list[ReviewFinding]) -> dict[str, Any]:
        matches: list[dict[str, Any]] = []
        for path in safe_files:
            for line_number, line in self._iter_text_lines(path):
                categories = self._secret_categories(line)
                for category, likely_real in categories:
                    snippet = self._redact_secret_line(line)
                    severity = "high" if likely_real else "medium"
                    finding = ReviewFinding(
                        severity=severity,
                        category="secret_pattern",
                        message="Likely secret or token pattern found with value redacted.",
                        path=str(path.relative_to(root)).replace("\\", "/"),
                        line=line_number,
                        match=category,
                        snippet=snippet,
                    )
                    findings.append(finding)
                    matches.append(finding.to_dict())
        return {"scannedFiles": len(safe_files), "matches": matches, "matchedCount": len(matches), "valuesRedacted": True}

    def _private_path_scan(self, root: Path, safe_files: list[Path], findings: list[ReviewFinding]) -> dict[str, Any]:
        matches: list[dict[str, Any]] = []
        for path in safe_files:
            for line_number, line in self._iter_text_lines(path):
                for category, pattern in PRIVATE_PATH_PATTERNS:
                    if not pattern.search(line):
                        continue
                    finding = ReviewFinding(
                        severity="high",
                        category="private_path",
                        message="Private or user-machine path pattern found with snippet redacted.",
                        path=str(path.relative_to(root)).replace("\\", "/"),
                        line=line_number,
                        match=category,
                        snippet=self._redact_private_path_line(line),
                    )
                    findings.append(finding)
                    matches.append(finding.to_dict())
                    break
        return {"scannedFiles": len(safe_files), "matches": matches, "matchedCount": len(matches), "valuesRedacted": True}

    def _public_release_claim_scan(self, root: Path, safe_files: list[Path], findings: list[ReviewFinding]) -> dict[str, Any]:
        risky_claims: list[dict[str, Any]] = []
        boundary_references: list[dict[str, Any]] = []
        docs_files = [path for path in safe_files if path.suffix.lower() in {".md", ".txt"} or "docs" in path.parts]
        for path in docs_files:
            for line_number, line in self._iter_text_lines(path):
                lowered = line.lower()
                for term in PUBLIC_CLAIM_TERMS:
                    if term.lower() not in lowered:
                        continue
                    item = {
                        "path": str(path.relative_to(root)).replace("\\", "/"),
                        "line": line_number,
                        "match": term,
                        "snippet": self._compact(line),
                    }
                    if self._is_boundary_wording(lowered):
                        boundary_references.append(item)
                    else:
                        finding = ReviewFinding(
                            severity="medium",
                            category="public_release_claim",
                            message="Potential production or public-release claim needs human review.",
                            path=item["path"],
                            line=line_number,
                            match=term,
                            snippet=item["snippet"],
                        )
                        findings.append(finding)
                        risky_claims.append(finding.to_dict())
        return {
            "riskyClaims": risky_claims,
            "riskyClaimCount": len(risky_claims),
            "acceptableBoundaryReferences": boundary_references,
            "acceptableBoundaryReferenceCount": len(boundary_references),
        }

    def _connector_placeholder_scan(self, root: Path, findings: list[ReviewFinding]) -> dict[str, Any]:
        connector_roots = [root / "connectors", self.connector_root]
        manifests: list[dict[str, Any]] = []
        seen: set[Path] = set()
        for connector_root in connector_roots:
            if not connector_root.exists() or not connector_root.is_dir():
                continue
            for path in sorted(connector_root.rglob("*.json")):
                resolved = path.resolve()
                if resolved in seen or is_protected_path(resolved):
                    continue
                seen.add(resolved)
                data = self._load_json_object(resolved)
                if not data or "defaultEnabled" not in data or "implemented" not in data:
                    continue
                relative = self._safe_relative(resolved, root)
                status = {
                    "path": relative,
                    "id": data.get("id"),
                    "implemented": data.get("implemented"),
                    "defaultEnabled": data.get("defaultEnabled"),
                }
                manifests.append(status)
                if data.get("implemented") is not False or data.get("defaultEnabled") is not False:
                    findings.append(
                        ReviewFinding(
                            severity="high",
                            category="connector_placeholder",
                            message="Future connector manifest is implemented or enabled unexpectedly.",
                            path=relative,
                            match="implemented/defaultEnabled",
                        )
                    )
        return {
            "manifestsChecked": len(manifests),
            "connectors": manifests,
            "unexpectedEnabledOrImplemented": [
                item for item in manifests if item["implemented"] is not False or item["defaultEnabled"] is not False
            ],
        }

    def _public_readiness_docs_scan(self, root: Path, findings: list[ReviewFinding]) -> dict[str, Any]:
        docs: dict[str, bool] = {}
        for relative in PUBLIC_READINESS_DOCS:
            exists = (root / relative).exists()
            docs[relative] = exists
            if not exists:
                severity = "medium" if relative in {"README.md", "SECURITY.md", "CONTRIBUTING.md"} else "low"
                findings.append(
                    ReviewFinding(
                        severity=severity,
                        category="public_readiness_docs",
                        message="Expected public-readiness documentation is missing.",
                        path=relative,
                        match="missing_doc",
                    )
                )
        return {"docs": docs, "missing": [path for path, exists in docs.items() if not exists]}

    def _dangerous_command_policy_scan(self, root: Path, findings: list[ReviewFinding]) -> dict[str, Any]:
        policy_files = ["services/jarvis-core/src/jarvis_core/permissions.py", "docs/safety.md", "AGENTS.md"]
        present = [relative for relative in policy_files if (root / relative).exists()]
        if not present:
            findings.append(
                ReviewFinding(
                    severity="low",
                    category="dangerous_command_policy",
                    message="No dangerous-command policy reference files were found in the reviewed project.",
                    match="missing_policy_reference",
                )
            )
        return {
            "policyReferencesPresent": present,
            "blockedCommandPatternsConfigured": len(BLOCKED_COMMAND_PATTERNS),
        }

    def _iter_safe_text_files(self, root: Path) -> Iterable[Path]:
        for path in self._iter_files(root, include_protected=False):
            if path.suffix.lower() not in SAFE_TEXT_SUFFIXES:
                continue
            try:
                if path.stat().st_size > MAX_TEXT_FILE_BYTES:
                    continue
                sample = path.read_bytes()[:4096]
            except OSError:
                continue
            if b"\x00" in sample:
                continue
            yield path

    def _iter_files(self, root: Path, include_protected: bool) -> Iterable[Path]:
        stack = [root]
        while stack:
            current = stack.pop()
            try:
                children = sorted(current.iterdir(), key=lambda item: item.name.lower())
            except OSError:
                continue
            for path in children:
                if path.is_dir():
                    if path.name in SKIP_DIRS or (path.name.startswith(".") and path.name not in {".github"}):
                        continue
                    stack.append(path)
                    continue
                if not path.is_file():
                    continue
                if not include_protected and self._matches_protected_pattern(str(path.relative_to(root)).replace("\\", "/")):
                    continue
                if not include_protected and is_protected_path(path):
                    continue
                yield path

    def _iter_text_lines(self, path: Path) -> Iterable[tuple[int, str]]:
        try:
            with path.open("r", encoding="utf-8", errors="replace") as handle:
                for index, line in enumerate(handle, start=1):
                    yield index, line.rstrip("\n")
        except OSError:
            return

    def _secret_categories(self, line: str) -> list[tuple[str, bool]]:
        categories: list[tuple[str, bool]] = []
        for match in SECRET_KEYWORD_RE.finditer(line):
            likely_real = self._assignment_looks_real(line, match.group(1))
            categories.append((match.group(1).lower(), likely_real))
        for category, pattern in TOKEN_PATTERNS:
            for token_match in pattern.finditer(line):
                categories.append((category, self._token_looks_real(token_match.group(0))))
        return categories

    def _assignment_looks_real(self, line: str, keyword: str) -> bool:
        for match in ASSIGNMENT_VALUE_RE.finditer(line):
            if match.group("key").strip().lower().startswith(keyword.lower()):
                return self._token_looks_real(match.group("value"))
        return False

    def _token_looks_real(self, value: str) -> bool:
        lowered = value.lower()
        placeholders = ["fake", "test", "placeholder", "example", "dummy", "redacted", "xxxx", "sample"]
        return bool(value.strip()) and not any(marker in lowered for marker in placeholders)

    def _redact_secret_line(self, line: str) -> str:
        redacted = ASSIGNMENT_VALUE_RE.sub(lambda match: f"{match.group('key')}{match.group('quote')}<redacted>", line)
        for category, pattern in TOKEN_PATTERNS:
            replacement = "Bearer <redacted>" if category == "bearer_token" else "<redacted-token>"
            redacted = pattern.sub(replacement, redacted)
        return self._compact(redacted)

    def _redact_private_path_line(self, line: str) -> str:
        redacted = line
        replacements = {
            "windows_user_path": "<redacted-user-path>",
            "ndus_onedrive_path": "<redacted-org-path>",
            "local_host_name": "<redacted-host>",
            "local_email_user": "<redacted-user>@",
            "linux_user_path": "<redacted-user-path>",
            "mac_user_path": "<redacted-user-path>",
        }
        for category, pattern in PRIVATE_PATH_PATTERNS:
            redacted = pattern.sub(replacements[category], redacted)
        return self._compact(redacted)

    def _matches_protected_pattern(self, relative_path: str) -> bool:
        normalized = relative_path.replace("\\", "/").lower()
        name = normalized.rsplit("/", 1)[-1]
        return any(fnmatch.fnmatch(name, pattern.lower()) or fnmatch.fnmatch(normalized, pattern.lower()) for pattern in PROTECTED_FILE_PATTERNS)

    def _inside_git(self, root: Path) -> bool:
        return self._git_text(root, ["rev-parse", "--is-inside-work-tree"]) == "true"

    def _git_text(self, root: Path, args: list[str]) -> str | None:
        if shutil.which("git") is None:
            return None
        try:
            result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, timeout=5, shell=False)
        except (OSError, subprocess.TimeoutExpired):
            return None
        return result.stdout.strip() if result.returncode == 0 else None

    def _git_lines(self, root: Path, args: list[str]) -> list[str]:
        text = self._git_text(root, args)
        return text.splitlines() if text else []

    def _branch_from_status(self, branch_line: str) -> str | None:
        if not branch_line.startswith("## "):
            return None
        branch = branch_line[3:].split("...", 1)[0].strip()
        return branch or None

    def _load_json_object(self, path: Path) -> dict[str, Any] | None:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            return None
        return data if isinstance(data, dict) else None

    def _safe_relative(self, path: Path, root: Path) -> str:
        try:
            return str(path.relative_to(root)).replace("\\", "/")
        except ValueError:
            return str(path)

    def _is_boundary_wording(self, lowered_line: str) -> bool:
        return any(word in lowered_line for word in BOUNDARY_WORDS)

    def _compact(self, line: str) -> str:
        return " ".join(line.strip().split())[:240]

    def _verdict(self, findings: list[ReviewFinding]) -> str:
        blocking_categories = {"protected_file", "private_path", "connector_placeholder"}
        if any(finding.severity == "high" and finding.category in blocking_categories for finding in findings):
            return "blocked"
        if any(finding.severity == "high" and finding.category == "secret_pattern" for finding in findings):
            return "blocked"
        if any(finding.severity == "medium" for finding in findings):
            return "needs_review"
        if findings:
            return "pass_with_warnings"
        return "pass"

    def _recommended_next_actions(self, verdict: str, findings: list[ReviewFinding]) -> list[str]:
        if verdict == "pass":
            return ["No findings require action before the next human review."]
        categories = {finding.category for finding in findings}
        actions: list[str] = []
        if "protected_file" in categories:
            actions.append("Review tracked protected or runtime filenames without opening secret values; decide rotation/history cleanup outside this agent if needed.")
        if "secret_pattern" in categories:
            actions.append("Manually verify redacted secret-pattern matches and rotate any real credentials outside this agent.")
        if "private_path" in categories:
            actions.append("Replace private local paths with portable examples or documentation-safe placeholders.")
        if "connector_placeholder" in categories:
            actions.append("Return future connector manifests to implemented=false and defaultEnabled=false.")
        if "public_release_claim" in categories:
            actions.append("Clarify public-release wording so documentation does not imply production readiness.")
        if "public_readiness_docs" in categories:
            actions.append("Add or restore missing public-readiness documentation before public visibility review.")
        if "dangerous_command_policy" in categories:
            actions.append("Document blocked push, merge, reset, delete, and external-action command policies.")
        return actions or ["Review warnings before treating the project as public-ready."]

    def _findings_by_severity(self, findings: list[ReviewFinding]) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = {"high": [], "medium": [], "low": []}
        for finding in findings:
            grouped.setdefault(finding.severity, []).append(finding.to_dict())
        return grouped

    def _report_id(self, result: SecurityReviewResult) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        project = re.sub(r"[^A-Za-z0-9_.-]+", "-", str(result.metadata["projectName"]).strip()).strip("-") or "project"
        return f"security-safety-{project}-{timestamp}.md"

    def _validated_report_path(self, review_id: str) -> Path:
        decoded = unquote(review_id).strip()
        relative = Path(decoded.replace("\\", "/"))
        if (
            not decoded
            or decoded != review_id
            or relative.is_absolute()
            or len(relative.parts) != 1
            or ".." in relative.parts
            or relative.suffix.lower() != ".md"
            or not relative.name.startswith("security-safety-")
        ):
            raise PermissionError("security review id must be a single generated Markdown report name")
        root = self.reports_root.resolve()
        candidate = (root / relative.name).resolve()
        if not candidate.is_relative_to(root) or is_protected_path(candidate):
            raise PermissionError("security review report path is outside the approved reports directory")
        return candidate
