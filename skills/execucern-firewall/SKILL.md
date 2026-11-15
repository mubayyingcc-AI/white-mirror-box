---
name: execucern-firewall
description: Wrap consequential AI-agent tool calls with a fail-closed policy check, exact-action approval, and redacted audit event.
---

# Execucern Execution Firewall

Use the `execucern` Python package at the last trusted boundary before a tool or business API executes.

## Required behavior

- Default-deny unknown tools.
- Classify tools as allowed or approval-required in host application code.
- Bind approvals to actor, tool name, normalized arguments, expiry, and a one-time nonce.
- Treat `ESCALATE` as a stop: do not call the tool until an authorized approval token is issued.
- Keep secrets out of audit payloads.
- Treat this package as a policy guard, not as proof of identity, a network isolation boundary, or a production sandbox.

## Minimal integration

```python
from execucern import Firewall, Rule

firewall = Firewall(
    rules={"search_orders": Rule(allow=True), "refund_order": Rule(allow=True, require_approval=True)},
    approval_secret="load-from-a-secret-manager",
)
result = firewall.execute("support-agent", "search_orders", {"query": "late shipment"}, search_orders)
```

For high-impact actions, issue an `ApprovalToken` only after an independently authenticated human or policy service approves the exact action.
