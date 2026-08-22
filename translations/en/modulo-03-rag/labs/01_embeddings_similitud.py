"""Lab 01 — Semantic similarity with local embeddings.

Compares pairs, searches against the corpus, and demonstrates why similarity is not probability. The
--lexical mode uses TF-IDF without downloading a model and serves as a reproducible baseline.

Execution:
    python modulo-03-rag/labs/01_embeddings_similitud.py --lexical
    python modulo-03-rag/labs/01_embeddings_similitud.py
"""

from __future__ import annotations

import argparse

from _rag_common import (
    EmbeddingEncoder,
    SearchIndex,
    TfidfEncoder,
    heading_chunks,
    load_documents,
)
from rich.console import Console
from rich.table import Table

PAIRS = [
    ("He perdido el segundo factor", "No puedo acceder porque perdí mi aplicación TOTP"),
    ("La factura tiene IVA incorrecto", "Necesito corregir el impuesto del documento"),
    ("La API devuelve 429", "El dashboard permite crear colores personalizados"),
    ("¿Existe aplicación móvil?", "La interfaz web funciona en pantallas pequeñas"),
]
console = Console()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lexical", action="store_true")
    parser.add_argument("--query", default="¿Qué hago si pierdo el MFA y soy el único admin?")
    return parser.parse_args()


def pair_scores(lexical: bool) -> list[float]:
    texts = [text for pair in PAIRS for text in pair]
    encoder = TfidfEncoder(texts) if lexical else EmbeddingEncoder()
    vectors = encoder.encode(texts, kind="passage")
    return [float(vectors[index] @ vectors[index + 1]) for index in range(0, len(vectors), 2)]


def main() -> int:
    args = parse_args()
    scores = pair_scores(args.lexical)
    table = Table(title="Similitud coseno de pares")
    table.add_column("Texto A", max_width=38)
    table.add_column("Texto B", max_width=38)
    table.add_column("cos", justify="right")
    for pair, score in zip(PAIRS, scores, strict=True):
        table.add_row(pair[0], pair[1], f"{score:.3f}")
    console.print(table)

    chunks = heading_chunks(load_documents())
    index = SearchIndex(chunks, lexical=args.lexical)
    hits = index.search(args.query, top_k=5)
    result_table = Table(title=f"Top-5 para: {args.query}", show_lines=True)
    result_table.add_column("rank")
    result_table.add_column("chunk")
    result_table.add_column("score", justify="right")
    result_table.add_column("fragmento", max_width=70)
    for rank, hit in enumerate(hits, start=1):
        result_table.add_row(
            str(rank),
            hit.chunk.chunk_id,
            f"{hit.score:.3f}",
            hit.chunk.text[:240].replace("\n", " "),
        )
    console.print(result_table)
    console.print(
        "[dim]El coseno ordena candidatos dentro de este índice. No es una probabilidad ni "
        "comparte umbral universal con otro modelo/corpus.[/dim]"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
