"""Lab 06 — Supervisor multi-agente con handoffs explícitos en LangGraph.

Por defecto el supervisor enruta con reglas deterministas. ``--live-router`` usa una salida
estructurada de gpt-5.6-luna, pero Python impide repetir especialistas y limita handoffs.

Ejecución:
    python modulo-04-agentes/labs/06_multiagente_supervisor.py
    python modulo-04-agentes/labs/06_multiagente_supervisor.py --live-router
"""

from __future__ import annotations

import argparse
import operator
import os
from pathlib import Path
from typing import Annotated, Literal, TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field
from rich.console import Console
from rich.table import Table

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
console = Console()
AgentName = Literal["researcher", "risk_analyst", "editor", "synthesize"]


class Report(TypedDict):
    agent: str
    finding: str
    evidence: list[str]


class TeamState(TypedDict):
    task: str
    next_agent: AgentName
    reports: Annotated[list[Report], operator.add]
    handoffs: int
    max_handoffs: int
    route_reason: str
    final: str
    live_router: bool


class RouteDecision(BaseModel):
    next_agent: Literal["researcher", "risk_analyst", "editor", "synthesize"]
    reason: str = Field(min_length=5, max_length=180)


def required_agents(task: str) -> list[str]:
    required = ["researcher", "editor"]
    if any(term in task.casefold() for term in ("riesgo", "seguridad", "producción", "coste")):
        required.insert(1, "risk_analyst")
    return required


def deterministic_route(state: TeamState) -> RouteDecision:
    completed = {report["agent"] for report in state["reports"]}
    for agent in required_agents(state["task"]):
        if agent not in completed:
            return RouteDecision(next_agent=agent, reason=f"falta el informe de {agent}")
    return RouteDecision(next_agent="synthesize", reason="están los informes requeridos")


def model_route(state: TeamState) -> RouteDecision:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("falta OPENAI_API_KEY para --live-router")
    from openai import OpenAI

    completed = [report["agent"] for report in state["reports"]]
    response = OpenAI(timeout=30.0, max_retries=2).responses.parse(
        model=MODEL,
        instructions=(
            "Eres supervisor. Elige un especialista que falte y sea necesario, o synthesize. "
            "No repitas agentes completados. La ruta es una decisión breve, no razonamiento privado."
        ),
        input=f"Tarea: {state['task']}\nCompletados: {completed}",
        text_format=RouteDecision,
        max_output_tokens=180,
    )
    if response.output_parsed is None:
        raise RuntimeError("el router no devolvió una decisión estructurada")
    return response.output_parsed


def supervisor(state: TeamState) -> dict:
    if state["handoffs"] >= state["max_handoffs"]:
        decision = RouteDecision(next_agent="synthesize", reason="presupuesto de handoffs agotado")
    else:
        proposed = model_route(state) if state["live_router"] else deterministic_route(state)
        completed = {report["agent"] for report in state["reports"]}
        missing = set(required_agents(state["task"])) - completed
        decision = (
            deterministic_route(state)
            if proposed.next_agent in completed
            or (proposed.next_agent == "synthesize" and missing)
            else proposed
        )
    return {
        "next_agent": decision.next_agent,
        "route_reason": decision.reason,
        "handoffs": state["handoffs"] + (decision.next_agent != "synthesize"),
    }


def researcher(state: TeamState) -> dict:
    return {
        "reports": [
            {
                "agent": "researcher",
                "finding": "Un grafo explícito permite medir trayectorias y limitar ciclos.",
                "evidence": ["LangGraph: StateGraph, conditional edges, checkpoints"],
            }
        ]
    }


def risk_analyst(state: TeamState) -> dict:
    return {
        "reports": [
            {
                "agent": "risk_analyst",
                "finding": "Tools con escritura exigen mínimo privilegio, idempotencia y aprobación.",
                "evidence": ["threat: prompt injection", "control: human-in-the-loop"],
            }
        ]
    }


def editor(state: TeamState) -> dict:
    prior = "; ".join(report["finding"] for report in state["reports"])
    return {
        "reports": [
            {
                "agent": "editor",
                "finding": f"Síntesis editorial preparada a partir de: {prior or 'brief inicial'}",
                "evidence": [report["agent"] for report in state["reports"]],
            }
        ]
    }


def synthesize(state: TeamState) -> dict:
    findings = " ".join(report["finding"] for report in state["reports"])
    report_count = len(state["reports"])
    report_label = "informe trazable" if report_count == 1 else "informes trazables"
    completed = {report["agent"] for report in state["reports"]}
    missing = [agent for agent in required_agents(state["task"]) if agent not in completed]
    coverage = (
        f"Cobertura incompleta por límite de handoffs; faltan: {', '.join(missing)}."
        if missing
        else "Se completaron todos los informes requeridos."
    )
    return {
        "final": (
            f"Propuesta para «{state['task']}»: {findings} "
            f"La decisión se apoya en {report_count} {report_label}. {coverage}"
        )
    }


def route(state: TeamState) -> AgentName:
    return state["next_agent"]


def build_graph():
    builder = StateGraph(TeamState)
    builder.add_node("supervisor", supervisor)
    builder.add_node("researcher", researcher)
    builder.add_node("risk_analyst", risk_analyst)
    builder.add_node("editor", editor)
    builder.add_node("synthesize", synthesize)
    builder.add_edge(START, "supervisor")
    builder.add_conditional_edges(
        "supervisor",
        route,
        {
            "researcher": "researcher",
            "risk_analyst": "risk_analyst",
            "editor": "editor",
            "synthesize": "synthesize",
        },
    )
    for agent in ("researcher", "risk_analyst", "editor"):
        builder.add_edge(agent, "supervisor")
    builder.add_edge("synthesize", END)
    return builder.compile()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "task",
        nargs="?",
        default="Diseña un agente de investigación seguro para producción",
    )
    parser.add_argument("--live-router", action="store_true")
    parser.add_argument("--max-handoffs", type=int, default=4)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not 1 <= args.max_handoffs <= 8:
        raise ValueError("max-handoffs debe estar entre 1 y 8")
    initial: TeamState = {
        "task": args.task,
        "next_agent": "researcher",
        "reports": [],
        "handoffs": 0,
        "max_handoffs": args.max_handoffs,
        "route_reason": "inicio",
        "final": "",
        "live_router": args.live_router,
    }
    result = build_graph().invoke(initial, {"recursion_limit": 30})
    table = Table(title="Informes especializados")
    table.add_column("agente")
    table.add_column("hallazgo")
    for report in result["reports"]:
        table.add_row(report["agent"], report["finding"])
    console.print(table)
    console.print(f"\n[bold green]Resultado:[/bold green] {result['final']}")
    console.print(f"[dim]Handoffs: {result['handoffs']} · último motivo: {result['route_reason']}[/dim]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
