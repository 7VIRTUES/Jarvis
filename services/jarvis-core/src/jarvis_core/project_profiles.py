from __future__ import annotations

import json
import shutil
import subprocess
import tomllib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .workspace_boundary import DEFAULT_RUNTIME_SKIP_DIRS, PROTECTED_FILE_PATTERNS, WorkspaceBoundaryValidator


CHECK_ORDER = ["typecheck", "lint", "test", "build"]
PUBLIC_READINESS_DOCS = ["docs/public-repo-readiness.md", "docs/public-safety-boundaries.md"]
SECURITY_DOCS = ["README.md", "SECURITY.md", "CONTRIBUTING.md"]


@dataclass
class ProjectProfile:
    project_name: str
    project_root: str
    root_validated: bool
    generated_at: str
    project_type: str
    detected_languages: list[str] = field(default_factory=list)
    detected_frameworks: list[str] = field(default_factory=list)
    package_manager: str = "none"
    package_scripts: dict[str, str] = field(default_factory=dict)
    preferred_check_order: list[str] = field(default_factory=list)
    has_git_repo: bool = False
    git_branch: str | None = None
    git_clean: bool | None = None
    runtime_skip_dirs: list[str] = field(default_factory=lambda: list(DEFAULT_RUNTIME_SKIP_DIRS))
    protected_patterns: list[str] = field(default_factory=lambda: list(PROTECTED_FILE_PATTERNS))
    public_readiness_docs_present: dict[str, bool] = field(default_factory=dict)
    security_docs_present: dict[str, bool] = field(default_factory=dict)
    future_connectors_placeholder_only: bool | None = None
    recommended_mode: str = "observe"
    risk_budget_hint: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    boundary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "projectName": self.project_name,
            "profileId": self.project_name,
            "projectRoot": self.project_root,
            "rootValidated": self.root_validated,
            "generatedAt": self.generated_at,
            "projectType": self.project_type,
            "detectedLanguages": self.detected_languages,
            "detectedFrameworks": self.detected_frameworks,
            "packageManager": self.package_manager,
            "packageScripts": self.package_scripts,
            "preferredCheckOrder": self.preferred_check_order,
            "hasGitRepo": self.has_git_repo,
            "gitBranch": self.git_branch,
            "gitClean": self.git_clean,
            "runtimeSkipDirs": self.runtime_skip_dirs,
            "protectedPatterns": self.protected_patterns,
            "publicReadinessDocsPresent": self.public_readiness_docs_present,
            "securityDocsPresent": self.security_docs_present,
            "futureConnectorsPlaceholderOnly": self.future_connectors_placeholder_only,
            "recommendedMode": self.recommended_mode,
            "riskBudgetHint": self.risk_budget_hint,
            "warnings": self.warnings,
            "blockedReasons": self.blocked_reasons,
            "boundary": self.boundary,
        }


class ProjectProfileService:
    def __init__(self, workspace_root: Path, connector_root: Path | None = None):
        self.workspace_root = workspace_root.resolve()
        self.connector_root = connector_root or (self.workspace_root / "connectors")

    def generate_profile(self, project_root: Path | str, project_name: str | None = None) -> ProjectProfile:
        validator = WorkspaceBoundaryValidator(project_root, self.workspace_root)
        root_decision = validator.validate_root()
        root = validator.project_root
        if not root_decision.allowed:
            return ProjectProfile(
                project_name=project_name or root.name,
                project_root=str(root),
                root_validated=False,
                generated_at=self._now(),
                project_type="unknown",
                blocked_reasons=[root_decision.reason],
                boundary={"root": root_decision.__dict__},
            )

        package_scripts = self._package_scripts(root, validator)
        detected_languages = self._detected_languages(root, validator)
        detected_frameworks = self._detected_frameworks(root, validator, package_scripts)
        project_type = self._project_type(detected_languages)
        public_docs = self._docs_presence(root, validator, PUBLIC_READINESS_DOCS)
        security_docs = self._docs_presence(root, validator, SECURITY_DOCS)
        git = self._git_summary(root)
        warnings = self._warnings(public_docs, security_docs)
        connector_status = self._future_connectors_placeholder_only(root, validator)

        if connector_status is False:
            warnings.append("One or more connector manifests are implemented or enabled unexpectedly.")

        return ProjectProfile(
            project_name=project_name or root.name,
            project_root=str(root),
            root_validated=True,
            generated_at=self._now(),
            project_type=project_type,
            detected_languages=detected_languages,
            detected_frameworks=detected_frameworks,
            package_manager=self._package_manager(root),
            package_scripts=package_scripts,
            preferred_check_order=self._preferred_check_order(project_type, package_scripts, root),
            has_git_repo=git["isRepository"],
            git_branch=git["branch"],
            git_clean=git["clean"],
            public_readiness_docs_present=public_docs,
            security_docs_present=security_docs,
            future_connectors_placeholder_only=connector_status,
            recommended_mode=self._recommended_mode(warnings),
            risk_budget_hint=self._risk_budget_hint(project_type, warnings),
            warnings=warnings,
            blocked_reasons=[],
            boundary={
                "root": root_decision.__dict__,
                "runtimeSkipDirs": list(DEFAULT_RUNTIME_SKIP_DIRS),
                "protectedPatterns": list(PROTECTED_FILE_PATTERNS),
            },
        )

    def _package_scripts(self, root: Path, validator: WorkspaceBoundaryValidator) -> dict[str, str]:
        package_json = root / "package.json"
        decision = validator.safe_to_read_metadata(package_json)
        if not decision.allowed or not package_json.exists():
            return {}
        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return {}
        scripts = data.get("scripts") if isinstance(data, dict) else None
        return {str(key): str(value) for key, value in scripts.items()} if isinstance(scripts, dict) else {}

    def _detected_languages(self, root: Path, validator: WorkspaceBoundaryValidator) -> list[str]:
        languages: set[str] = set()
        if self._metadata_exists(root, validator, "pyproject.toml") or self._metadata_exists(root, validator, "requirements.txt") or (root / "tests").is_dir():
            languages.add("python")
        if self._metadata_exists(root, validator, "package.json"):
            languages.add("javascript")
        if any((root / relative).exists() for relative in ["tsconfig.json", "src", "apps"]):
            if (root / "package.json").exists() or (root / "tsconfig.json").exists():
                languages.add("typescript")
        return sorted(languages)

    def _detected_frameworks(self, root: Path, validator: WorkspaceBoundaryValidator, package_scripts: dict[str, str]) -> list[str]:
        frameworks: set[str] = set()
        package_data = self._package_json(root, validator)
        dependencies = {}
        for key in ["dependencies", "devDependencies"]:
            value = package_data.get(key)
            if isinstance(value, dict):
                dependencies.update(value)
        if "vite" in dependencies or any("vite" in script for script in package_scripts.values()):
            frameworks.add("vite")
        if "next" in dependencies:
            frameworks.add("nextjs")
        if "react" in dependencies:
            frameworks.add("react")
        pyproject = self._pyproject(root, validator)
        pyproject_text = str(pyproject).lower()
        requirements = self._metadata_text(root, validator, "requirements.txt").lower()
        if "fastapi" in pyproject_text or "fastapi" in requirements:
            frameworks.add("fastapi")
        if "pytest" in pyproject_text or "pytest" in requirements or (root / "tests").is_dir():
            frameworks.add("pytest")
        return sorted(frameworks)

    def _project_type(self, languages: list[str]) -> str:
        language_set = set(languages)
        if "python" in language_set and language_set & {"javascript", "typescript"}:
            return "mixed"
        if "python" in language_set:
            return "python"
        if language_set & {"javascript", "typescript"}:
            return "node"
        return "unknown"

    def _package_manager(self, root: Path) -> str:
        if (root / "pnpm-lock.yaml").exists():
            return "pnpm"
        if (root / "yarn.lock").exists():
            return "yarn"
        if (root / "package-lock.json").exists() or (root / "package.json").exists():
            return "npm"
        return "none"

    def _preferred_check_order(self, project_type: str, scripts: dict[str, str], root: Path) -> list[str]:
        commands = [f"npm run {name}" for name in CHECK_ORDER if name in scripts]
        if commands:
            return commands
        if project_type in {"python", "mixed"} and (root / "tests").is_dir():
            return ["python -m pytest"]
        return []

    def _docs_presence(self, root: Path, validator: WorkspaceBoundaryValidator, relatives: list[str]) -> dict[str, bool]:
        presence: dict[str, bool] = {}
        for relative in relatives:
            path = root / relative
            decision = validator.safe_to_read_metadata(path)
            presence[relative] = path.exists() and decision.status != "blocked"
        return presence

    def _future_connectors_placeholder_only(self, root: Path, validator: WorkspaceBoundaryValidator) -> bool | None:
        connector_root = root / "connectors" / "placeholders"
        if not connector_root.exists():
            return None
        checked = False
        for path in sorted(connector_root.glob("*.json")):
            decision = validator.check_path(path)
            if not decision.allowed:
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                return False
            if not isinstance(data, dict) or "implemented" not in data or "defaultEnabled" not in data:
                continue
            checked = True
            if data.get("implemented") is not False or data.get("defaultEnabled") is not False:
                return False
        return True if checked else None

    def _warnings(self, public_docs: dict[str, bool], security_docs: dict[str, bool]) -> list[str]:
        warnings: list[str] = []
        missing_security = [path for path, present in security_docs.items() if not present]
        missing_public = [path for path, present in public_docs.items() if not present]
        if missing_security:
            warnings.append("Missing security/project documentation: " + ", ".join(missing_security))
        if missing_public:
            warnings.append("Missing public-readiness documentation: " + ", ".join(missing_public))
        return warnings

    def _recommended_mode(self, warnings: list[str]) -> str:
        return "assist" if not warnings else "observe"

    def _risk_budget_hint(self, project_type: str, warnings: list[str]) -> dict[str, int]:
        base = {"changedFiles": 5, "commands": 3, "networkCalls": 0}
        if project_type == "mixed":
            base["changedFiles"] = 4
        if warnings:
            base["changedFiles"] = min(base["changedFiles"], 3)
        return base

    def _metadata_exists(self, root: Path, validator: WorkspaceBoundaryValidator, relative: str) -> bool:
        path = root / relative
        return path.exists() and validator.safe_to_read_metadata(path).status != "blocked"

    def _metadata_text(self, root: Path, validator: WorkspaceBoundaryValidator, relative: str) -> str:
        path = root / relative
        decision = validator.safe_to_read_metadata(path)
        if not decision.allowed or not path.exists():
            return ""
        try:
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return ""

    def _package_json(self, root: Path, validator: WorkspaceBoundaryValidator) -> dict[str, Any]:
        text = self._metadata_text(root, validator, "package.json")
        if not text:
            return {}
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return {}
        return data if isinstance(data, dict) else {}

    def _pyproject(self, root: Path, validator: WorkspaceBoundaryValidator) -> dict[str, Any]:
        text = self._metadata_text(root, validator, "pyproject.toml")
        if not text:
            return {}
        try:
            data = tomllib.loads(text)
        except tomllib.TOMLDecodeError:
            return {}
        return data if isinstance(data, dict) else {}

    def _git_summary(self, root: Path) -> dict[str, Any]:
        if shutil.which("git") is None:
            return {"isRepository": False, "branch": None, "clean": None}
        if self._git_text(root, ["rev-parse", "--is-inside-work-tree"]) != "true":
            return {"isRepository": False, "branch": None, "clean": None}
        status = self._git_text(root, ["status", "--porcelain=v1"])
        return {
            "isRepository": True,
            "branch": self._git_text(root, ["branch", "--show-current"]),
            "clean": status == "",
        }

    def _git_text(self, root: Path, args: list[str]) -> str | None:
        try:
            result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, timeout=5, shell=False)
        except (OSError, subprocess.TimeoutExpired):
            return None
        return result.stdout.strip() if result.returncode == 0 else None

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()
