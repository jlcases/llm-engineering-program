"""Núcleo offline para los labs de Harness Engineering."""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

SENSITIVE_KEYS = {"api_key", "authorization", "password", "secret", "token"}


def _redact(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): "[REDACTED]" if str(key).casefold() in SENSITIVE_KEYS else _redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


@dataclass(frozen=True)
class Capability:
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[[dict[str, Any]], dict[str, Any]]
    effect: str = "read"
    requires_approval: bool = False

    def public_contract(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "effect": self.effect,
            "requires_approval": self.requires_approval,
        }


@dataclass(frozen=True)
class TraceEvent:
    sequence: int
    kind: str
    name: str
    monotonic_ms: int
    payload: dict[str, Any]


@dataclass
class RunTrace:
    run_id: str
    events: list[TraceEvent] = field(default_factory=list)

    def append(self, kind: str, name: str, payload: dict[str, Any]) -> None:
        self.events.append(
            TraceEvent(
                sequence=len(self.events) + 1,
                kind=kind,
                name=name,
                monotonic_ms=time.monotonic_ns() // 1_000_000,
                payload=_redact(payload),
            )
        )

    def as_json(self) -> str:
        return json.dumps(
            {"run_id": self.run_id, "events": [asdict(event) for event in self.events]},
            ensure_ascii=False,
            indent=2,
        )


class WorkspaceSandbox:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def resolve(self, relative_path: str) -> Path:
        requested = Path(relative_path)
        if requested.is_absolute():
            raise PermissionError("absolute paths are not allowed")
        resolved = (self.root / requested).resolve()
        if resolved != self.root and self.root not in resolved.parents:
            raise PermissionError("path escapes the sandbox")
        return resolved

    def read_text(self, relative_path: str) -> str:
        return self.resolve(relative_path).read_text(encoding="utf-8")

    def write_text(self, relative_path: str, content: str) -> dict[str, Any]:
        target = self.resolve(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {"path": relative_path, "bytes": len(content.encode("utf-8"))}


class AgentHarness:
    def __init__(
        self,
        *,
        run_id: str,
        capabilities: list[Capability],
        allowed: set[str],
        approved: set[str] | None = None,
        trace_preview_chars: int = 2_000,
    ) -> None:
        self._capabilities = {capability.name: capability for capability in capabilities}
        if len(self._capabilities) != len(capabilities):
            raise ValueError("capability names must be unique")
        unknown = allowed - self._capabilities.keys()
        if unknown:
            raise ValueError(f"unknown allowed capabilities: {sorted(unknown)}")
        self.allowed = frozenset(allowed)
        self.approved = frozenset(approved or set())
        self.trace_preview_chars = trace_preview_chars
        self.trace = RunTrace(run_id)

    def manifest(self) -> list[dict[str, Any]]:
        return [
            self._capabilities[name].public_contract()
            for name in sorted(self.allowed)
        ]

    def invoke(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        capability = self._capabilities.get(name)
        if capability is None:
            self.trace.append("denied", name, {"reason": "unknown_capability"})
            raise KeyError(f"unknown capability: {name}")
        if name not in self.allowed:
            self.trace.append("denied", name, {"reason": "not_allowed"})
            raise PermissionError(f"capability not allowed for this run: {name}")
        if capability.requires_approval and name not in self.approved:
            self.trace.append("denied", name, {"reason": "approval_required"})
            raise PermissionError(f"approval required: {name}")

        self.trace.append("call", name, {"arguments": arguments})
        started = time.monotonic_ns()
        try:
            result = capability.handler(arguments)
        except Exception as exc:
            self.trace.append(
                "error",
                name,
                {"error_type": type(exc).__name__, "message": str(exc)[: self.trace_preview_chars]},
            )
            raise
        elapsed_ms = (time.monotonic_ns() - started) // 1_000_000
        serialized = json.dumps(result, ensure_ascii=False, default=str)
        preview = serialized[: self.trace_preview_chars]
        self.trace.append(
            "result",
            name,
            {"elapsed_ms": elapsed_ms, "preview": preview, "truncated": len(serialized) > len(preview)},
        )
        return result
