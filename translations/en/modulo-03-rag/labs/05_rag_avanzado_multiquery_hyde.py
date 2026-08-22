"""Lab 05 — Advanced RAG with multi-query, HyDE, and Reciprocal Rank Fusion.

``--offline`` produces deterministic expansions to study and test fusion without an
API. Without this flag, OpenAI generates three reformulations and a structured hypothetical document.

Execution:
    python modulo-03-rag/labs/05_rag_avanzado_multiquery_hyde.py --offline --lexical
    python modulo-03-rag/labs/05_rag_avanzado_multiquery_hyde.py "question" --lexical
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Literal

from _rag_common import (
    SearchHit,
    SearchIndex,
    heading_chunks,
    load_documents,
    reciprocal_rank_fusion,
    tokenize,
)
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
console = Console()


class QueryExpansion(BaseModel):
    queries: list[str] = Field(min_length=3, max_length=3)
    hypothetical_document: str = Field(min_length=40, max_length=900)
    method: Literal["multi_query_hyde"] = "multi_query_hyde"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "question",
        nargs="?",
        default="Perdí el segundo factor y no hay otro administrador, ¿cómo recupero la cuenta?",
    )
    parser.add_argument("--top-k-per-query", type=int, default=6)
    parser.add_argument("--final-k", type=int, default=5)
    parser.add_argument("--lexical", action="store_true")
    parser.add_argument("--offline", action="store_true")
    return parser.parse_args()


def offline_expansion(question: str) -> QueryExpansion:
    terms = " ".join(dict.fromkeys(tokenize(question)))
    return QueryExpansion(
        queries=[
            question,
            f"procedimiento oficial requisitos pasos {terms}",
            f"excepciones seguridad recuperación administrador {terms}",
        ],
        hypothetical_document=(
            "La documentación operativa describe el procedimiento aplicable, los requisitos de "
            "verificación, el orden de los pasos y las excepciones de seguridad para recuperar "
            f"acceso. Conceptos de la consulta: {terms}."
        ),
    )


def live_expansion(question: str) -> QueryExpansion:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("falta OPENAI_API_KEY; usa --offline para el recorrido local")
    from openai import OpenAI

    response = OpenAI(timeout=30.0, max_retries=2).responses.parse(
        model=MODEL,
        instructions=(
            "Expande consultas para buscar documentación interna. Devuelve exactamente tres "
            "consultas: original, paráfrasis y variante con vocabulario técnico. El documento "
            "hipotético debe parecer un pasaje que respondería la pregunta, sin inventar cifras, "
            "nombres propios ni decisiones concretas."
        ),
        input=question,
        text_format=QueryExpansion,
        max_output_tokens=700,
    )
    if response.output_parsed is None:
        raise RuntimeError("el modelo no devolvió una expansión estructurada")
    return response.output_parsed


def retrieve_fused(
    index: SearchIndex,
    expansion: QueryExpansion,
    *,
    top_k_per_query: int,
) -> tuple[list[SearchHit], list[list[SearchHit]]]:
    result_sets = [
        index.search(query, top_k=top_k_per_query) for query in expansion.queries
    ]
    result_sets.append(
        index.search(expansion.hypothetical_document, top_k=top_k_per_query)
    )
    return reciprocal_rank_fusion(result_sets), result_sets


def main() -> int:
    args = parse_args()
    if args.top_k_per_query <= 0 or args.final_k <= 0:
        raise ValueError("los valores de k deben ser > 0")
    expansion = (
        offline_expansion(args.question)
        if args.offline
        else live_expansion(args.question)
    )
    index = SearchIndex(heading_chunks(load_documents()), lexical=args.lexical)
    baseline = index.search(args.question, top_k=args.final_k)
    fused, result_sets = retrieve_fused(
        index,
        expansion,
        top_k_per_query=args.top_k_per_query,
    )

    console.print(Panel("\n".join(f"• {query}" for query in expansion.queries), title="Multi-query"))
    console.print(Panel(expansion.hypothetical_document, title="HyDE"))
    table = Table(title="Baseline frente a RRF")
    table.add_column("rank")
    table.add_column("baseline")
    table.add_column("RRF")
    table.add_column("apariciones", justify="right")
    for rank in range(args.final_k):
        baseline_id = baseline[rank].chunk.chunk_id if rank < len(baseline) else "—"
        fused_id = fused[rank].chunk.chunk_id if rank < len(fused) else "—"
        appearances = (
            sum(
                any(hit.chunk.chunk_id == fused_id for hit in result_set)
                for result_set in result_sets
            )
            if fused_id != "—"
            else 0
        )
        table.add_row(str(rank + 1), baseline_id, fused_id, str(appearances))
    console.print(table)
    console.print(
        "[dim]RRF usa rangos, no scores incompatibles. HyDE mejora algunas consultas ambiguas, "
        "pero puede arrastrar el retrieval si su hipótesis introduce conceptos falsos.[/dim]"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
