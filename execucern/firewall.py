"""Small, local pre-execution policy guard for agent tool calls."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import hmac
import json
import secrets
from typing import Any, Callable, Mapping


def _now() -> int:
    return int(datetime.now(timezone.utc).timestamp())


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode()).hexdigest()


def _redact(value: Any) -> Any:
    secret_words = ("token", "secret", "password", "api_key", "apikey", "authorization", "private_key")
    if isinstance(value, Mapping):
        return {str(k): ("[REDACTED]" if any(w in str(k).lower() for w in secret_words) else _redact(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact(v) for v in value]
    if isinstance(value, tuple):
        return [_redact(v) for v in value]
    return value


@dataclass(frozen=True)
class Rule:
    """A tool rule. Unknown tools are denied by default."""
    allow: bool = False
    require_approval: bool = False
    max_calls: int | None = None


@dataclass(frozen=True)
class ApprovalToken:
    actor: str
    tool: str
    arguments_hash: str
    issued_at: int
    expires_at: int
    nonce: str
    signature: str

    @classmethod
    def issue(cls, actor: str, tool: str, arguments: Mapping[str, Any], secret: str, ttl_seconds: int = 300) -> "ApprovalToken":
        now = _now()
        args_hash = _digest(_canonical(dict(arguments)))
        nonce = secrets.token_urlsafe(18)
        body = f"{actor}|{tool}|{args_hash}|{now}|{now + ttl_seconds}|{nonce}"
        signature = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
        return cls(actor, tool, args_hash, now, now + ttl_seconds, nonce, signature)

    def valid_for(self, actor: str, tool: str, arguments: Mapping[str, Any], secret: str, now: int | None = None) -> bool:
        current = _now() if now is None else now
        if current >= self.expires_at or actor != self.actor or tool != self.tool:
            return False
        if _digest(_canonical(dict(arguments))) != self.arguments_hash:
            return False
        body = f"{self.actor}|{self.tool}|{self.arguments_hash}|{self.issued_at}|{self.expires_at}|{self.nonce}"
        expected = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, self.signature)


@dataclass(frozen=True)
class Decision:
    decision: str
    reason: str
    event_id: str
    tool: str
    arguments_hash: str


@dataclass
class Firewall:
    """Fail-closed guard that must sit immediately before a protected tool call.

    This is a local policy component, not a network proxy, identity provider, or sandbox.
    """
    rules: Mapping[str, Rule]
    approval_secret: str = field(repr=False)
    audit_sink: Callable[[dict[str, Any]], None] | None = None
    _calls: dict[str, int] = field(default_factory=dict, init=False, repr=False)
    _used_approvals: set[str] = field(default_factory=set, init=False, repr=False)

    def _emit(self, decision: str, reason: str, actor: str, tool: str, arguments: Mapping[str, Any]) -> Decision:
        args_hash = _digest(_canonical(dict(arguments)))
        event_id = secrets.token_hex(12)
        event = {
            "event_id": event_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "decision": decision,
            "reason": reason,
            "actor": actor,
            "tool": tool,
            "arguments_hash": args_hash,
            "arguments": _redact(dict(arguments)),
        }
        if self.audit_sink:
            self.audit_sink(event)
        return Decision(decision, reason, event_id, tool, args_hash)

    def evaluate(self, actor: str, tool: str, arguments: Mapping[str, Any], approval: ApprovalToken | None = None) -> Decision:
        rule = self.rules.get(tool)
        if rule is None or not rule.allow:
            return self._emit("BLOCK", "TOOL_NOT_ALLOWED", actor, tool, arguments)
        used = self._calls.get(tool, 0)
        if rule.max_calls is not None and used >= rule.max_calls:
            return self._emit("BLOCK", "CALL_LIMIT_EXCEEDED", actor, tool, arguments)
        if rule.require_approval:
            if approval is None or not approval.valid_for(actor, tool, arguments, self.approval_secret):
                return self._emit("ESCALATE", "EXACT_ACTION_APPROVAL_REQUIRED", actor, tool, arguments)
            if approval.nonce in self._used_approvals:
                return self._emit("BLOCK", "APPROVAL_REPLAYED", actor, tool, arguments)
            self._used_approvals.add(approval.nonce)
        self._calls[tool] = used + 1
        return self._emit("ALLOW", "POLICY_MATCH", actor, tool, arguments)

    def execute(self, actor: str, tool: str, arguments: Mapping[str, Any], fn: Callable[..., Any], approval: ApprovalToken | None = None) -> Any:
        """Evaluate and invoke only after an ALLOW decision.

        The callable is intentionally supplied by the host application so this SDK can wrap
        Python functions, HTTP adapters, MCP clients, or any other tool boundary.
        """
        decision = self.evaluate(actor, tool, arguments, approval)
        if decision.decision != "ALLOW":
            raise PermissionError(f"{decision.decision}: {decision.reason}")
        return fn(**dict(arguments))
