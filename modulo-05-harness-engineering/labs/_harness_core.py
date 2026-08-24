"""Núcleo offline para los labs de Harness Engineering."""

from __future__ import annotations

import json
import re
import time
from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

SENSITIVE_KEYS = {
    "api_key",
    "authorization",
    "cookie",
    "password",
    "private_key",
    "secret",
    "set_cookie",
    "token",
}
SENSITIVE_SUFFIXES = ("_api_key", "_password", "_private_key", "_secret", "_token")


def _normalized_key(value: Any) -> str:
    text = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", str(value))
    return re.sub(r"[^a-z0-9]+", "_", text.casefold()).strip("_")


def _is_sensitive_key(value: Any) -> bool:
    normalized = _normalized_key(value)
    return normalized in SENSITIVE_KEYS or normalized.endswith(SENSITIVE_SUFFIXES)


def _redact(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): "[REDACTED]" if _is_sensitive_key(key) else _redact(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
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
    _validator: Draft202012Validator = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("capability name cannot be blank")
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("capability description cannot be blank")
        if not isinstance(self.effect, str) or not self.effect.strip():
            raise ValueError("capability effect cannot be blank")
        if not isinstance(self.requires_approval, bool):
            raise TypeError("requires_approval must be a boolean")
        if not isinstance(self.input_schema, dict):
            raise TypeError("input_schema must be a JSON Schema object")
        if not callable(self.handler):
            raise TypeError("handler must be callable")
        schema = deepcopy(self.input_schema)
        Draft202012Validator.check_schema(schema)
        object.__setattr__(self, "input_schema", schema)
        object.__setattr__(self, "_validator", Draft202012Validator(schema))

    def public_contract(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": deepcopy(self.input_schema),
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
        if not 1 <= trace_preview_chars <= 100_000:
            raise ValueError("trace_preview_chars must be between 1 and 100000")
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

        if not isinstance(arguments, dict):
            self.trace.append("denied", name, {"reason": "invalid_arguments_type"})
            raise TypeError("capability arguments must be a JSON object")
        try:
            json.dumps(arguments, ensure_ascii=False)
        except (TypeError, ValueError, RecursionError) as exc:
            self.trace.append("denied", name, {"reason": "unserializable_arguments"})
            raise TypeError("capability arguments must be JSON serializable") from exc

        validation_errors = sorted(
            capability._validator.iter_errors(arguments),
            key=lambda error: tuple(str(part) for part in error.absolute_path),
        )
        if validation_errors:
            first = validation_errors[0]
            pointer = "$" + "".join(f"[{part!r}]" for part in first.absolute_path)
            self.trace.append(
                "denied",
                name,
                {"reason": "invalid_arguments", "path": pointer, "rule": first.validator},
            )
            raise ValueError(f"invalid arguments for {name} at {pointer}: {first.validator}")

        self.trace.append("call", name, {"arguments": arguments})
        started = time.monotonic_ns()
        try:
            result = capability.handler(arguments)
        except Exception as exc:
            self.trace.append(
                "error",
                name,
                {"error_type": type(exc).__name__},
            )
            raise
        elapsed_ms = (time.monotonic_ns() - started) // 1_000_000
        if not isinstance(result, Mapping):
            self.trace.append("error", name, {"error_type": "InvalidCapabilityResult"})
            raise TypeError(f"capability {name} must return a mapping")
        try:
            serialized = json.dumps(_redact(result), ensure_ascii=False)
        except (TypeError, ValueError, RecursionError) as exc:
            self.trace.append("error", name, {"error_type": "UnserializableCapabilityResult"})
            raise TypeError(f"capability {name} returned an unserializable mapping") from exc
        preview = serialized[: self.trace_preview_chars]
        self.trace.append(
            "result",
            name,
            {"elapsed_ms": elapsed_ms, "preview": preview, "truncated": len(serialized) > len(preview)},
        )
        return dict(result)
