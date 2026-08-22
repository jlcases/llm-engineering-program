"""Lab 01 — Primera llamada a OpenAI con Responses API.

Qué se aprende
--------------
- Anatomía de una llamada a Responses: modelo, instructions, input y límite de salida.
- Cómo leer la respuesta: output tipado, status y usage (tokens de entrada/salida).
- Por qué las instrucciones de desarrollador cambian el comportamiento sin tocar la pregunta.

Requisitos
----------
- Fichero .env en la raíz del repo con OPENAI_API_KEY=sk-...
- Dependencias del pyproject raíz (openai, python-dotenv, rich).

Ejecución
---------
    python modulo-01-fundamentos-llm/labs/01_primer_llamada_openai.py --dry-run
    python modulo-01-fundamentos-llm/labs/01_primer_llamada_openai.py

Modelo de desarrollo: gpt-5.6-luna (catálogo verificado en agosto de 2026).
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

# El .env vive en la raíz del repo (dos niveles por encima de labs/)
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
    """Aborta con un mensaje claro si falta la clave."""
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

    client = OpenAI()  # lee OPENAI_API_KEY del entorno automáticamente

    console.rule(f"[bold]Llamada a {MODEL}[/bold]")
    console.print(f"[dim]instructions:[/dim] {INSTRUCTIONS}")
    console.print(f"[dim]user:[/dim] {USER_PROMPT}\n")

    response = client.responses.create(**request)

    console.print(
        Panel(response.output_text, title="Respuesta del modelo", border_style="green")
    )

    # La metadata importa tanto como el texto: aquí está el coste y el motivo de parada
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
