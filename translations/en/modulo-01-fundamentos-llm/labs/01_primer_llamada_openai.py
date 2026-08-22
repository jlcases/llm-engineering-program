"""Lab 01 — First OpenAI Call with the Responses API.

What You Will Learn
-------------------
- Anatomy of a Responses call: model, instructions, input, and output limit.
- How to read the response: typed output, status, and usage (input/output tokens).
- Why developer instructions change behavior without altering the prompt.

Requirements
------------
- .env file in the repo root containing OPENAI_API_KEY=sk-...
- Dependencies from the root pyproject (openai, python-dotenv, rich).

Execution
---------
    python modulo-01-fundamentos-llm/labs/01_primer_llamada_openai.py --dry-run
    python modulo-01-fundamentos-llm/labs/01_primer_llamada_openai.py

Development model: gpt-5.6-luna (catalog verified in August 2026).
"""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# .env file is located in the repo root (two levels above labs/)
REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
INSTRUCTIONS = (
    "Eres un profesor de ingeniería de LLMs. Respondes en español, "
    "con rigor pero en un máximo de 4 frases."
)
USER_PROMPT = "Explícame qué es un token y por qué las APIs cobran por tokens."

console = Console()


def require_api_key() -> None:
    """Exits with a clear message if the key is missing."""
    if not os.getenv("OPENAI_API_KEY"):
        console.print(
            Panel(
                "No se encontró [bold]OPENAI_API_KEY[/bold].\n\n"
                f"Crea el fichero [cyan]{REPO_ROOT / '.env'}[/cyan] con la línea:\n"
                "  OPENAI_API_KEY=sk-...\n\n"
                "La clave se obtiene en https://platform.openai.com/api-keys",
                title="Falta la clave de API",
                border_style="red",
            )
        )
        sys.exit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    request = {
        "model": MODEL,
        "instructions": INSTRUCTIONS,
        "input": USER_PROMPT,
        "reasoning": {"effort": "none"},
        "max_output_tokens": 300,
    }
    if args.dry_run:
        console.print_json(json.dumps(request, ensure_ascii=False))
        return
    require_api_key()

    from openai import OpenAI

    client = OpenAI()  # reads OPENAI_API_KEY from the environment automatically

    console.rule(f"[bold]Llamada a {MODEL}[/bold]")
    console.print(f"[dim]instructions:[/dim] {INSTRUCTIONS}")
    console.print(f"[dim]user:[/dim] {USER_PROMPT}\n")

    response = client.responses.create(**request)

    console.print(
        Panel(response.output_text, title="Respuesta del modelo", border_style="green")
    )

    # Metadata is as important as the text: here you can find the cost and the stop reason.
    usage = response.usage
    table = Table(title="Metadata de la respuesta")
    table.add_column("Campo", style="cyan")
    table.add_column("Valor")
    table.add_row("model (real)", response.model)
    table.add_row("status", response.status)
    table.add_row("input_tokens", str(usage.input_tokens))
    table.add_row("output_tokens", str(usage.output_tokens))
    table.add_row("total_tokens", str(usage.total_tokens))
    console.print(table)

    if response.status == "incomplete":
        reason = getattr(response.incomplete_details, "reason", "no informado")
        console.print(
            f"[yellow]Aviso:[/yellow] respuesta incompleta ({reason}). En producción "
            "hay que tratar este estado siempre."
        )

    console.print(
        "\n[dim]Prueba a cambiar el system prompt (p. ej. 'responde como un pirata') "
        "y vuelve a ejecutar. El lab 04 aísla los parámetros de muestreo.[/dim]"
    )


if __name__ == "__main__":
    main()
