"""Lab 07 — Comparación estadística pareada de dos prompts.

Lee la salida del lab 06, calcula discordancias de McNemar, p exacta y un intervalo bootstrap para
la diferencia de accuracy. Si no existe output previo usa un ejemplo incluido y reproducible.

Ejecución:
    python modulo-02-prompt-engineering/labs/07_ab_testing_prompts.py
    python modulo-02-prompt-engineering/labs/07_ab_testing_prompts.py --input outputs/module02_eval_latest.json
"""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from _common import OUTPUTS_DIR
from rich.console import Console
from rich.table import Table

EXAMPLE = {
    "baseline": [1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
    "candidate": [1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0],
}
console = Console()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=OUTPUTS_DIR / "module02_eval_latest.json")
    parser.add_argument("--bootstrap", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def load_outcomes(path: Path) -> tuple[list[int], list[int], str]:
    if not path.exists():
        return EXAMPLE["baseline"], EXAMPLE["candidate"], "ejemplo incorporado"
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    baseline_rows = payload["variants"]["baseline"]["rows"]
    candidate_rows = payload["variants"]["candidate"]["rows"]
    if [row["case_id"] for row in baseline_rows] != [row["case_id"] for row in candidate_rows]:
        raise ValueError("las variantes no contienen los mismos casos en el mismo orden")
    baseline = [int(row["category_correct"]) for row in baseline_rows]
    candidate = [int(row["category_correct"]) for row in candidate_rows]
    return baseline, candidate, str(path)


def exact_mcnemar(b: int, c: int) -> float:
    discordant = b + c
    if discordant == 0:
        return 1.0
    tail = sum(math.comb(discordant, k) for k in range(min(b, c) + 1)) / (2**discordant)
    return min(1.0, 2 * tail)


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    index = (len(ordered) - 1) * q
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return ordered[lower]
    weight = index - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def paired_bootstrap(
    baseline: list[int], candidate: list[int], *, repetitions: int, seed: int
) -> tuple[float, float]:
    if repetitions < 1000:
        raise ValueError("usa al menos 1000 repeticiones bootstrap")
    rng = random.Random(seed)
    n = len(baseline)
    differences = []
    for _ in range(repetitions):
        indices = [rng.randrange(n) for _ in range(n)]
        a = sum(baseline[i] for i in indices) / n
        b = sum(candidate[i] for i in indices) / n
        differences.append(b - a)
    return percentile(differences, 0.025), percentile(differences, 0.975)


def main() -> int:
    args = parse_args()
    try:
        baseline, candidate, source = load_outcomes(args.input)
        if len(baseline) != len(candidate) or not baseline:
            raise ValueError("se requieren pares no vacíos del mismo tamaño")
        ci_low, ci_high = paired_bootstrap(
            baseline, candidate, repetitions=args.bootstrap, seed=args.seed
        )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        console.print(f"[red]Input inválido:[/red] {exc}")
        return 2

    both_correct = sum(a == 1 and b == 1 for a, b in zip(baseline, candidate, strict=True))
    baseline_only = sum(a == 1 and b == 0 for a, b in zip(baseline, candidate, strict=True))
    candidate_only = sum(a == 0 and b == 1 for a, b in zip(baseline, candidate, strict=True))
    both_wrong = sum(a == 0 and b == 0 for a, b in zip(baseline, candidate, strict=True))
    p_value = exact_mcnemar(baseline_only, candidate_only)
    accuracy_a = sum(baseline) / len(baseline)
    accuracy_b = sum(candidate) / len(candidate)

    table = Table(title="Resultados pareados")
    table.add_column("Celda")
    table.add_column("Casos", justify="right")
    table.add_row("ambos correctos", str(both_correct))
    table.add_row("solo baseline", str(baseline_only))
    table.add_row("solo candidate", str(candidate_only))
    table.add_row("ambos fallan", str(both_wrong))
    console.print(table)
    console.print(f"Fuente: {source}")
    console.print(f"Accuracy baseline={accuracy_a:.1%} · candidate={accuracy_b:.1%}")
    console.print(f"Diferencia={accuracy_b - accuracy_a:+.1%}")
    console.print(f"IC bootstrap 95 %=[{ci_low:+.1%}, {ci_high:+.1%}]")
    console.print(f"McNemar exacto p={p_value:.4f}")

    if ci_low > 0 and p_value < 0.05:
        console.print("[green]Evidencia consistente de mejora en este dataset.[/green]")
    elif ci_high < 0 and p_value < 0.05:
        console.print("[red]Evidencia consistente de regresión en este dataset.[/red]")
    else:
        console.print(
            "[yellow]Resultado inconcluso:[/yellow] no equivale a empate; amplía casos o acepta "
            "que el efecto detectable es limitado."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
