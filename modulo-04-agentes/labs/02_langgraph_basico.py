"""Lab 02 — Primer grafo de estado con LangGraph 1.2.x, totalmente offline.

Construye un workflow de clasificación → respuesta → auditoría. Los nodos devuelven updates
parciales y las aristas, no el prompt, garantizan el orden.

Ejecución:
    python modulo-04-agentes/labs/02_langgraph_basico.py
"""

from __future__ import annotations

import argparse
import operator
from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from rich.console import Console
from rich.table import Table

console = Console()


class SupportState(TypedDict):
    question: str
    category: Literal["security", "billing", "technical", "general"]
    answer: str
    audit: Annotated[list[str], operator.add]


def classify(state: SupportState) -> dict:
    text = state["question"].casefold()
    if any(term in text for term in ("clave", "mfa", "seguridad", "token")):
        category = "security"
    elif any(term in text for term in ("factura", "cobro", "pago")):
        category = "billing"
    elif any(term in text for term in ("error", "api", "latencia")):
        category = "technical"
    else:
        category = "general"
    return {"category": category, "audit": [f"classified:{category}"]}


def answer(state: SupportState) -> dict:
    policies = {
        "security": "Revoca la credencial afectada y escala al equipo de seguridad.",
        "billing": "Verifica factura, moneda y estado antes de modificar un cobro.",
        "technical": "Recoge request ID, intervalo temporal y región antes del diagnóstico.",
        "general": "Aclara el objetivo y el resultado esperado antes de actuar.",
    }
    return {
        "answer": policies[state["category"]],
        "audit": [f"answered:{state['category']}"],
    }


def audit(state: SupportState) -> dict:
    checks = [
        "answer_non_empty" if state["answer"].strip() else "answer_empty",
        "category_known" if state["category"] in {"security", "billing", "technical", "general"} else "category_unknown",
    ]
    return {"audit": checks}


def build_graph():
    builder = StateGraph(SupportState)
    builder.add_node("classify", classify)
    builder.add_node("answer", answer)
    builder.add_node("audit", audit)
    builder.add_edge(START, "classify")
    builder.add_edge("classify", "answer")
    builder.add_edge("answer", "audit")
    builder.add_edge("audit", END)
    return builder.compile()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "question",
        nargs="?",
        default="He publicado por error una clave API, ¿qué hago?",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = build_graph().invoke(
        {"question": args.question, "category": "general", "answer": "", "audit": []}
    )
    table = Table(title="Estado final")
    table.add_column("campo")
    table.add_column("valor")
    for key in ("question", "category", "answer", "audit"):
        table.add_row(key, str(result[key]))
    console.print(table)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
