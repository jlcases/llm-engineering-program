"""Lab 05 — Inferencia multi-modelo con Amazon Bedrock Converse API.

Aprendes a construir una petición Converse, invocarla o transmitirla por streaming, leer uso de
tokens y distinguir el cliente de runtime del cliente de control. El modo --dry-run no necesita
cuenta AWS y muestra exactamente el payload sin enviarlo.

Requisitos para una llamada real:
    AWS_REGION=eu-west-1
    BEDROCK_MODEL_ID=<modelo o inference profile habilitado en esa región>

Autenticación: perfil local, AWS SSO, variables temporales o rol. No pongas credenciales en código.

Ejecución:
    python modulo-01-fundamentos-llm/labs/05_bedrock_inference.py --dry-run
    python modulo-01-fundamentos-llm/labs/05_bedrock_inference.py
    python modulo-01-fundamentos-llm/labs/05_bedrock_inference.py --stream
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

DEFAULT_PROMPT = (
    "Explica en tres frases la diferencia entre Amazon Bedrock y un endpoint de SageMaker."
)
SYSTEM_PROMPT = (
    "Eres un profesor de ingeniería de LLMs. Responde en español, con precisión, "
    "sin inventar servicios ni precios."
)
console = Console()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--model", default=os.getenv("BEDROCK_MODEL_ID"))
    parser.add_argument("--region", default=os.getenv("AWS_REGION", "eu-west-1"))
    parser.add_argument("--profile", default=os.getenv("AWS_PROFILE"))
    parser.add_argument("--max-tokens", type=int, default=300)
    parser.add_argument("--stream", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def build_request(args: argparse.Namespace) -> dict[str, Any]:
    model_id = args.model or "<configura BEDROCK_MODEL_ID>"
    return {
        "modelId": model_id,
        "system": [{"text": SYSTEM_PROMPT}],
        "messages": [{"role": "user", "content": [{"text": args.prompt}]}],
        "inferenceConfig": {
            "maxTokens": args.max_tokens,
            "temperature": 0.2,
            "topP": 0.9,
        },
    }


def make_runtime(args: argparse.Namespace):
    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    return session.client("bedrock-runtime")


def render_metadata(
    *,
    model_id: str,
    elapsed_ms: float,
    stop_reason: str | None,
    usage: dict[str, Any] | None,
    latency_ms: int | None,
) -> None:
    usage = usage or {}
    table = Table(title="Metadata de Bedrock")
    table.add_column("Campo", style="cyan")
    table.add_column("Valor")
    table.add_row("modelId", model_id)
    table.add_row("stopReason", stop_reason or "no informado")
    table.add_row("inputTokens", str(usage.get("inputTokens", "no informado")))
    table.add_row("outputTokens", str(usage.get("outputTokens", "no informado")))
    table.add_row("totalTokens", str(usage.get("totalTokens", "no informado")))
    table.add_row("latencia cliente", f"{elapsed_ms:.0f} ms")
    table.add_row("latencia servicio", f"{latency_ms} ms" if latency_ms else "no informada")
    console.print(table)


def invoke_once(runtime: Any, request: dict[str, Any]) -> None:
    started = time.perf_counter()
    response = runtime.converse(**request)
    elapsed_ms = (time.perf_counter() - started) * 1000

    content = response["output"]["message"]["content"]
    text = "".join(block["text"] for block in content if "text" in block)
    console.print(Panel(text, title="Respuesta", border_style="green"))
    render_metadata(
        model_id=request["modelId"],
        elapsed_ms=elapsed_ms,
        stop_reason=response.get("stopReason"),
        usage=response.get("usage"),
        latency_ms=response.get("metrics", {}).get("latencyMs"),
    )


def invoke_stream(runtime: Any, request: dict[str, Any]) -> None:
    started = time.perf_counter()
    response = runtime.converse_stream(**request)
    stop_reason: str | None = None
    usage: dict[str, Any] | None = None
    latency_ms: int | None = None

    console.rule("[bold]Respuesta en streaming[/bold]")
    for event in response["stream"]:
        if "contentBlockDelta" in event:
            delta = event["contentBlockDelta"].get("delta", {})
            if "text" in delta:
                console.print(delta["text"], end="")
        elif "messageStop" in event:
            stop_reason = event["messageStop"].get("stopReason")
        elif "metadata" in event:
            usage = event["metadata"].get("usage")
            latency_ms = event["metadata"].get("metrics", {}).get("latencyMs")
    console.print()
    render_metadata(
        model_id=request["modelId"],
        elapsed_ms=(time.perf_counter() - started) * 1000,
        stop_reason=stop_reason,
        usage=usage,
        latency_ms=latency_ms,
    )


def explain_client_error(exc: ClientError) -> str:
    error = exc.response.get("Error", {})
    code = error.get("Code", type(exc).__name__)
    message = error.get("Message", str(exc))
    hints = {
        "AccessDeniedException": (
            "Comprueba acceso al modelo, rol IAM, región e inference profile."
        ),
        "ValidationException": (
            "Comprueba model ID, región, parámetros y compatibilidad con Converse."
        ),
        "ThrottlingException": "Has alcanzado una cuota; aplica backoff y revisa Service Quotas.",
    }
    return f"{code}: {message}\n{hints.get(code, 'Consulta el código y Request ID en CloudTrail/logs.')}"


def main() -> int:
    args = parse_args()
    request = build_request(args)

    if args.dry_run:
        console.print_json(json.dumps(request, ensure_ascii=False))
        console.print(
            "[yellow]Dry-run:[/yellow] no se creó cliente ni se envió ninguna petición."
        )
        return 0
    if not args.model:
        console.print(
            Panel(
                "Configura BEDROCK_MODEL_ID o pasa --model. Usa un model ID o inference "
                "profile disponible y habilitado en la región elegida.",
                title="Falta el modelo",
                border_style="red",
            )
        )
        return 2

    try:
        runtime = make_runtime(args)
        if args.stream:
            invoke_stream(runtime, request)
        else:
            invoke_once(runtime, request)
    except NoCredentialsError:
        console.print("[red]AWS no encontró credenciales válidas.[/red]")
        return 3
    except ClientError as exc:
        console.print(Panel(explain_client_error(exc), title="Error de Bedrock", border_style="red"))
        return 4
    except BotoCoreError as exc:
        console.print(f"[red]Error del SDK de AWS:[/red] {exc}")
        return 5
    return 0


if __name__ == "__main__":
    sys.exit(main())
