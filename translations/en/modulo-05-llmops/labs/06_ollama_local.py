"""Lab 06 — Local discovery and inference with the native Ollama API.

Do not hardcode a model that will expire: use ``--model``, OLLAMA_MODEL, or the first installed model returned by `/api/tags`. Report load latency, evaluation, generation, and tokens/second.

Execution:
    ollama serve
    python modulo-05-llmops/labs/06_ollama_local.py --list
    python modulo-05-llmops/labs/06_ollama_local.py --model <installed-tag>
"""

from __future__ import annotations

import argparse
import os
from typing import Any

import httpx
from rich.console import Console
from rich.table import Table

console = Console()


def list_models(client: httpx.Client) -> list[dict[str, Any]]:
    response = client.get("/api/tags")
    response.raise_for_status()
    return response.json().get("models", [])


def choose_model(models: list[dict[str, Any]], requested: str | None) -> str:
    names = [model["name"] for model in models]
    if requested:
        if requested not in names:
            raise ValueError(f"modelo '{requested}' no instalado; disponibles: {names}")
        return requested
    if not names:
        raise ValueError(
            "no hay modelos instalados; elige uno actual en https://ollama.com/library, "
            "ejecuta 'ollama pull <tag>' y pásalo con --model"
        )
    return names[0]


def chat(client: httpx.Client, model: str, prompt: str) -> dict[str, Any]:
    response = client.post(
        "/api/chat",
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": "Responde en español en un máximo de cuatro frases."},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {"temperature": 0.2},
        },
    )
    response.raise_for_status()
    return response.json()


def nanoseconds_to_ms(value: float | None) -> float:
    return float(value or 0) / 1_000_000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt", nargs="?", default="Explica qué es continuous batching.")
    parser.add_argument("--base-url", default=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"))
    parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL"))
    parser.add_argument("--list", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        with httpx.Client(base_url=args.base_url, timeout=120.0) as client:
            models = list_models(client)
            if args.list:
                table = Table(title="Modelos instalados en Ollama")
                table.add_column("tag")
                table.add_column("bytes", justify="right")
                table.add_column("modified")
                for model in models:
                    table.add_row(model["name"], str(model.get("size", "?")), model.get("modified_at", "?"))
                console.print(table)
                return 0
            model = choose_model(models, args.model)
            result = chat(client, model, args.prompt)
    except httpx.ConnectError:
        console.print(f"[red]Ollama no responde en {args.base_url}. Ejecuta 'ollama serve'.[/red]")
        return 2
    except (httpx.HTTPStatusError, ValueError) as exc:
        console.print(f"[red]{type(exc).__name__}:[/red] {exc}")
        return 3

    eval_count = int(result.get("eval_count", 0))
    eval_seconds = float(result.get("eval_duration", 0)) / 1_000_000_000
    tokens_per_second = eval_count / eval_seconds if eval_seconds else 0.0
    console.print(result.get("message", {}).get("content", ""))
    table = Table(title=f"Métricas · {model}")
    table.add_column("total ms")
    table.add_column("load ms")
    table.add_column("prompt tokens")
    table.add_column("output tokens")
    table.add_column("tok/s")
    table.add_row(
        f"{nanoseconds_to_ms(result.get('total_duration')):.1f}",
        f"{nanoseconds_to_ms(result.get('load_duration')):.1f}",
        str(result.get("prompt_eval_count", 0)),
        str(eval_count),
        f"{tokens_per_second:.1f}",
    )
    console.print(table)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
