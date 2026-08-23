"""Lab 01 — Bounded loop with terminal states and progress detection.

Run:
    python modulo-06-loop-engineering/labs/01_bounded_loop.py
"""

from __future__ import annotations

import json
from dataclasses import asdict

from _loop_core import ActionResult, Budgets, Decision, DurableLoop, LoopState


def planner(state: LoopState) -> Decision:
    remaining = int(state.observation or "3")
    if remaining == 0:
        return Decision(kind="final", answer="All bounded steps completed.")
    return Decision(kind="action", action="decrement", arguments={"value": remaining})


def executor(action: str, arguments: dict[str, object]) -> ActionResult:
    if action != "decrement":
        raise ValueError(f"unknown action: {action}")
    value = int(arguments["value"])
    next_value = value - 1
    return ActionResult(
        observation=str(next_value),
        progress_marker=f"remaining:{next_value}",
        tokens=25,
        cost_micros=10,
    )


def main() -> None:
    loop = DurableLoop(LoopState(run_id="bounded-01", task="Reach zero"), Budgets(max_steps=5))
    result = loop.run(planner, executor)
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
