"""Lab 03 — Ciclo acotado y aristas condicionales en LangGraph.

El grafo busca evidencia, la evalúa y reformula hasta superar el umbral o consumir el presupuesto.
La condición de parada está en Python y siempre produce una salida degradada útil.

Ejecución:
    python modulo-04-agentes/labs/03_langgraph_ciclos_condicionales.py
"""

from __future__ import annotations

import argparse
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from rich.console import Console
from rich.table import Table

console = Console()
CORPUS = {
    "mcp": "MCP separa hosts, clientes y servidores y transporta JSON-RPC por stdio o HTTP.",
    "checkpoints": "LangGraph guarda estado por thread mediante un checkpointer.",
    "tools": "Una tool debe tener schema estrecho, permisos mínimos y errores estructurados.",
}


class ResearchState(TypedDict):
    question: str
    query: str
    attempts: int
    max_attempts: int
    evidence: list[str]
    confidence: float
    outcome: Literal["searching", "ready", "exhausted"]
    trace: list[str]


def search(state: ResearchState) -> dict:
    terms = set(state["query"].casefold().split())
    matches = [
        passage
        for topic, passage in CORPUS.items()
        if topic in state["query"].casefold()
        or terms & set(passage.casefold().replace(",", "").split())
    ]
    attempt = state["attempts"] + 1
    return {
        "attempts": attempt,
        "evidence": matches,
        "trace": state["trace"] + [f"search:{attempt}:{len(matches)}"],
    }


def evaluate(state: ResearchState) -> dict:
    confidence = min(1.0, 0.25 + 0.45 * len(state["evidence"]))
    if confidence >= 0.65:
        outcome = "ready"
    elif state["attempts"] >= state["max_attempts"]:
        outcome = "exhausted"
    else:
        outcome = "searching"
    return {
        "confidence": confidence,
        "outcome": outcome,
        "trace": state["trace"] + [f"evaluate:{outcome}:{confidence:.2f}"],
    }


def reformulate(state: ResearchState) -> dict:
    vocabulary = " mcp checkpoints tools seguridad"
    return {
        "query": state["question"] + vocabulary,
        "trace": state["trace"] + ["reformulate:controlled_expansion"],
    }


def route_after_evaluation(state: ResearchState) -> Literal["retry", "finish"]:
    return "retry" if state["outcome"] == "searching" else "finish"


def build_graph():
    builder = StateGraph(ResearchState)
    builder.add_node("search", search)
    builder.add_node("evaluate", evaluate)
    builder.add_node("reformulate", reformulate)
    builder.add_edge(START, "search")
    builder.add_edge("search", "evaluate")
    builder.add_conditional_edges(
        "evaluate",
        route_after_evaluation,
        {"retry": "reformulate", "finish": END},
    )
    builder.add_edge("reformulate", "search")
    return builder.compile()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", nargs="?", default="¿Cómo persiste estado un grafo?")
    parser.add_argument("--max-attempts", type=int, default=2)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not 1 <= args.max_attempts <= 5:
        raise ValueError("max-attempts debe estar entre 1 y 5")
    initial: ResearchState = {
        "question": args.question,
        "query": args.question,
        "attempts": 0,
        "max_attempts": args.max_attempts,
        "evidence": [],
        "confidence": 0.0,
        "outcome": "searching",
        "trace": [],
    }
    result = build_graph().invoke(initial, {"recursion_limit": 20})
    table = Table(title=f"Resultado: {result['outcome']}")
    table.add_column("paso")
    for event in result["trace"]:
        table.add_row(event)
    console.print(table)
    if result["outcome"] == "ready":
        console.print("[green]Evidencia:[/green] " + " ".join(result["evidence"]))
    else:
        console.print("[yellow]Presupuesto agotado: hace falta otra fuente o aclaración.[/yellow]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
