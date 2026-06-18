from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "security_safety_agent"
AGENT_NAME = "Security/Safety Review Agent"


@dataclass(frozen=True)
class ReviewFinding:
    severity: str
    category: str
    message: str
    path: str | None = None
    line: int | None = None
    match: str | None = None
    snippet: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "severity": self.severity,
            "category": self.category,
            "message": self.message,
        }
        if self.path is not None:
            data["path"] = self.path
        if self.line is not None:
            data["line"] = self.line
        if self.match is not None:
            data["match"] = self.match
        if self.snippet is not None:
            data["snippet"] = self.snippet
        return data


@dataclass
class SecurityReviewResult:
    metadata: dict[str, Any]
    git: dict[str, Any]
    protected_file_scan: dict[str, Any]
    secret_pattern_scan: dict[str, Any]
    private_path_scan: dict[str, Any]
    public_release_claim_scan: dict[str, Any]
    connector_placeholder_scan: dict[str, Any]
    public_readiness_docs_scan: dict[str, Any]
    dangerous_command_policy_scan: dict[str, Any]
    findings: list[ReviewFinding] = field(default_factory=list)
    verdict: str = "pass"
    recommended_next_actions: list[str] = field(default_factory=list)
    report_id: str | None = None
    report_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "metadata": self.metadata,
            "git": self.git,
            "protectedFileScan": self.protected_file_scan,
            "secretPatternScan": self.secret_pattern_scan,
            "privatePathScan": self.private_path_scan,
            "publicReleaseClaimScan": self.public_release_claim_scan,
            "connectorPlaceholderScan": self.connector_placeholder_scan,
            "publicReadinessDocsScan": self.public_readiness_docs_scan,
            "dangerousCommandPolicyScan": self.dangerous_command_policy_scan,
            "findings": [finding.to_dict() for finding in self.findings],
            "verdict": self.verdict,
            "recommendedNextActions": self.recommended_next_actions,
            "reportId": self.report_id,
            "reportPath": self.report_path,
        }
