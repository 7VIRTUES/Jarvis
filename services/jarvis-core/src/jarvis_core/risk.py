from __future__ import annotations

from dataclasses import dataclass
from typing import Any


DEFAULT_RISK_BUDGET = {
    "maxChangedFiles": 10,
    "maxDiffLines": 700,
    "maxRepairAttempts": 2,
    "maxCodexRunsPerTask": 3,
    "maxNewDependenciesWithoutApproval": 0,
}


@dataclass(frozen=True)
class RiskBudgetResult:
    allowed: bool
    approval_required: bool
    risk_level: str
    reason: str


def validate_risk_budget(plan: dict[str, Any] | None, budget: dict[str, int] | None = None) -> RiskBudgetResult:
    effective_budget = {**DEFAULT_RISK_BUDGET, **(budget or {})}
    plan = plan or {}
    checks = [
        ("changedFiles", "maxChangedFiles"),
        ("diffLines", "maxDiffLines"),
        ("repairAttempts", "maxRepairAttempts"),
        ("codexRuns", "maxCodexRunsPerTask"),
        ("newDependencies", "maxNewDependenciesWithoutApproval"),
    ]
    exceeded: list[str] = []
    for field, limit in checks:
        try:
            value = int(plan.get(field, 0))
        except (TypeError, ValueError):
            return RiskBudgetResult(False, True, "high", f"{field} must be an integer")
        if value < 0:
            return RiskBudgetResult(False, True, "high", f"{field} cannot be negative")
        if value > effective_budget[limit]:
            exceeded.append(f"{field}={value} exceeds {limit}={effective_budget[limit]}")
    if exceeded:
        return RiskBudgetResult(False, True, "high", "; ".join(exceeded))
    return RiskBudgetResult(True, False, "low", "plan is within risk budget")
