"""Lab 03 — Tokenización comparada con tiktoken.

Qué se aprende
--------------
- Cómo trocea un BPE textos reales: ver los tokens uno a uno.
- Comparar dos vocabularios de OpenAI: cl100k_base (GPT-4) vs o200k_base (GPT-4o):
  un vocabulario mayor comprime más, sobre todo fuera del inglés.
- Medir la "tasa de cambio" caracteres/token por idioma y tipo de texto,
  y entender el impacto en coste y ventana de contexto.
- Rarezas: espacios, mayúsculas, números y emojis.

Requisitos
----------
- NO necesita claves de API: tiktoken tokeniza en local.
- Dependencias del pyproject raíz (tiktoken, rich).

Ejecución
---------
    python modulo-01-fundamentos-llm/labs/03_tokenizacion_comparada.py
"""

import tiktoken
from rich.console import Console
from rich.table import Table

console = Console()

ENCODINGS = {
    "cl100k_base": "GPT-3.5 / GPT-4",
    "o200k_base": "GPT-4o / o-series",
}

# Textos de prueba: mismo contenido en dos idiomas + código + casos raros
SAMPLES = {
    "Español": (
        "La tokenización determina cuánto cuesta cada llamada y cuánto texto "
        "cabe en la ventana de contexto del modelo."
    ),
    "Inglés (traducción)": (
        "Tokenization determines how much each call costs and how much text "
        "fits in the model's context window."
    ),
    "Código Python": (
        "def factorial(n: int) -> int:\n"
        "    return 1 if n <= 1 else n * factorial(n - 1)"
    ),
    "Números": "El resultado es 1234567890 y el IBAN tiene 24 dígitos.",
    "Emojis y raro": "Paella 🥘 + debugging 🐛 = viernes típico. Café ☕×3.",
}


def show_token_breakdown(text: str, encoding_name: str) -> None:
    """Imprime cada token individual entre barras para ver los cortes."""
    enc = tiktoken.get_encoding(encoding_name)
    ids = enc.encode(text)
    # Cada id se decodifica por separado para visualizar el troceado exacto
    pieces = [enc.decode([token_id]) for token_id in ids]
    rendered = "|".join(piece.replace("\n", "\\n") for piece in pieces)
    console.print(f"[dim]{encoding_name} ({len(ids)} tokens):[/dim]")
    console.print(f"  [green]{rendered}[/green]\n")


def main() -> None:
    console.rule("[bold]1. Ver los cortes de un tokenizador[/bold]")
    demo = "El murciélago hipotecario desayuna transformers."
    console.print(f'Texto: "{demo}"\n')
    for encoding_name in ENCODINGS:
        show_token_breakdown(demo, encoding_name)
    console.print(
        "[dim]Fíjate: las palabras raras se parten en trozos, y el espacio inicial "
        "forma parte del token siguiente.[/dim]\n"
    )

    console.rule("[bold]2. Comparativa cl100k_base vs o200k_base[/bold]")
    table = Table(title="Tokens por texto y encoding (menos = más barato)")
    table.add_column("Texto", style="cyan", max_width=24)
    table.add_column("Caracteres", justify="right")
    for encoding_name, models in ENCODINGS.items():
        table.add_column(f"{encoding_name}\n({models})", justify="right")
    table.add_column("Ahorro o200k", justify="right", style="green")

    for label, text in SAMPLES.items():
        counts = {
            name: len(tiktoken.get_encoding(name).encode(text)) for name in ENCODINGS
        }
        saving = 1 - counts["o200k_base"] / counts["cl100k_base"]
        table.add_row(
            label,
            str(len(text)),
            str(counts["cl100k_base"]),
            str(counts["o200k_base"]),
            f"{saving:+.0%}",
        )
    console.print(table)

    console.rule("[bold]3. Caracteres por token (eficiencia por idioma)[/bold]")
    ratio_table = Table(title="chars/token — cuanto más alto, más comprime")
    ratio_table.add_column("Texto", style="cyan", max_width=24)
    for name in ENCODINGS:
        ratio_table.add_column(name, justify="right")
    for label, text in SAMPLES.items():
        row = [label]
        for name in ENCODINGS:
            n_tokens = len(tiktoken.get_encoding(name).encode(text))
            row.append(f"{len(text) / n_tokens:.2f}")
        ratio_table.add_row(*row)
    console.print(ratio_table)

    console.rule("[bold]4. Rarezas que explican bugs famosos[/bold]")
    enc = tiktoken.get_encoding("o200k_base")
    for text in ["hola", " hola", "Hola", "strawberry", "12345678"]:
        ids = enc.encode(text)
        pieces = [enc.decode([t]) for t in ids]
        console.print(
            f'  "{text}" → {len(ids)} token(s): {pieces}'
        )
    console.print(
        "\n[dim]Conclusiones: 'hola', ' hola' y 'Hola' son tokens distintos; "
        "'strawberry' es 1-2 tokens opacos (por eso contar sus erres es difícil); "
        "los números se trocean en grupos de dígitos.[/dim]"
    )

    console.print(
        "\n[bold]Recuerda:[/bold] tiktoken solo es exacto para modelos de OpenAI. "
        "Para Claude usa client.messages.count_tokens (lab 02); para otros, "
        "el tokenizador oficial de cada proveedor."
    )


if __name__ == "__main__":
    main()
