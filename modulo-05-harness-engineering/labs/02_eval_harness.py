"""Lab 02 — Evaluation harness con trials aislados y graders separados.

Ejecución:
    python modulo-05-harness-engineering/labs/02_eval_harness.py
"""

from __future__ import annotations

import json
import tempfile
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    instruction: str
    fixture: str
    expected_marker: str


@dataclass(frozen=True)
class TrialResult:
    task_id: str
    output: str
    outcome_exists: bool
    marker_present: bool
    leaked_files: tuple[str, ...]
    elapsed_ms: int

    @property
    def passed(self) -> bool:
        return self.outcome_exists and self.marker_present and not self.leaked_files


Candidate = Callable[[TaskSpec, Path], str]


def run_trial(task: TaskSpec, candidate: Candidate) -> TrialResult:
    started = time.monotonic_ns()
    with tempfile.TemporaryDirectory(prefix=f"llmec-eval-{task.task_id}-") as temporary:
        workspace = Path(temporary)
        (workspace / "input.txt").write_text(task.fixture, encoding="utf-8")
        output = candidate(task, workspace)
        artifact = workspace / "artifact.txt"
        allowed = {"input.txt", "artifact.txt"}
        leaked = tuple(sorted(path.name for path in workspace.iterdir() if path.name not in allowed))
        outcome_exists = artifact.is_file()
        marker_present = outcome_exists and task.expected_marker in artifact.read_text(encoding="utf-8")
    return TrialResult(
        task_id=task.task_id,
        output=output,
        outcome_exists=outcome_exists,
        marker_present=marker_present,
        leaked_files=leaked,
        elapsed_ms=(time.monotonic_ns() - started) // 1_000_000,
    )


def run_suite(tasks: list[TaskSpec], candidate: Candidate, *, workers: int = 2) -> dict[str, object]:
    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(lambda task: run_trial(task, candidate), tasks))
    passed = sum(result.passed for result in results)
    return {
        "passed": passed,
        "total": len(results),
        "pass_rate": passed / len(results) if results else 0.0,
        "results": [asdict(result) | {"passed": result.passed} for result in results],
    }


def deterministic_candidate(task: TaskSpec, workspace: Path) -> str:
    source = (workspace / "input.txt").read_text(encoding="utf-8")
    artifact = f"{task.expected_marker}\n{source.upper()}"
    (workspace / "artifact.txt").write_text(artifact, encoding="utf-8")
    return "completed"


def main() -> None:
    tasks = [
        TaskSpec("contract", "Create a contract", "provider-neutral", "CONTRACT_OK"),
        TaskSpec("trace", "Create a trace", "observable", "TRACE_OK"),
    ]
    print(json.dumps(run_suite(tasks, deterministic_candidate), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
