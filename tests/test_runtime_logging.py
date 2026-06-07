import json

from jarvis_core.audit import JsonlLogger
from jarvis_core.runtime import ActionRequest, SafeActionRuntime


def test_blocked_command_creates_security_event(tmp_path):
    logger = JsonlLogger(tmp_path)
    runtime = SafeActionRuntime(logger)

    receipt = runtime.validate(ActionRequest("coding_agent", "command", "git push"))

    assert receipt.status == "blocked"
    security_log = tmp_path / "security.jsonl"
    assert security_log.exists()
    events = [json.loads(line) for line in security_log.read_text(encoding="utf-8").splitlines()]
    assert events[0]["eventType"] == "action_blocked"
    assert events[0]["action_type"] == "command"

