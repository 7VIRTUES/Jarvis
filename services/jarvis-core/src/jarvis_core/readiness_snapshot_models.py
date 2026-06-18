from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "private_alpha_readiness_agent"
AGENT_NAME = "Private-Alpha Readiness Snapshot Agent"
MODE = "local_readiness_snapshot"
ALLOWED_VERDICTS = {"ready_for_manual_vm_validation", "needs_evidence", "needs_review", "blocked"}


@dataclass(frozen=True)
class ReadinessSection:
    section_id: str
    title: str
    status: str
    summary: str
    items: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sectionId": self.section_id,
            "section_id": self.section_id,
            "title": self.title,
            "status": self.status,
            "summary": self.summary,
            "items": dict(self.items),
        }


@dataclass(frozen=True)
class ReadinessSnapshot:
    snapshot_id: str
    generated_at: str
    overall_verdict: str
    summary: str
    sections: dict[str, ReadinessSection]
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    recommended_next_actions: list[str] = field(default_factory=list)
    report_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshotId": self.snapshot_id,
            "snapshot_id": self.snapshot_id,
            "generatedAt": self.generated_at,
            "generated_at": self.generated_at,
            "agentId": AGENT_ID,
            "agent_id": AGENT_ID,
            "agentName": AGENT_NAME,
            "agent_name": AGENT_NAME,
            "mode": MODE,
            "overallVerdict": self.overall_verdict,
            "overall_verdict": self.overall_verdict,
            "summary": self.summary,
            "sections": {key: section.to_dict() for key, section in self.sections.items()},
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "recommendedNextActions": list(self.recommended_next_actions),
            "recommended_next_actions": list(self.recommended_next_actions),
            "reportId": self.report_id,
            "report_id": self.report_id,
        }
