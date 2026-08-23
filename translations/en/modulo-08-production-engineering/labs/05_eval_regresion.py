"""Lab 05 — Deterministic regression gate for CI.

Compares baseline and candidate on the same cases, reports global/segment metrics, and returns
exit code 1 if the contract is violated. ``--simulate-regression`` demonstrates that the gate blocks.

Execution:
    python modulo-08-production-engineering/labs/05_eval_regresion.py
    python modulo-08-production-engineering/labs/05_eval_regresion.py --simulate-regression
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

from rich.console import Console
from rich.table import Table

DATASET = Path(__file__).resolve().parent / "data" / "regression_cases.json"
console = Console()


@dataclass(frozen=True)
class Prediction:
    category: str
    escalate: bool


def baseline(text: str) -> Prediction:
    lowered = text.casefold()
    if any(term in lowered for term in ("factura", "cobro", "tarjeta", "iva")):
        category = "billing"
    elif any(term in lowered for term in ("api", "503", "latencia", "timeout", "jobs")):
        category = "technical"
    else:
        category = "account"
    return Prediction(category, any(term in lowered for term in ("producción", "robado", "todos")))


def candidate(text: str, simulate_regression: bool = False) -> Prediction:
    lowered = text.casefold()
    if simulate_regression and "factura" in lowered:
        return Prediction("account", False)
    rules = {
        "security": ("clave api", "mfa", "token de sesión", "otro tenant", "robado"),
        "billing": ("factura", "cobro", "tarjeta", "iva"),
        "technical": ("api", "503", "latencia", "webhooks", "timeout", "despliegue", "jobs"),
    }
    category = next(
        (label for label, keywords in rules.items() if any(term in lowered for term in keywords)),
        "account",
    )
    critical = (
        category == "security"
        or "producción" in lowered
        or "duplicado" in lowered
        or "todos los jobs" in lowered
        or "12 segundos" in lowered
    )
    return Prediction(category, critical)


def f1(tp: int, fp: int, fn: int) -> float:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def evaluate(cases: list[dict], predictor) -> tuple[dict, list[dict]]:
    records = []
    by_segment: dict[str, list[bool]] = defaultdict(list)
    tp = fp = fn = 0
    critical_total = critical_correct = 0
    for case in cases:
        prediction = predictor(case["text"])
        category_ok = prediction.category == case["category"]
        escalate_ok = prediction.escalate == case["escalate"]
        by_segment[case["segment"]].append(category_ok and escalate_ok)
        if prediction.escalate and case["escalate"]:
            tp += 1
        elif prediction.escalate and not case["escalate"]:
            fp += 1
        elif not prediction.escalate and case["escalate"]:
            fn += 1
        if case["segment"] == "critical":
            critical_total += 1
            critical_correct += int(category_ok and prediction.escalate)
        records.append(
            {
                "id": case["id"],
                "expected": {"category": case["category"], "escalate": case["escalate"]},
                "prediction": asdict(prediction),
                "exact": category_ok and escalate_ok,
            }
        )
    metrics = {
        "category_accuracy": sum(record["prediction"]["category"] == record["expected"]["category"] for record in records) / len(records),
        "exact_match": sum(record["exact"] for record in records) / len(records),
        "escalation_f1": f1(tp, fp, fn),
        "critical_recall": critical_correct / critical_total,
        "segments": {
            segment: sum(values) / len(values) for segment, values in sorted(by_segment.items())
        },
    }
    return metrics, records


def gate(baseline_metrics: dict, candidate_metrics: dict) -> list[str]:
    failures = []
    if candidate_metrics["category_accuracy"] < 0.90:
        failures.append("category_accuracy < 0.90")
    if candidate_metrics["critical_recall"] < 1.0:
        failures.append("critical_recall < 1.00")
    if candidate_metrics["escalation_f1"] < 0.90:
        failures.append("escalation_f1 < 0.90")
    if candidate_metrics["exact_match"] + 0.02 < baseline_metrics["exact_match"]:
        failures.append("exact_match regresa más de 0.02 frente al baseline")
    for segment, score in candidate_metrics["segments"].items():
        if score < 0.75:
            failures.append(f"segmento {segment} < 0.75")
    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DATASET)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--simulate-regression", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cases = json.loads(args.dataset.read_text(encoding="utf-8"))
    baseline_metrics, _ = evaluate(cases, baseline)
    candidate_metrics, records = evaluate(
        cases,
        lambda text: candidate(text, args.simulate_regression),
    )
    failures = gate(baseline_metrics, candidate_metrics)
    table = Table(title="Regression gate")
    table.add_column("métrica")
    table.add_column("baseline", justify="right")
    table.add_column("candidate", justify="right")
    for name in ("category_accuracy", "exact_match", "escalation_f1", "critical_recall"):
        table.add_row(name, f"{baseline_metrics[name]:.3f}", f"{candidate_metrics[name]:.3f}")
    console.print(table)
    result = {
        "dataset": str(args.dataset),
        "cases": len(cases),
        "baseline": baseline_metrics,
        "candidate": candidate_metrics,
        "gate": {"passed": not failures, "failures": failures},
        "records": records,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if failures:
        console.print("[red]GATE FAIL:[/red] " + "; ".join(failures))
        return 1
    console.print("[green]GATE PASS[/green]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
