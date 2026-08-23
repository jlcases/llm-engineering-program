"""Lab 02 — Checkpoint, reanudación e idempotencia de un efecto.

Ejecución:
    python modulo-06-loop-engineering/labs/02_durable_loop.py
"""

from __future__ import annotations

import json
from dataclasses import asdict

from _loop_core import ActionResult, Budgets, Decision, DurableLoop, LoopState

external_effects: list[str] = []


def planner(state: LoopState) -> Decision:
    if state.effect_receipts:
        return Decision(kind="final", answer="Notification committed exactly once.")
    return Decision(
        kind="action",
        action="notify",
        arguments={"message": "deployment-ready"},
        effect_key=f"{state.run_id}:notify:deployment-ready",
    )


def executor(action: str, arguments: dict[str, object]) -> ActionResult:
    if action != "notify":
        raise ValueError(f"unknown action: {action}")
    external_effects.append(str(arguments["message"]))
    return ActionResult(
        observation="notification accepted",
        progress_marker="notification:accepted",
        effect_applied=True,
    )


def main() -> None:
    loop = DurableLoop(LoopState(run_id="durable-01", task="Notify once"), Budgets(max_steps=4))
    loop.step(planner, executor)
    restored = DurableLoop.restore(loop.checkpoint())
    result = restored.run(planner, executor)
    print(json.dumps({"state": asdict(result), "external_effects": external_effects}, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
