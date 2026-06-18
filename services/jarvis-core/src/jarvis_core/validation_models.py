from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "validation_agent"
AGENT_NAME = "Validation Agent"

RUN_STATUSES = {"not_started", "in_progress", "passed", "failed", "blocked", "canceled"}
STEP_STATUSES = {"not_started", "passed", "failed", "blocked", "skipped"}


@dataclass(frozen=True)
class ValidationStep:
    step_id: str
    title: str
    instructions: str
    expected_result: str
    evidence_type: str
    required: bool
    category: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "stepId": self.step_id,
            "step_id": self.step_id,
            "title": self.title,
            "instructions": self.instructions,
            "expectedResult": self.expected_result,
            "expected_result": self.expected_result,
            "evidenceType": self.evidence_type,
            "evidence_type": self.evidence_type,
            "required": self.required,
            "category": self.category,
        }


@dataclass(frozen=True)
class ValidationRunbook:
    runbook_id: str
    title: str
    description: str
    target_environment: str
    steps: list[ValidationStep]
    safety_notes: list[str] = field(default_factory=list)
    non_goals: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "runbookId": self.runbook_id,
            "runbook_id": self.runbook_id,
            "title": self.title,
            "description": self.description,
            "targetEnvironment": self.target_environment,
            "target_environment": self.target_environment,
            "steps": [step.to_dict() for step in self.steps],
            "safetyNotes": list(self.safety_notes),
            "safety_notes": list(self.safety_notes),
            "nonGoals": list(self.non_goals),
            "non_goals": list(self.non_goals),
        }


@dataclass(frozen=True)
class ValidationStepResult:
    step_id: str
    status: str
    notes: str
    redacted_evidence: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "stepId": self.step_id,
            "step_id": self.step_id,
            "status": self.status,
            "notes": self.notes,
            "redactedEvidence": self.redacted_evidence,
            "redacted_evidence": self.redacted_evidence,
            "updatedAt": self.updated_at,
            "updated_at": self.updated_at,
        }


@dataclass(frozen=True)
class ValidationRun:
    run_id: str
    runbook_id: str
    status: str
    target_environment: str
    created_at: str
    updated_at: str
    started_at: str | None
    completed_at: str | None
    summary: str
    step_results: list[ValidationStepResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "runId": self.run_id,
            "run_id": self.run_id,
            "runbookId": self.runbook_id,
            "runbook_id": self.runbook_id,
            "status": self.status,
            "targetEnvironment": self.target_environment,
            "target_environment": self.target_environment,
            "createdAt": self.created_at,
            "created_at": self.created_at,
            "updatedAt": self.updated_at,
            "updated_at": self.updated_at,
            "startedAt": self.started_at,
            "started_at": self.started_at,
            "completedAt": self.completed_at,
            "completed_at": self.completed_at,
            "summary": self.summary,
            "stepResults": [result.to_dict() for result in self.step_results],
            "step_results": [result.to_dict() for result in self.step_results],
        }
