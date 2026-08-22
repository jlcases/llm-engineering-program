"""Lab 03 — Complete function calling loop with the OpenAI Responses API.

Includes a strict schema, multiple tools, local execution, typed results, controlled errors, and
an iteration limit. --dry-run executes the tools directly and does not use the network.

Execution:
    python modulo-02-prompt-engineering/labs/03_function_calling_openai.py --dry-run
    python modulo-02-prompt-engineering/labs/03_function_calling_openai.py \
         "How much remains to be paid for FAC-2026-0042 and when is it due?"
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from decimal import Decimal
from typing import Any

from _common import OPENAI_MODEL, require_env
from rich.console import Console

INVOICES = {
    "FAC-2026-0042": {
        "status": "partial",
        "total_cents": 149900,
        "paid_cents": 50000,
        "due_date": "2026-09-15",
        "currency": "EUR",
    },
    "FAC-2026-0088": {
        "status": "paid",
        "total_cents": 42000,
        "paid_cents": 42000,
        "due_date": "2026-07-30",
        "currency": "EUR",
    },
}

TOOLS = [
    {
        "type": "function",
        "name": "get_invoice",
        "description": (
            "Recupera una factura existente por número. Úsala para consultar estado, total, "
            "importe pagado, moneda o vencimiento. Es de solo lectura."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "invoice_number": {
                    "type": "string",
                    "description": "Número exacto con formato FAC-YYYY-NNNN",
                    "pattern": "^FAC-[0-9]{4}-[0-9]{4}$",
                }
            },
            "required": ["invoice_number"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "calculate_outstanding",
        "description": (
            "Calcula importe pendiente a partir de total y pagado en céntimos. Úsala después "
            "de get_invoice cuando el usuario pregunte cuánto queda por pagar."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "total_cents": {"type": "integer", "description": "Importe total en céntimos"},
                "paid_cents": {"type": "integer", "description": "Importe ya pagado en céntimos"},
                "currency": {"type": "string", "enum": ["EUR", "USD"]},
            },
            "required": ["total_cents", "paid_cents", "currency"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]
console = Console()


def get_invoice(invoice_number: str) -> dict[str, Any]:
    invoice = INVOICES.get(invoice_number)
    if invoice is None:
        return {"ok": False, "error": "invoice_not_found", "invoice_number": invoice_number}
    return {"ok": True, "invoice_number": invoice_number, **invoice}


def calculate_outstanding(
    total_cents: int, paid_cents: int, currency: str
) -> dict[str, Any]:
    if total_cents < 0 or paid_cents < 0:
        return {"ok": False, "error": "amounts_must_be_non_negative"}
    if paid_cents > total_cents:
        return {"ok": False, "error": "paid_exceeds_total"}
    outstanding = Decimal(total_cents - paid_cents) / Decimal(100)
    return {
        "ok": True,
        "outstanding": format(outstanding, ".2f"),
        "currency": currency,
    }


TOOL_FUNCTIONS: dict[str, Callable[..., dict[str, Any]]] = {
    "get_invoice": get_invoice,
    "calculate_outstanding": calculate_outstanding,
}


def execute_tool(name: str, arguments_json: str) -> dict[str, Any]:
    function = TOOL_FUNCTIONS.get(name)
    if function is None:
        return {"ok": False, "error": "unknown_tool", "tool": name}
    try:
        arguments = json.loads(arguments_json)
    except json.JSONDecodeError as exc:
        return {"ok": False, "error": "invalid_json", "detail": str(exc)}
    try:
        return function(**arguments)
    except TypeError as exc:
        return {"ok": False, "error": "invalid_arguments", "detail": str(exc)}


def run_agent(client, question: str, max_iterations: int = 5) -> str:
    input_items: list[Any] = [{"role": "user", "content": question}]
    for iteration in range(1, max_iterations + 1):
        response = client.responses.create(
            model=OPENAI_MODEL,
            instructions=(
                "Ayuda con facturas usando las herramientas. No inventes datos. "
                "Importes monetarios se presentan con dos decimales."
            ),
            input=input_items,
            tools=TOOLS,
        )
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            console.print(f"[dim]Fin tras {iteration} iteración(es).[/dim]")
            return response.output_text

        input_items.extend(response.output)
        for call in calls:
            result = execute_tool(call.name, call.arguments)
            console.print(f"[cyan]tool[/cyan] {call.name}({call.arguments}) → {result}")
            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(result, ensure_ascii=False),
                }
            )
    raise RuntimeError(f"el agente superó {max_iterations} iteraciones")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "question",
        nargs="?",
        default="¿Cuánto queda por pagar de FAC-2026-0042 y cuándo vence?",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.dry_run:
        invoice = execute_tool("get_invoice", '{"invoice_number":"FAC-2026-0042"}')
        outstanding = execute_tool(
            "calculate_outstanding",
            '{"total_cents":149900,"paid_cents":50000,"currency":"EUR"}',
        )
        console.print_json(data={"invoice": invoice, "outstanding": outstanding})
        return 0

    require_env("OPENAI_API_KEY")
    from openai import OpenAI

    answer = run_agent(OpenAI(timeout=30.0, max_retries=2), args.question)
    console.print(f"\n[bold green]{answer}[/bold green]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
