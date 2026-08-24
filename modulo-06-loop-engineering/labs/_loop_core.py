"""Máquina de estados offline para los labs de Loop Engineering."""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any

CHECKPOINT_VERSION = 2
SUPPORTED_CHECKPOINT_VERSIONS = {1, CHECKPOINT_VERSION}


def _require_non_negative_int(value: int, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be a non-negative integer")


class RunStatus(StrEnum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    EXHAUSTED = "exhausted"
    CANCELLED = "cancelled"
    NEEDS_HUMAN = "needs_human"


TERMINAL_STATUSES = {
    RunStatus.SUCCEEDED,
    RunStatus.FAILED,
    RunStatus.EXHAUSTED,
    RunStatus.CANCELLED,
    RunStatus.NEEDS_HUMAN,
}


@dataclass(frozen=True)
class Budgets:
    max_steps: int = 8
    max_elapsed_ms: int = 30_000
    max_tokens: int = 8_000
    max_cost_micros: int = 100_000
    max_effects: int = 3
    max_stagnant_steps: int = 2

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            _require_non_negative_int(value, name)
        if self.max_elapsed_ms == 0:
            raise ValueError("max_elapsed_ms must be greater than zero")


@dataclass
class Usage:
    steps: int = 0
    tokens: int = 0
    cost_micros: int = 0
    effects: int = 0

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            _require_non_negative_int(value, name)


@dataclass(frozen=True)
class Decision:
    kind: str
    action: str | None = None
    arguments: dict[str, Any] = field(default_factory=dict)
    effect_key: str | None = None
    answer: str | None = None
    reason: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.kind, str) or not self.kind.strip():
            raise ValueError("decision kind cannot be blank")
        for name in ("action", "effect_key", "answer", "reason"):
            value = getattr(self, name)
            if value is not None and not isinstance(value, str):
                raise TypeError(f"{name} must be a string or None")
        if self.effect_key is not None and not self.effect_key.strip():
            raise ValueError("effect_key cannot be blank")
        if not isinstance(self.arguments, dict):
            raise TypeError("arguments must be a JSON object")
        try:
            json.dumps(self.arguments, ensure_ascii=False)
        except (TypeError, ValueError, RecursionError) as exc:
            raise TypeError("arguments must be JSON serializable") from exc


@dataclass(frozen=True)
class ActionResult:
    observation: str
    progress_marker: str
    tokens: int = 0
    cost_micros: int = 0
    effect_applied: bool = False

    def __post_init__(self) -> None:
        _require_non_negative_int(self.tokens, "tokens")
        _require_non_negative_int(self.cost_micros, "cost_micros")
        if not isinstance(self.observation, str) or not isinstance(self.progress_marker, str):
            raise TypeError("observation and progress_marker must be strings")
        if not isinstance(self.effect_applied, bool):
            raise TypeError("effect_applied must be a boolean")


@dataclass
class LoopState:
    run_id: str
    task: str
    status: RunStatus = RunStatus.RUNNING
    observation: str = ""
    answer: str | None = None
    terminal_reason: str | None = None
    usage: Usage = field(default_factory=Usage)
    last_progress_marker: str | None = None
    stagnant_steps: int = 0
    cancel_requested: bool = False
    events: list[dict[str, Any]] = field(default_factory=list)
    effect_receipts: dict[str, dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.run_id, str) or not isinstance(self.task, str):
            raise TypeError("run_id and task must be strings")
        if not self.run_id.strip() or not self.task.strip():
            raise ValueError("run_id and task cannot be blank")
        if not isinstance(self.status, RunStatus):
            raise TypeError("status must be a RunStatus")
        if not isinstance(self.observation, str):
            raise TypeError("observation must be a string")
        for name in ("answer", "terminal_reason", "last_progress_marker"):
            value = getattr(self, name)
            if value is not None and not isinstance(value, str):
                raise TypeError(f"{name} must be a string or None")
        _require_non_negative_int(self.stagnant_steps, "stagnant_steps")
        if not isinstance(self.cancel_requested, bool):
            raise TypeError("cancel_requested must be a boolean")
        if not isinstance(self.usage, Usage):
            raise TypeError("usage must be a Usage instance")
        if not isinstance(self.events, list) or not isinstance(self.effect_receipts, dict):
            raise TypeError("events and effect_receipts have invalid types")
        if any(not isinstance(event, dict) for event in self.events):
            raise ValueError("events must contain JSON objects")
        try:
            json.dumps(self.events, ensure_ascii=False)
        except (TypeError, ValueError, RecursionError) as exc:
            raise TypeError("events must be JSON serializable") from exc
        for effect_key, receipt in self.effect_receipts.items():
            if not isinstance(effect_key, str) or not effect_key or not isinstance(receipt, dict):
                raise ValueError("invalid effect receipt")
            if set(receipt) != {"result"} or not isinstance(receipt["result"], dict):
                raise ValueError("invalid effect receipt payload")
            ActionResult(**receipt["result"])


Planner = Callable[[LoopState], Decision]
Executor = Callable[[str, dict[str, Any]], ActionResult]


class DurableLoop:
    def __init__(self, state: LoopState, budgets: Budgets, *, started_ns: int | None = None) -> None:
        if not isinstance(state, LoopState) or not isinstance(budgets, Budgets):
            raise TypeError("state and budgets must use their declared contract types")
        now = time.monotonic_ns()
        if started_ns is not None and (isinstance(started_ns, bool) or not isinstance(started_ns, int) or started_ns < 0 or started_ns > now):
            raise ValueError("started_ns must be a valid past monotonic timestamp")
        self.state = state
        self.budgets = budgets
        self.started_ns = now if started_ns is None else started_ns

    def _event(self, kind: str, payload: dict[str, Any]) -> None:
        self.state.events.append({"sequence": len(self.state.events) + 1, "kind": kind, **payload})

    def _finish(self, status: RunStatus, reason: str, answer: str | None = None) -> RunStatus:
        self.state.status = status
        self.state.terminal_reason = reason
        self.state.answer = answer
        self._event("terminal", {"status": status.value, "reason": reason})
        return status

    def _elapsed_ms(self) -> int:
        return (time.monotonic_ns() - self.started_ns) // 1_000_000

    def _budget_reason(self) -> str | None:
        usage = self.state.usage
        if usage.steps >= self.budgets.max_steps:
            return "step_budget"
        if self._elapsed_ms() >= self.budgets.max_elapsed_ms:
            return "time_budget"
        if usage.tokens > self.budgets.max_tokens:
            return "token_budget"
        if usage.cost_micros > self.budgets.max_cost_micros:
            return "cost_budget"
        if usage.effects > self.budgets.max_effects:
            return "effect_budget"
        return None

    def request_cancel(self) -> None:
        self.state.cancel_requested = True

    def step(self, planner: Planner, executor: Executor) -> RunStatus:
        if self.state.status in TERMINAL_STATUSES:
            return self.state.status
        if self.state.cancel_requested:
            return self._finish(RunStatus.CANCELLED, "cancel_requested")
        if reason := self._budget_reason():
            return self._finish(RunStatus.EXHAUSTED, reason)

        try:
            decision = planner(deepcopy(self.state))
        except Exception as exc:  # noqa: BLE001 -- planner failures become durable terminal state.
            self._event("planner_error", {"type": type(exc).__name__})
            return self._finish(RunStatus.FAILED, "unhandled_planner_error")
        if not isinstance(decision, Decision):
            self._event("planner_error", {"type": "InvalidDecisionType"})
            return self._finish(RunStatus.FAILED, "invalid_decision")
        self.state.usage.steps += 1
        self._event("decision", {"kind": decision.kind, "action": decision.action})

        if decision.kind == "final":
            if not decision.answer:
                return self._finish(RunStatus.FAILED, "empty_final_answer")
            return self._finish(RunStatus.SUCCEEDED, "goal_reached", decision.answer)
        if decision.kind == "impossible":
            return self._finish(RunStatus.FAILED, decision.reason or "task_impossible")
        if decision.kind == "human":
            return self._finish(RunStatus.NEEDS_HUMAN, decision.reason or "human_judgement_required")
        if decision.kind != "action" or not decision.action:
            return self._finish(RunStatus.FAILED, "invalid_decision")
        if decision.effect_key and decision.effect_key in self.state.effect_receipts:
            receipt = self.state.effect_receipts[decision.effect_key]
            result = ActionResult(**receipt["result"])
            self._event("deduplicated", {"effect_key": decision.effect_key})
        else:
            if decision.effect_key and self.state.usage.effects >= self.budgets.max_effects:
                return self._finish(RunStatus.EXHAUSTED, "effect_budget")
            try:
                result = executor(decision.action, deepcopy(decision.arguments))
                if not isinstance(result, ActionResult):
                    raise TypeError("executor must return ActionResult")
            except Exception as exc:  # noqa: BLE001 -- the loop converts tool failures into state.
                self._event("action_error", {"type": type(exc).__name__})
                return self._finish(RunStatus.FAILED, "unhandled_action_error")
            if result.effect_applied:
                if not decision.effect_key:
                    return self._finish(RunStatus.FAILED, "effect_without_idempotency_key")
                self.state.usage.effects += 1
                self.state.effect_receipts[decision.effect_key] = {"result": asdict(result)}

        self.state.observation = result.observation
        self.state.usage.tokens += result.tokens
        self.state.usage.cost_micros += result.cost_micros
        if result.progress_marker == self.state.last_progress_marker:
            self.state.stagnant_steps += 1
        else:
            self.state.last_progress_marker = result.progress_marker
            self.state.stagnant_steps = 0
        self._event("observation", {"progress_marker": result.progress_marker})

        if self.state.stagnant_steps >= self.budgets.max_stagnant_steps:
            return self._finish(RunStatus.EXHAUSTED, "no_progress")
        if reason := self._budget_reason():
            return self._finish(RunStatus.EXHAUSTED, reason)
        return self.state.status

    def run(self, planner: Planner, executor: Executor) -> LoopState:
        while self.state.status not in TERMINAL_STATUSES:
            self.step(planner, executor)
        return self.state

    def checkpoint(self) -> str:
        payload = {
            "checkpoint_version": CHECKPOINT_VERSION,
            "elapsed_ms": self._elapsed_ms(),
            "budgets": asdict(self.budgets),
            "state": asdict(self.state) | {"status": self.state.status.value},
        }
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)

    @classmethod
    def restore(cls, checkpoint: str) -> DurableLoop:
        payload = json.loads(checkpoint)
        if not isinstance(payload, dict):
            raise TypeError("checkpoint must be a JSON object")
        version = payload.get("checkpoint_version")
        if version not in SUPPORTED_CHECKPOINT_VERSIONS:
            raise ValueError("unsupported checkpoint version")
        required = {"checkpoint_version", "budgets", "state"}
        if version == CHECKPOINT_VERSION:
            required.add("elapsed_ms")
        if set(payload) != required:
            raise ValueError("checkpoint has missing or unknown fields")
        elapsed_ms = payload.get("elapsed_ms", 0)
        _require_non_negative_int(elapsed_ms, "elapsed_ms")
        if not isinstance(payload["state"], dict) or not isinstance(payload["budgets"], dict):
            raise TypeError("checkpoint state and budgets must be objects")
        raw_state = dict(payload["state"])
        raw_state["status"] = RunStatus(raw_state["status"])
        if not isinstance(raw_state.get("usage"), dict):
            raise TypeError("checkpoint usage must be an object")
        raw_state["usage"] = Usage(**raw_state["usage"])
        state = LoopState(**raw_state)
        started_ns = time.monotonic_ns() - elapsed_ms * 1_000_000
        return cls(state, Budgets(**payload["budgets"]), started_ns=started_ns)
