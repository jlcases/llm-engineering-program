"""Lab 04 — Barrido de temperature y top_p sobre un mismo prompt.

Qué se aprende
--------------
- El efecto REAL de temperature: mismas instrucciones, distinta aleatoriedad.
  * T=0 → respuestas (casi) idénticas entre muestras.
  * T alta → diversidad creciente, hasta rozar la incoherencia.
- El efecto de top_p como truncador de la cola de la distribución.
- Por qué se recomienda ajustar temperature O top_p, no ambos a la vez.

Requisitos
----------
- Fichero .env en la raíz del repo con OPENAI_API_KEY=sk-...
- Dependencias del pyproject raíz (openai, python-dotenv, rich).

Ejecución
---------
    python modulo-01-fundamentos-llm/labs/04_parametros_generacion.py --dry-run
    python modulo-01-fundamentos-llm/labs/04_parametros_generacion.py

Coste: (4 temperatures × 3 muestras) + (3 top_p × 1) = 15 llamadas cortas a
`gpt-5.6-luna` por defecto. Calcula el importe con la tarifa vigente antes de ejecutar.
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

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
PROMPT = "Escribe una única frase que abra una novela de misterio ambientada en Valencia."
TEMPERATURES = [0.0, 0.4, 0.8, 1.2]
SAMPLES_PER_TEMP = 3
TOP_P_VALUES = [0.1, 0.5, 1.0]

console = Console()


def require_api_key() -> None:
    """Aborta con un mensaje claro si falta la clave."""
    if not os.getenv("OPENAI_API_KEY"):
        console.print(
            Panel(
                "No se encontró [bold]OPENAI_API_KEY[/bold].\n\n"
                f"Crea el fichero [cyan]{REPO_ROOT / '.env'}[/cyan] con la línea:\n"
                "  OPENAI_API_KEY=sk-...",
                title="Falta la clave de API",
                border_style="red",
            )
        )
        sys.exit(1)


def generate(client, temperature: float | None = None, top_p: float | None = None) -> str:
    """Una muestra corta con los parámetros indicados (solo uno debería variar)."""
    kwargs = {}
    if temperature is not None:
        kwargs["temperature"] = temperature
    if top_p is not None:
        kwargs["top_p"] = top_p
    response = client.responses.create(
        model=MODEL,
        input=PROMPT,
        reasoning={"effort": "none"},
        max_output_tokens=60,
        **kwargs,
    )
    if response.status == "incomplete" and not response.output_text:
        reason = getattr(response.incomplete_details, "reason", "desconocido")
        raise RuntimeError(f"respuesta incompleta sin texto: {reason}")
    return response.output_text.strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.dry_run:
        console.print_json(
            json.dumps(
                {
                    "model": MODEL,
                    "prompt": PROMPT,
                    "reasoning_effort": "none",
                    "temperature_sweep": TEMPERATURES,
                    "samples_per_temperature": SAMPLES_PER_TEMP,
                    "top_p_sweep": TOP_P_VALUES,
                    "planned_api_calls": len(TEMPERATURES) * SAMPLES_PER_TEMP
                    + len(TOP_P_VALUES),
                },
                ensure_ascii=False,
            )
        )
        return
    require_api_key()

    from openai import OpenAI

    client = OpenAI()

    console.rule("[bold]Barrido de temperature[/bold]")
    console.print(f'Prompt fijo: "{PROMPT}"')
    console.print(
        f"[dim]{SAMPLES_PER_TEMP} muestras por temperature; top_p sin tocar.[/dim]\n"
    )

    for temperature in TEMPERATURES:
        table = Table(
            title=f"temperature = {temperature}", show_header=False, expand=True
        )
        table.add_column("n", style="dim", width=3)
        table.add_column("Muestra")
        with console.status(f"Generando con T={temperature}..."):
            for i in range(SAMPLES_PER_TEMP):
                table.add_row(str(i + 1), generate(client, temperature=temperature))
        console.print(table)

    console.print(
        Panel(
            "Qué observar:\n"
            "• Con T=0 las tres muestras deberían ser casi idénticas (y bastante "
            "tópicas: es la respuesta modal).\n"
            "• Con T=0.8 hay variedad manteniendo coherencia.\n"
            "• Con T=1.2 aparecen giros más raros; en modelos sin truncado de cola "
            "esto ya descarrilaría más a menudo.",
            title="Lectura del experimento",
            border_style="blue",
        )
    )

    console.rule("[bold]Barrido de top_p (temperature sin tocar)[/bold]")
    table = Table(show_header=True, expand=True)
    table.add_column("top_p", width=8)
    table.add_column("Muestra")
    with console.status("Generando barrido de top_p..."):
        for top_p in TOP_P_VALUES:
            table.add_row(str(top_p), generate(client, top_p=top_p))
    console.print(table)

    console.print(
        Panel(
            "top_p=0.1 restringe el muestreo al núcleo mínimo de tokens que suma el "
            "10% de probabilidad: el efecto se parece a bajar la temperature, pero el "
            "mecanismo es distinto (truncar candidatos vs redistribuir probabilidad).\n\n"
            "Regla práctica: ajusta temperature O top_p, nunca los dos a la vez — si "
            "mueves ambos no sabrás a cuál atribuir el cambio.",
            title="Lectura del experimento",
            border_style="blue",
        )
    )


if __name__ == "__main__":
    main()
