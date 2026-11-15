from execucern import ApprovalToken, Firewall, Rule
import pytest


def test_unknown_tool_is_blocked_and_not_called():
    fw = Firewall({"refund": Rule(allow=True)}, "dev-secret")
    with pytest.raises(PermissionError, match="TOOL_NOT_ALLOWED"):
        fw.execute("agent-1", "delete_db", {"id": "7"}, lambda **_: True)


def test_exact_action_approval_is_required_and_bound_to_arguments():
    fw = Firewall({"refund": Rule(allow=True, require_approval=True)}, "dev-secret")
    approval = ApprovalToken.issue("agent-1", "refund", {"order_id": "o-1", "amount": 20}, "dev-secret")
    with pytest.raises(PermissionError, match="ESCALATE"):
        fw.execute("agent-1", "refund", {"order_id": "o-1", "amount": 21}, lambda **_: True, approval)
    assert fw.execute("agent-1", "refund", {"order_id": "o-1", "amount": 20}, lambda **_: "ok", approval) == "ok"


def test_approval_cannot_be_replayed():
    fw = Firewall({"refund": Rule(allow=True, require_approval=True)}, "dev-secret")
    args = {"order_id": "o-1", "amount": 20}
    approval = ApprovalToken.issue("agent-1", "refund", args, "dev-secret")
    fw.execute("agent-1", "refund", args, lambda **_: "ok", approval)
    with pytest.raises(PermissionError, match="APPROVAL_REPLAYED"):
        fw.execute("agent-1", "refund", args, lambda **_: "bad", approval)


def test_audit_redacts_secret_values():
    events = []
    fw = Firewall({"send": Rule(allow=True)}, "dev-secret", audit_sink=events.append)
    fw.execute("agent-1", "send", {"to": "user@example.com", "api_key": "do-not-log"}, lambda **_: True)
    assert events[0]["arguments"]["api_key"] == "[REDACTED]"
    assert events[0]["decision"] == "ALLOW"


def test_call_limit_blocks_after_first_call():
    fw = Firewall({"read": Rule(allow=True, max_calls=1)}, "dev-secret")
    assert fw.execute("agent-1", "read", {}, lambda **_: 1) == 1
    with pytest.raises(PermissionError, match="CALL_LIMIT_EXCEEDED"):
        fw.execute("agent-1", "read", {}, lambda **_: 2)
