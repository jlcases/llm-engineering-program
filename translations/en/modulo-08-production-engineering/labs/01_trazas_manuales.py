"""Lab 01 — Manual JSONL traces without framework or sensitive data.

Instrument a request with nested spans, latency, tokens, model, status, and error. Prompts and
responses are not saved: only length and hash are preserved for correlation. The result shows
what contract any observability platform must provide.

Execution:
    python modulo-08-production-engineering/labs/01_trazas_manuales.py
    python modulo-08-production-engineering/labs/01_trazas_manuales.py --output outputs/manual-trace.jsonl
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from rich.console import Console
from rich.table import Table

console = Console()


@dataclass
class Span:
    trace_id: str
    span_id: str
    parent_id: str | None
    name: str
    kind: str
    started_at: str
    duration_ms: float = 0.0
    status: str = "running"
    attributes: dict = field(default_factory=dict)
    error: dict | None = None


class TraceCollector:
    def __init__(self, output: Path | None = None) -> None:
        self.trace_id = uuid4().hex
        self.output = output
        self.spans: list[Span] = []

    @contextmanager
    def span(
        self,
        name: str,
        *,
        kind: str,
        parent_id: str | None = None,
        attributes: dict | None = None,
    ) -> Iterator[Span]:
        span = Span(
            trace_id=self.trace_id,
            span_id=uuid4().hex[:16],
            parent_id=parent_id,
            name=name,
            kind=kind,
            started_at=datetime.now(UTC).isoformat(),
            attributes=attributes or {},
        )
        started = time.perf_counter()
        try:
            yield span
        except Exception as exc:
            span.status = "error"
            span.error = {"type": type(exc).__name__, "message": str(exc)[:300]}
            raise
        else:
            span.status = "ok"
        finally:
            span.duration_ms = round((time.perf_counter() - started) * 1_000, 3)
            self.spans.append(span)
            if self.output:
                self.output.parent.mkdir(parents=True, exist_ok=True)
                with self.output.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(asdict(span), ensure_ascii=False) + "\n")


def fingerprint(text: str) -> dict[str, str | int]:
    return {
        "characters": len(text),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }


def simulated_retrieval(question: str) -> list[str]:
    time.sleep(0.01)
    return ["policy: las credenciales expuestas se revocan antes de rotarlas"]


def simulated_llm(question: str, contexts: list[str]) -> tuple[str, dict[str, int]]:
    time.sleep(0.02)
    return (
        "Revoca primero la credencial expuesta y después crea otra con permisos mínimos.",
        {"input_tokens": 52, "output_tokens": 17},
    )


def run_pipeline(question: str, collector: TraceCollector) -> str:
    with collector.span(
        "answer_request",
        kind="chain",
        attributes={"input": fingerprint(question), "tenant": "training"},
    ) as root:
        with collector.span(
            "retrieve",
            kind="retriever",
            parent_id=root.span_id,
            attributes={"top_k": 4},
        ) as retrieval_span:
            contexts = simulated_retrieval(question)
            retrieval_span.attributes["documents"] = len(contexts)
        with collector.span(
            "generate",
            kind="llm",
            parent_id=root.span_id,
            attributes={"model": "gpt-5.6-luna", "provider": "simulated"},
        ) as llm_span:
            answer, usage = simulated_llm(question, contexts)
            llm_span.attributes.update(usage)
            llm_span.attributes["output"] = fingerprint(answer)
        root.attributes["result"] = "answered"
        return answer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "question",
        nargs="?",
        default="He expuesto una clave API, ¿qué hago primero?",
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    collector = TraceCollector(args.output)
    answer = run_pipeline(args.question, collector)
    table = Table(title=f"Trace {collector.trace_id}")
    table.add_column("span")
    table.add_column("kind")
    table.add_column("status")
    table.add_column("ms", justify="right")
    table.add_column("parent")
    for span in collector.spans:
        table.add_row(span.name, span.kind, span.status, f"{span.duration_ms:.1f}", span.parent_id or "root")
    console.print(table)
    console.print(f"[bold green]Respuesta simulada:[/bold green] {answer}")
    if args.output:
        console.print(f"JSONL: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
