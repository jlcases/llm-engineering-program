"""Lab 04 — Bucle completo de tool use con Anthropic Messages API.

Muestra bloques tool_use/tool_result, ejecución de varias herramientas, errores y límite de pasos.
--dry-run prueba las funciones sin consumir API.

Ejecución:
    python modulo-02-prompt-engineering/labs/04_tool_use_anthropic.py --dry-run
    python modulo-02-prompt-engineering/labs/04_tool_use_anthropic.py \
        "¿Dónde está PED-1042 y cuántos días lleva en tránsito?"
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from datetime import date
from typing import Any

from _common import ANTHROPIC_MODEL, require_env
from rich.console import Console

SHIPMENTS = {
    "PED-1042": {
        "status": "in_transit",
        "city": "Zaragoza",
        "shipped_on": "2026-08-18",
        "estimated_delivery": "2026-08-22",
    },
    "PED-1099": {
        "status": "delivered",
        "city": "Valencia",
        "shipped_on": "2026-08-15",
        "estimated_delivery": "2026-08-19",
    },
}

TOOLS = [
    {
        "name": "get_shipment",
        "description": (
            "Recupera el estado logístico de un pedido existente por su ID. Úsala para saber "
            "ubicación, estado, fecha de envío o entrega estimada. Es de solo lectura."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "Identificador exacto con formato PED-NNNN",
                    "pattern": "^PED-[0-9]{4}$",
                }
            },
            "required": ["order_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "name": "days_between",
        "description": (
            "Calcula días naturales entre dos fechas ISO YYYY-MM-DD. Úsala para duraciones "
            "exactas; no calcules fechas mentalmente."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "format": "date"},
                "end_date": {"type": "string", "format": "date"},
            },
            "required": ["start_date", "end_date"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]
console = Console()


def get_shipment(order_id: str) -> dict[str, Any]:
    shipment = SHIPMENTS.get(order_id)
    if shipment is None:
        return {"ok": False, "error": "order_not_found", "order_id": order_id}
    return {"ok": True, "order_id": order_id, **shipment}


def days_between(start_date: str, end_date: str) -> dict[str, Any]:
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError:
        return {"ok": False, "error": "invalid_iso_date"}
    if end < start:
        return {"ok": False, "error": "end_before_start"}
    return {"ok": True, "days": (end - start).days}


TOOL_FUNCTIONS: dict[str, Callable[..., dict[str, Any]]] = {
    "get_shipment": get_shipment,
    "days_between": days_between,
}


def execute_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    function = TOOL_FUNCTIONS.get(name)
    if function is None:
        return {"ok": False, "error": "unknown_tool", "tool": name}
    try:
        return function(**arguments)
    except TypeError as exc:
        return {"ok": False, "error": "invalid_arguments", "detail": str(exc)}


def serialize_blocks(blocks: list[Any]) -> list[dict[str, Any]]:
    return [block.model_dump(mode="json") for block in blocks]


def run_agent(client, question: str, max_iterations: int = 5) -> str:
    messages: list[dict[str, Any]] = [{"role": "user", "content": question}]
    for iteration in range(1, max_iterations + 1):
        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=600,
            system=(
                "Ayuda con pedidos usando herramientas. La fecha actual de este ejercicio es "
                "2026-08-21. No inventes estados ni hagas aritmética de fechas mentalmente."
            ),
            messages=messages,
            tools=TOOLS,
        )
        tool_blocks = [block for block in response.content if block.type == "tool_use"]
        if not tool_blocks:
            console.print(f"[dim]Fin tras {iteration} iteración(es).[/dim]")
            return "".join(block.text for block in response.content if block.type == "text")

        messages.append({"role": "assistant", "content": serialize_blocks(response.content)})
        results = []
        for block in tool_blocks:
            output = execute_tool(block.name, block.input)
            console.print(f"[cyan]tool[/cyan] {block.name}({block.input}) → {output}")
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(output, ensure_ascii=False),
                    "is_error": not output.get("ok", False),
                }
            )
        messages.append({"role": "user", "content": results})
    raise RuntimeError(f"el agente superó {max_iterations} iteraciones")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "question",
        nargs="?",
        default="¿Dónde está PED-1042 y cuántos días lleva en tránsito a fecha 2026-08-21?",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.dry_run:
        console.print_json(
            data={
                "shipment": execute_tool("get_shipment", {"order_id": "PED-1042"}),
                "days": execute_tool(
                    "days_between",
                    {"start_date": "2026-08-18", "end_date": "2026-08-21"},
                ),
            }
        )
        return 0

    require_env("ANTHROPIC_API_KEY")
    from anthropic import Anthropic

    answer = run_agent(Anthropic(timeout=30.0, max_retries=2), args.question)
    console.print(f"\n[bold green]{answer}[/bold green]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
