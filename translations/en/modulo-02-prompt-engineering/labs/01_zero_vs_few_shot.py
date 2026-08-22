"""Lab 01 — Compare zero-shot and few-shot on the same cases.

The lab does not rely on a single run. Execute both variants on a small dataset, require an exact label, and report accuracy case by case. --dry-run prints both prompts without consuming API calls.

Execution:
    python modulo-02-prompt-engineering/labs/01_zero_vs_few_shot.py --dry-run
    python modulo-02-prompt-engineering/labs/01_zero_vs_few_shot.py --limit 12
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

from _common import DATA_DIR, OPENAI_MODEL, load_json, require_env
from rich.console import Console
from rich.table import Table

CATEGORIES = ("facturacion", "tecnico", "cuenta", "ventas")
ZERO_SYSTEM = (
    "Clasifica tickets de un SaaS. Devuelve exactamente una label en minúsculas: "
    "facturacion, tecnico, cuenta o ventas. No añadas explicación."
)
FEW_SYSTEM = ZERO_SYSTEM + (
    " Facturacion cubre cobros, impuestos y documentos de factura; cuenta cubre acceso, "
    "identidad y configuración del usuario; ventas cubre compra o ampliación; tecnico cubre "
    "fallos del producto."
)
FEW_EXAMPLES = [
    ("Me cobraron dos veces este mes.", "facturacion"),
    ("No puedo acceder porque perdí el segundo factor.", "cuenta"),
    ("La API devuelve 500 desde el deploy.", "tecnico"),
    ("¿Cuánto cuesta añadir 40 usuarios?", "ventas"),
]
console = Console()


@dataclass(frozen=True)
class Prediction:
    case_id: str
    expected: str
    predicted: str

    @property
    def correct(self) -> bool:
        return self.expected == self.predicted


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def build_input(ticket: str, few_shot: bool) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = [
        {"role": "system", "content": FEW_SYSTEM if few_shot else ZERO_SYSTEM}
    ]
    if few_shot:
        for example, label in FEW_EXAMPLES:
            messages.extend(
                [
                    {"role": "user", "content": f"<ticket>{example}</ticket>"},
                    {"role": "assistant", "content": label},
                ]
            )
    messages.append({"role": "user", "content": f"<ticket>{ticket}</ticket>"})
    return messages


def normalize_label(text: str) -> str:
    label = text.strip().lower().strip(". `\n\t")
    return label if label in CATEGORIES else f"invalid:{label[:30]}"


def classify(client, ticket: str, few_shot: bool) -> str:
    response = client.responses.create(
        model=OPENAI_MODEL,
        input=build_input(ticket, few_shot),
        temperature=0,
        max_output_tokens=20,
    )
    return normalize_label(response.output_text)


def evaluate(client, cases: list[dict], few_shot: bool) -> list[Prediction]:
    predictions = []
    for case in cases:
        predictions.append(
            Prediction(
                case_id=case["id"],
                expected=case["category"],
                predicted=classify(client, case["text"], few_shot),
            )
        )
    return predictions


def print_results(zero: list[Prediction], few: list[Prediction]) -> None:
    table = Table(title="Zero-shot vs few-shot", show_lines=True)
    table.add_column("Caso")
    table.add_column("Esperada")
    table.add_column("Zero-shot")
    table.add_column("Few-shot")
    for a, b in zip(zero, few, strict=True):
        table.add_row(
            a.case_id,
            a.expected,
            ("✓ " if a.correct else "✗ ") + a.predicted,
            ("✓ " if b.correct else "✗ ") + b.predicted,
        )
    console.print(table)
    for name, rows in (("zero-shot", zero), ("few-shot", few)):
        correct = sum(row.correct for row in rows)
        invalid = sum(row.predicted.startswith("invalid:") for row in rows)
        console.print(
            f"[bold]{name}[/bold]: accuracy={correct / len(rows):.1%} "
            f"({correct}/{len(rows)}), invalid={invalid}"
        )


def main() -> int:
    args = parse_args()
    cases = load_json(DATA_DIR / "prompt_eval_cases.json")[: args.limit]
    if not cases:
        console.print("[red]--limit debe seleccionar al menos un caso.[/red]")
        return 2
    if args.dry_run:
        console.rule("Zero-shot")
        console.print_json(data=build_input(cases[0]["text"], False))
        console.rule("Few-shot")
        console.print_json(data=build_input(cases[0]["text"], True))
        return 0

    require_env("OPENAI_API_KEY")
    from openai import OpenAI

    client = OpenAI(timeout=30.0, max_retries=2)
    zero = evaluate(client, cases, few_shot=False)
    few = evaluate(client, cases, few_shot=True)
    print_results(zero, few)
    console.print(
        "\n[dim]Conclusión válida: la variante que rindió mejor en estos casos. "
        "No generalices a otra distribución sin ampliar el dataset.[/dim]"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
