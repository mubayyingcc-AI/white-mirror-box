# Execucern Execution Firewall

A small, model-agnostic **pre-execution guard for AI-agent tool calls**.

Execucern wraps the last trusted boundary before a tool or business API runs. It defaults to deny, supports `ALLOW`, `BLOCK`, and `ESCALATE`, binds approvals to the exact actor/tool/arguments, prevents approval replay, enforces simple budgets, and emits redacted audit events.

This is intentionally a narrow open-source wedge. It does not replace an identity provider, network policy, MCP authorization server, sandbox runtime, or immutable audit service. It does not make LLM execution deterministic. The goal is to give developers a useful control they can install in minutes and compose with LangGraph, OpenAI Agents, CrewAI, PydanticAI, raw Python, HTTP adapters, or MCP clients.

## Install and run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
pytest -q
python examples/basic.py
```

## Minimal integration

```python
from execucern import Firewall, Rule

firewall = Firewall(
    rules={
        "search_orders": Rule(allow=True),
        "refund_order": Rule(allow=True, require_approval=True),
    },
    approval_secret="load-from-a-secret-manager",
)

result = firewall.execute(
    "support-agent",
    "search_orders",
    {"query": "late shipment"},
    search_orders,
)
```

For `require_approval=True`, issue an `ApprovalToken` only after an independently authenticated reviewer or policy service approves the exact action. An approval for a different amount, target, actor, or tool is rejected.

## Why this wedge

Agent protocols standardize tool connectivity, but they do not by themselves enforce the application's authorization policy. MCP's own guidance treats tool descriptions as untrusted and calls for explicit consent and authorization controls. Execucern makes the enforcement point explicit and framework-agnostic.

The project deliberately calls its recording feature an **audit event**, not deterministic replay. A future replay package can add recorded tool-result fixtures and regression diffs without claiming that live external state is reproducible.

## Status and safety

Alpha, local-only SDK. Do not connect this prototype directly to production payment rails, destructive infrastructure, or sensitive customer data without an independent security review. The host application remains responsible for identity, secret storage, tool isolation, tenant separation, durable audit retention, and the final protected adapter.

## Project shape

- `execucern/` — zero-dependency Python SDK.
- `plugin.json` and `skills/` — portable Agent Plugin package metadata.
- `tests/` — negative and security-focused tests.
- `examples/` — copy-paste starting point.
- `FACT_CHECK_AND_PRODUCT_PLAN.md` — researched positioning, evidence, and next-stage roadmap.

## License

Apache-2.0.
