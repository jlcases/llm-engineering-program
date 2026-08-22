"""Lab 02 — First Call to the Anthropic API (Claude).

What You Will Learn
--------------------
- The Anthropic Messages API and its differences from OpenAI:
   * `system` is a separate parameter, not just another message.
   * `max_tokens` is REQUIRED.
   * The response content is a list of typed blocks.
   * The stopping reason is called `stop_reason` (not `finish_reason`).
- Count tokens without spending: the `count_tokens` endpoint.

Requirements
------------
- `.env` file in the repo root containing `ANTHROPIC_API_KEY=sk-ant-...`
- Root `pyproject` dependencies (`anthropic`, `python-dotenv`, `rich`).

Execution
---------
    python modulo-01-fundamentos-llm/labs/02_primer_llamada_anthropic.py --dry-run
    python modulo-01-fundamentos-llm/labs/02_primer_llamada_anthropic.py

Development model: claude-haiku-4-5 (catalog verified as of August 2026)."""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5")
SYSTEM_PROMPT = (
    "Eres un profesor de ingeniería de LLMs. Respondes en español, "
    "con rigor pero en un máximo de 4 frases."
)
MESSAGES = [
    {
        "role": "user",
        "content": "Explícame qué es la ventana de contexto y qué pasa si la supero.",
    }
]

console = Console()


def require_api_key() -> None:
    """Aborts with a clear message if the key is missing."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        console.print(
            Panel(
                "No se encontró [bold]ANTHROPIC_API_KEY[/bold].\n\n"
                f"Crea el fichero [cyan]{REPO_ROOT / '.env'}[/cyan] con la línea:\n"
                "  ANTHROPIC_API_KEY=sk-ant-...\n\n"
                "La clave se obtiene en https://console.anthropic.com/settings/keys",
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
        "max_tokens": 300,
        "system": SYSTEM_PROMPT,
        "messages": MESSAGES,
        "temperature": 0.3,
    }
    if args.dry_run:
        console.print_json(json.dumps(request, ensure_ascii=False))
        return
    require_api_key()

    from anthropic import Anthropic

    client = Anthropic()  # reads ANTHROPIC_API_KEY from the environment

    # Before making the call: count tokens for free using the count_tokens endpoint
    count = client.messages.count_tokens(
        model=MODEL, system=SYSTEM_PROMPT, messages=MESSAGES
    )
    console.rule(f"[bold]Llamada a {MODEL}[/bold]")
    console.print(
        f"[dim]Tokens de entrada según count_tokens (sin coste): "
        f"{count.input_tokens}[/dim]\n"
    )

    response = client.messages.create(**request)

    # response.content is a LIST of blocks; the text is in the blocks with type="text"
    text = "".join(block.text for block in response.content if block.type == "text")
    console.print(Panel(text, title="Respuesta del modelo", border_style="green"))

    table = Table(title="Metadata de la respuesta")
    table.add_column("Campo", style="cyan")
    table.add_column("Valor")
    table.add_row("model", response.model)
    table.add_row("stop_reason", str(response.stop_reason))
    table.add_row("input_tokens", str(response.usage.input_tokens))
    table.add_row("output_tokens", str(response.usage.output_tokens))
    console.print(table)

    if response.stop_reason == "max_tokens":
        console.print(
            "[yellow]Aviso:[/yellow] respuesta truncada por max_tokens — "
            "el equivalente al finish_reason == 'length' de OpenAI."
        )

    console.print(
        "\n[dim]Compara la estructura de esta respuesta con la del lab 01: "
        "misma idea (mensajes con roles), detalles distintos en cada API.[/dim]"
    )


if __name__ == "__main__":
    main()
