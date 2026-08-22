"""Lab 02 — Razonamiento privado y self-consistency con voto mayoritario.

No intenta extraer chain-of-thought privado. Pide al modelo resolver internamente y emitir solo una
respuesta verificable. Compara una muestra directa con varias muestras y voto; --dry-run no llama
a la API.

Ejecución:
    python modulo-02-prompt-engineering/labs/02_chain_of_thought.py --dry-run
    python modulo-02-prompt-engineering/labs/02_chain_of_thought.py --samples 5
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from dataclasses import dataclass

from _common import OPENAI_MODEL, require_env
from rich.console import Console
from rich.table import Table

CASES = [
    ("Una licencia cuesta 18 € al mes. Hay 14 licencias y se aplica 15 % de descuento. Total mensual en euros.", "214.20"),
    ("Un job procesa 45 documentos por minuto. ¿Cuántos procesa en 2 horas y 20 minutos?", "6300"),
    ("Un presupuesto de 50 € consume 0,0125 € por consulta. ¿Cuántas consultas completas permite?", "4000"),
    ("De 240 evaluaciones, fallan 18. Da el porcentaje de éxito con una cifra decimal.", "92.5"),
]
ANSWER_RE = re.compile(r"ANSWER:\s*(-?[0-9]+(?:[.,][0-9]+)?)", re.IGNORECASE)
console = Console()


@dataclass(frozen=True)
class Sample:
    raw: str
    answer: str | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=int, default=5)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def prompt_for(problem: str, deliberate: bool) -> str:
    instruction = (
        "Resuelve el problema internamente, verifica unidades y aritmética, y no muestres "
        "tu razonamiento privado. "
        if deliberate
        else "Responde al problema. "
    )
    return instruction + "Emite una sola línea con el formato ANSWER: <número>.\n\n" + problem


def extract_answer(text: str) -> str | None:
    match = ANSWER_RE.search(text)
    return match.group(1).replace(",", ".") if match else None


def sample(client, problem: str, *, deliberate: bool, temperature: float) -> Sample:
    response = client.responses.create(
        model=OPENAI_MODEL,
        input=prompt_for(problem, deliberate),
        temperature=temperature,
        max_output_tokens=120,
    )
    return Sample(raw=response.output_text, answer=extract_answer(response.output_text))


def majority(samples: list[Sample]) -> tuple[str | None, int]:
    counts = Counter(item.answer for item in samples if item.answer is not None)
    return counts.most_common(1)[0] if counts else (None, 0)


def main() -> int:
    args = parse_args()
    if args.samples < 3:
        console.print("[red]Usa al menos 3 muestras para self-consistency.[/red]")
        return 2
    if args.dry_run:
        console.rule("Prompt directo")
        console.print(prompt_for(CASES[0][0], False))
        console.rule("Prompt deliberado")
        console.print(prompt_for(CASES[0][0], True))
        return 0

    require_env("OPENAI_API_KEY")
    from openai import OpenAI

    client = OpenAI(timeout=30.0, max_retries=2)
    table = Table(title=f"Self-consistency ({args.samples} muestras)", show_lines=True)
    table.add_column("Problema", max_width=42)
    table.add_column("Esperada")
    table.add_column("Directa T=0")
    table.add_column("Voto")
    table.add_column("Acuerdo")

    direct_hits = vote_hits = 0
    for problem, expected in CASES:
        direct = sample(client, problem, deliberate=False, temperature=0)
        variants = [
            sample(client, problem, deliberate=True, temperature=0.7)
            for _ in range(args.samples)
        ]
        voted, votes = majority(variants)
        direct_hits += direct.answer == expected
        vote_hits += voted == expected
        table.add_row(
            problem,
            expected,
            str(direct.answer),
            str(voted),
            f"{votes}/{args.samples}",
        )
    console.print(table)
    console.print(f"Directa: {direct_hits}/{len(CASES)} · voto: {vote_hits}/{len(CASES)}")
    console.print(
        "[dim]El acuerdo entre muestras es una señal, no una prueba: varias muestras pueden "
        "repetir el mismo error. El coste crece aproximadamente con el número de muestras.[/dim]"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
