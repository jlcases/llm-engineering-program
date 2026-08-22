"""Lab 02 — La misma cadena instrumentada con LangSmith.

Sin ``--send`` fuerza tracing desactivado y funciona como smoke test local. Con ``--send`` exige
LANGSMITH_API_KEY, habilita el proyecto indicado y envía una traza de funciones simuladas: no
consume una API LLM.

Ejecución:
    python modulo-05-llmops/labs/02_langsmith_tracing.py
    python modulo-05-llmops/labs/02_langsmith_tracing.py --send --project llmops-course
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")
console = Console()


def configure(send: bool, project: str) -> None:
    if send and not os.getenv("LANGSMITH_API_KEY"):
        raise RuntimeError("falta LANGSMITH_API_KEY para --send")
    os.environ["LANGSMITH_TRACING"] = "true" if send else "false"
    os.environ["LANGSMITH_PROJECT"] = project


def build_traced_pipeline():
    from langsmith import traceable

    @traceable(name="retrieve-policy", run_type="retriever")
    def retrieve(question: str) -> list[dict]:
        return [
            {
                "id": "security-rotate-01",
                "content": "Revocar una clave expuesta antes de crear la sustituta.",
            }
        ]

    @traceable(name="generate-grounded", run_type="llm", metadata={"model": "simulated"})
    def generate(question: str, contexts: list[dict]) -> dict:
        return {
            "answer": "Revoca la clave expuesta antes de crear la sustituta.",
            "citations": [contexts[0]["id"]],
            "usage": {"input_tokens": 44, "output_tokens": 13},
        }

    @traceable(name="support-answer", run_type="chain", tags=["course", "offline-data"])
    def answer(question: str) -> dict:
        contexts = retrieve(question)
        return generate(question, contexts)

    return answer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--send", action="store_true")
    parser.add_argument("--project", default="llm-engineering-program")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configure(args.send, args.project)
    pipeline = build_traced_pipeline()
    result = pipeline("¿Qué hago si expongo una clave?")
    console.print_json(data=result)
    mode = "enviada" if args.send else "local, envío desactivado"
    console.print(f"[dim]Traza {mode}; proyecto={args.project}[/dim]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
