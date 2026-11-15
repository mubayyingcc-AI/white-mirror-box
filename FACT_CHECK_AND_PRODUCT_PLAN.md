# Execucern: Fact Check and Fast Open-Source Wedge

## Verdict

The problem is real and payable, but the original brief overstates differentiation and bundles too many products. The strongest first product is not a new agent harness. It is a **drop-in pre-execution tool-call guard** that developers can place immediately before a consequential function, HTTP request, or MCP call. It should be open-source, local-first, framework-agnostic, and useful without sending prompts or customer data to a hosted service.

The existing GitHub portfolio supports this direction. `white-mirror-box` was empty and is now the cleanest public home for the narrow SDK. `ActBound` already contains a deeper research prototype for signed task manifests, receipt consumption, budgets, and simulated payment enforcement. `Envarith-System` already contains the control-plane concepts for authority envelopes, revocation, evidence, and accountability. Execucern should be the small developer wedge that can later integrate those systems, not a fourth overlapping governance platform.

## What the original brief gets right

**The execution boundary is the right problem.** OWASP recommends per-tool least privilege, explicit authorization for sensitive operations, exact-action approval binding, replay protection, and fail-closed behavior for unknown tools or missing approval [1]. These are concrete controls, not merely observability features.

**MCP increases the relevance of the problem.** MCP standardizes how hosts, clients, and servers exchange resources, prompts, and tools, but its specification also says tool descriptions and annotations should be treated cautiously and that hosts should provide consent and authorization controls [2]. The current authorization specification covers transport-level OAuth for HTTP MCP servers; it does not define an application's business policy for whether a particular agent may refund order X for amount Y [3]. That application-level gap is a reasonable product surface.

**The market is validated, not empty.** LangSmith provides framework-agnostic tracing, monitoring, and evaluation [4]. NeuralTrust documents inline evaluation of pending tool calls and blocking before dispatch, including the operational cost of an extra evaluation round trip per tool call [5]. Palo Alto documents an MCP security product surface in Prisma AIRS [6]. Therefore customers understand the category, but “we block tool calls” alone is not a moat.

## What needs correction

**“Deterministic replay” needs narrower language.** Recording an agent trace is useful. Re-running it against captured tool-result fixtures can produce a reproducible regression test. But external state, permissions, time, retries, and side effects change. The MVP should say **recorded execution fixtures** or **trace replay for regression tests**, and explicitly avoid claiming that live agent behavior becomes deterministic.

**“Model-agnostic harness” is the wrong adoption entry point.** Teams already choose LangGraph, OpenAI Agents, CrewAI, PydanticAI, Vercel AI SDK, or custom code. Requiring a harness migration creates unnecessary friction. The SDK therefore accepts a tool name, argument object, and callable; adapters can be added for frameworks later.

**“Execution firewall” is a positioning metaphor, not automatically a security boundary.** A Python wrapper can be bypassed if the agent can call the underlying tool directly. The README must state that the host must place the guard at the last trusted boundary and prevent alternate paths. A production version needs protected adapters, identity integration, revocation checks immediately before execution, idempotency, and deployment-level complete mediation.

**“Less than 10 ms” is not yet a supported fact.** A local dictionary/policy check may be fast, but approval lookup, remote policy evaluation, identity checks, logging, and network hops change the number. Benchmark local evaluation and report p50/p95 on defined hardware before making a latency claim.

**Open-core monetization is plausible but not proven.** Governance, hosted policy management, enterprise identity, multi-tenant audit retention, incident workflows, and support are plausible paid expansions. They are hypotheses until users install the OSS package and repeatedly ask for those features.

## MVP implemented in `white-mirror-box`

The first release contains:

- A zero-dependency Python package with `Firewall`, `Rule`, `ApprovalToken`, and `Decision`.
- Default-deny behavior for unknown tools.
- `ALLOW`, `BLOCK`, and `ESCALATE` decisions.
- Exact approval binding to actor, tool, normalized arguments, expiry, and one-time nonce.
- Simple call-count limits as an initial budget control.
- Redacted audit events with argument hashes.
- A portable `plugin.json` and Agent Plugin skill package.
- Negative tests for bypass-oriented cases and a copy-paste example.

The package intentionally does not claim identity, sandbox isolation, MCP OAuth, tamper-proof storage, or production readiness.

## Recommended product sequence

### 1. Public developer wedge

Ship the SDK, examples, framework adapters, and a CLI that can validate a policy file. Add adapters for one Python framework and one MCP client only after collecting real integration requests. Publish a short demo showing a refund or destructive operation being escalated and a safe read operation proceeding.

### 2. Recorded fixtures, not “magic replay”

Add a recorder that stores tool-call envelopes and tool-result fixtures with secret redaction. Add a replay runner that invokes the agent against fixtures and diffs the proposed tool trajectory. Label this as offline regression testing. Keep destructive tools mocked by default.

### 3. Protected adapter and approval service

Move exact-action approval, revocation, and idempotency into a server-side adapter. Integrate the stronger signed-receipt and budget ideas from ActBound. The adapter—not the browser and not the model—must recheck authorization immediately before the side effect.

### 4. Control plane

Reuse Envarith's authority-envelope and evidence concepts for policy distribution, approvals, tenant isolation, retention, and incident review. Keep the local SDK usable when the control plane is absent.

### 5. Paid expansion

Test demand for hosted policy management, SSO/RBAC, approval workflows, central audit retention, SIEM export, policy simulation, and support. Do not build all of these before the open-source wedge has adoption signals.

## Who to target first

Start with platform and AI-infrastructure engineers at companies deploying agents that can **write data or create externally visible effects**. The first action classes should be refunds, email sending, ticket/status changes, deployment actions, and database mutations. They are easy to demonstrate and easy to explain. Avoid starting with generic “all agent safety,” which is too broad for a new project.

The initial CTA should be: “Wrap one consequential tool call in five minutes and see every allow, block, and escalation decision locally.” The success metric is not website traffic. It is installation-to-first-policy, number of wrapped tools, and whether users keep the guard in their execution path.

## Claims to use and claims to avoid

Use: “framework-agnostic pre-execution guard,” “default-deny policy,” “exact-action approvals,” “redacted audit events,” and “offline trace fixtures planned.”

Avoid: “prevents prompt injection,” “deterministic agents,” “complete execution firewall,” “guaranteed compliance,” “immutable audit,” “production-ready,” and “under 10 ms” until each claim has a narrowly defined test and evidence.

## Sources

[1]: https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html "OWASP AI Agent Security Cheat Sheet"
[2]: https://modelcontextprotocol.io/specification/2025-06-18 "Model Context Protocol Specification"
[3]: https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization "MCP Authorization Specification"
[4]: https://www.langchain.com/langsmith "LangSmith Observability"
[5]: https://docs.neuraltrust.ai/integrations/langchain "NeuralTrust LangChain Integration"
[6]: https://docs.paloaltonetworks.com/content/techdocs/en_US/prisma-airs/ai-agent-identity/understanding-the-prisma-airs-mcp-server "Prisma AIRS MCP Server"
[7]: https://github.com/agentplugins/agent-plugins-spec "Agent Plugins Specification Repository"
