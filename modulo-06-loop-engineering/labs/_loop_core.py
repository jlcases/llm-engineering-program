"""Máquina de estados offline para los labs de Loop Engineering."""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any

CHECKPOINT_VERSION = 1


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


@dataclass
class Usage:
    steps: int = 0
    tokens: int = 0
    cost_micros: int = 0
    effects: int = 0


@dataclass(frozen=True)
class Decision:
    kind: str
    action: str | None = None
    arguments: dict[str, Any] = field(default_factory=dict)
    effect_key: str | None = None
    answer: str | None = None
    reason: str | None = None


@dataclass(frozen=True)
class ActionResult:
    observation: str
    progress_marker: str
    tokens: int = 0
    cost_micros: int = 0
    effect_applied: bool = False


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


Planner = Callable[[LoopState], Decision]
Executor = Callable[[str, dict[str, Any]], ActionResult]


class DurableLoop:
    def __init__(self, state: LoopState, budgets: Budgets, *, started_ns: int | None = None) -> None:
        self.state = state
        self.budgets = budgets
        self.started_ns = started_ns or time.monotonic_ns()

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
        if usage.tokens >= self.budgets.max_tokens:
            return "token_budget"
        if usage.cost_micros >= self.budgets.max_cost_micros:
            return "cost_budget"
        if usage.effects >= self.budgets.max_effects:
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

        decision = planner(self.state)
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
            try:
                result = executor(decision.action, decision.arguments)
            except Exception as exc:  # noqa: BLE001 -- the loop converts tool failures into state.
                self._event("action_error", {"type": type(exc).__name__, "message": str(exc)})
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
            "budgets": asdict(self.budgets),
            "state": asdict(self.state) | {"status": self.state.status.value},
        }
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)

    @classmethod
    def restore(cls, checkpoint: str) -> DurableLoop:
        payload = json.loads(checkpoint)
        if payload.get("checkpoint_version") != CHECKPOINT_VERSION:
            raise ValueError("unsupported checkpoint version")
        raw_state = payload["state"]
        raw_state["status"] = RunStatus(raw_state["status"])
        raw_state["usage"] = Usage(**raw_state["usage"])
        state = LoopState(**raw_state)
        return cls(state, Budgets(**payload["budgets"]))
