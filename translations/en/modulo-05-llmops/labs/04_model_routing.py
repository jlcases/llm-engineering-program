"""Lab 04 — Auditable model routing between GPT-5.6 Luna, Terra, and Sol.

The deterministic router uses visible signals and a risk-based override. By default, it simulates
responses; ``--live`` calls the Responses API. Aliases were verified in August 2026 and are
stored in variables to allow migration without modifying the policy.

Execution:
    python modulo-05-llmops/labs/04_model_routing.py
    python modulo-05-llmops/labs/04_model_routing.py --live "Analiza este contrato"
"""

from __future__ import annotations

import argparse
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")
LUNA = os.getenv("OPENAI_LUNA_MODEL", "gpt-5.6-luna")
TERRA = os.getenv("OPENAI_TERRA_MODEL", "gpt-5.6-terra")
SOL = os.getenv("OPENAI_SOL_MODEL", "gpt-5.6-sol")
console = Console()


@dataclass(frozen=True)
class Route:
    tier: Literal["luna", "terra", "sol"]
    model: str
    reason: str
    risk_override: bool


def route(question: str) -> Route:
    text = question.casefold()
    high_risk = any(term in text for term in ("diagnóstico médico", "asesoría legal", "transferencia", "credencial de producción"))
    complex_signals = sum(
        term in text
        for term in ("demuestra", "arquitectura", "compara", "contrato", "planifica", "causa raíz")
    )
    if high_risk:
        return Route("sol", SOL, "dominio de alto impacto: máximo tier y revisión humana", True)
    if len(question) > 500 or complex_signals >= 2:
        return Route("terra", TERRA, "múltiples señales de análisis o contexto largo", False)
    return Route("luna", LUNA, "tarea breve de volumen", False)


def execute(question: str, selected: Route, live: bool) -> tuple[str, float]:
    started = time.perf_counter()
    if not live:
        answer = f"[simulado:{selected.model}] Procesaría la tarea con la política {selected.tier}."
    else:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("falta OPENAI_API_KEY para --live")
        from openai import OpenAI

        response = OpenAI(timeout=45.0, max_retries=2).responses.create(
            model=selected.model,
            instructions="Responde en español, de forma verificable y concisa.",
            input=question,
            reasoning={"effort": "low" if selected.tier == "luna" else "medium"},
            max_output_tokens=500,
        )
        answer = response.output_text
    return answer, (time.perf_counter() - started) * 1_000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "question",
        nargs="?",
        default="Resume en tres puntos qué es un cache semántico.",
    )
    parser.add_argument("--live", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    selected = route(args.question)
    answer, latency_ms = execute(args.question, selected, args.live)
    table = Table(title="Decisión de routing")
    table.add_column("tier")
    table.add_column("modelo")
    table.add_column("override")
    table.add_column("motivo")
    table.add_column("ms", justify="right")
    table.add_row(
        selected.tier,
        selected.model,
        str(selected.risk_override),
        selected.reason,
        f"{latency_ms:.1f}",
    )
    console.print(table)
    console.print(answer)
    if selected.risk_override:
        console.print("[yellow]El tier no sustituye la revisión humana exigida por la política.[/yellow]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
