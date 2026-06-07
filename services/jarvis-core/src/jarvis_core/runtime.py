from __future__ import annotations

from dataclasses import asdict, dataclass
from uuid import uuid4

from .audit import JsonlLogger
from .permissions import PolicyCheckResult, check_action


@dataclass(frozen=True)
class ActionRequest:
    agent_id: str
    action_type: str
    target: str | None = None


@dataclass(frozen=True)
class ActionReceipt:
    action_id: str
    agent_id: str
    action_type: str
    status: str
    reason: str


class SafeActionRuntime:
    def __init__(self, logger: JsonlLogger):
        self.logger = logger

    def validate(self, request: ActionRequest) -> ActionReceipt:
        result: PolicyCheckResult = check_action(request.action_type, request.target)
        receipt = ActionReceipt(
            action_id=str(uuid4()),
            agent_id=request.agent_id,
            action_type=request.action_type,
            status=result.status,
            reason=result.reason,
        )
        self.logger.append("actions", asdict(receipt))
        if not result.allowed:
            self.logger.append("security", {"eventType": "action_blocked", **asdict(receipt)})
        return receipt

