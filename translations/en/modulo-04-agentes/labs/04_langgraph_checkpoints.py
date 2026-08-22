"""Lab 04 — Threads, checkpoints, and history with InMemorySaver.

Two invocations using the same thread continue the counter; another thread remains isolated. The
in-memory backend is for development only: a restart clears everything.

Execution:
    python modulo-04-agentes/labs/04_langgraph_checkpoints.py
"""

from __future__ import annotations

import operator
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from rich.console import Console
from rich.table import Table

console = Console()


class ConversationState(TypedDict):
    messages: Annotated[list[str], operator.add]
    turns: int


def respond(state: ConversationState) -> dict:
    user_message = state["messages"][-1]
    turn = state.get("turns", 0) + 1
    return {
        "messages": [f"assistant: turno {turn}; recibido '{user_message}'"],
        "turns": turn,
    }


def build_graph(checkpointer: InMemorySaver):
    builder = StateGraph(ConversationState)
    builder.add_node("respond", respond)
    builder.add_edge(START, "respond")
    builder.add_edge("respond", END)
    return builder.compile(checkpointer=checkpointer)


def invoke(graph, thread_id: str, message: str) -> dict:
    config = {"configurable": {"thread_id": thread_id}}
    return graph.invoke({"messages": [message]}, config)


def main() -> int:
    saver = InMemorySaver()
    graph = build_graph(saver)
    first = invoke(graph, "alice", "hola")
    second = invoke(graph, "alice", "continúa")
    isolated = invoke(graph, "bob", "hola")

    table = Table(title="Aislamiento por thread_id")
    table.add_column("invocación")
    table.add_column("turnos")
    table.add_column("último mensaje")
    for label, state in (("alice/1", first), ("alice/2", second), ("bob/1", isolated)):
        table.add_row(label, str(state["turns"]), state["messages"][-1])
    console.print(table)

    config = {"configurable": {"thread_id": "alice"}}
    history = list(graph.get_state_history(config))
    console.print(f"[bold]Checkpoints de alice:[/bold] {len(history)}")
    assert second["turns"] == 2 and isolated["turns"] == 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
