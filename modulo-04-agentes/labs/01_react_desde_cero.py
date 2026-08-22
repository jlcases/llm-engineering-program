"""Lab 01 — Bucle ReAct desde cero, con tools tipadas y límite de pasos.

El modo offline ejecuta un plan determinista y permite probar el orquestador sin API. ``--live``
usa Responses API con gpt-5.6-luna por defecto. La traza registra acciones y observaciones, no una
cadena privada de pensamiento.

Ejecución:
    python modulo-04-agentes/labs/01_react_desde_cero.py
    python modulo-04-agentes/labs/01_react_desde_cero.py --live
"""

from __future__ import annotations

import argparse
import ast
import json
import operator
import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
console = Console()

KNOWLEDGE = {
    "respuestas api": "Responses es la API recomendada para integraciones nuevas de OpenAI.",
    "mcp": "MCP estandariza tools, resources y prompts entre clientes y servidores.",
    "langgraph": "LangGraph modela flujos con estado, nodos, aristas, ciclos y checkpoints.",
}
OPERATORS: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


@dataclass(frozen=True)
class TraceEvent:
    step: int
    kind: str
    name: str
    payload: str


def search_course(query: str) -> dict[str, Any]:
    """Busca conceptos del curso en un índice local pequeño y de solo lectura."""
    normalized = query.casefold()
    matches = [
        {"topic": topic, "content": content}
        for topic, content in KNOWLEDGE.items()
        if topic in normalized or any(word in content.casefold() for word in normalized.split())
    ]
    return {"matches": matches[:3], "count": len(matches)}


def calculate(expression: str) -> dict[str, float | str]:
    """Evalúa una expresión aritmética con +, -, * y /; nunca ejecuta código Python."""

    def evaluate(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, int | float):
            return float(node.value)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -evaluate(node.operand)
        if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
            return OPERATORS[type(node.op)](evaluate(node.left), evaluate(node.right))
        raise ValueError("expresión no permitida")

    if len(expression) > 100:
        raise ValueError("expresión demasiado larga")
    value = evaluate(ast.parse(expression, mode="eval"))
    if not (-1e12 <= value <= 1e12):
        raise ValueError("resultado fuera de rango")
    return {"expression": expression, "value": value}


TOOLS: dict[str, Callable[..., dict[str, Any]]] = {
    "search_course": search_course,
    "calculate": calculate,
}
TOOL_SCHEMAS = [
    {
        "type": "function",
        "name": "search_course",
        "description": "Busca conceptos de LLM engineering en el índice local de solo lectura.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string", "minLength": 2}},
            "required": ["query"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "calculate",
        "description": "Calcula aritmética básica con +, -, * y /.",
        "parameters": {
            "type": "object",
            "properties": {"expression": {"type": "string", "minLength": 1}},
            "required": ["expression"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


def safe_execute(name: str, arguments: str) -> dict[str, Any]:
    tool = TOOLS.get(name)
    if tool is None:
        return {"ok": False, "error": "unknown_tool", "tool": name}
    try:
        payload = json.loads(arguments)
        if not isinstance(payload, dict):
            raise TypeError("los argumentos deben ser un objeto JSON")
        return {"ok": True, "result": tool(**payload)}
    except (json.JSONDecodeError, TypeError, ValueError, ZeroDivisionError) as exc:
        return {"ok": False, "error": type(exc).__name__, "message": str(exc)}


def offline_run(question: str) -> tuple[str, list[TraceEvent]]:
    events = []
    search_result = search_course(question)
    events.append(TraceEvent(1, "action", "search_course", json.dumps({"query": question}, ensure_ascii=False)))
    events.append(TraceEvent(1, "observation", "search_course", json.dumps(search_result, ensure_ascii=False)))
    if search_result["count"]:
        evidence = " ".join(item["content"] for item in search_result["matches"])
        return f"Según el índice local: {evidence}", events
    return "El índice local no contiene evidencia suficiente para responder.", events


def live_run(question: str, max_steps: int) -> tuple[str, list[TraceEvent]]:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("falta OPENAI_API_KEY para --live")
    from openai import OpenAI

    client = OpenAI(timeout=30.0, max_retries=2)
    input_items: list[Any] = [{"role": "user", "content": question}]
    events: list[TraceEvent] = []
    for step in range(1, max_steps + 1):
        response = client.responses.create(
            model=MODEL,
            instructions=(
                "Responde en español. Usa tools cuando aporten evidencia o cálculo. No inventes "
                "resultados. Si una tool falla, corrige una vez o explica el límite."
            ),
            input=input_items,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
            reasoning={"effort": "low"},
            max_output_tokens=500,
        )
        input_items.extend(response.output)
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            answer = response.output_text.strip()
            if not answer:
                raise RuntimeError(f"respuesta final vacía; status={response.status}")
            events.append(TraceEvent(step, "final", MODEL, answer))
            return answer, events
        for call in calls:
            events.append(TraceEvent(step, "action", call.name, call.arguments))
            result = safe_execute(call.name, call.arguments)
            serialized = json.dumps(result, ensure_ascii=False)
            events.append(TraceEvent(step, "observation", call.name, serialized))
            input_items.append(
                {"type": "function_call_output", "call_id": call.call_id, "output": serialized}
            )
    return f"No se completó la tarea tras {max_steps} pasos; revisa la traza.", events


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "question",
        nargs="?",
        default="¿Qué es MCP y para qué sirve en un agente?",
    )
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--max-steps", type=int, default=4)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not 1 <= args.max_steps <= 10:
        raise ValueError("max-steps debe estar entre 1 y 10")
    answer, events = (
        live_run(args.question, args.max_steps)
        if args.live
        else offline_run(args.question)
    )
    table = Table(title="Traza observable")
    table.add_column("paso")
    table.add_column("tipo")
    table.add_column("nombre")
    table.add_column("payload", overflow="fold")
    for event in events:
        table.add_row(str(event.step), event.kind, event.name, event.payload)
    console.print(table)
    console.print(f"\n[bold green]Respuesta:[/bold green] {answer}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
