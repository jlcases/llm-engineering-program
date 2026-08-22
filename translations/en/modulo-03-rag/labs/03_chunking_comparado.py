"""Lab 03 — Compare chunking with a retrieval metric.

Evaluate fixed-window, paragraphs, and sections on the same questions. Report doc recall@k, MRR, and
size distribution. --lexical makes the experiment fast and offline.

Execution:
    python modulo-03-rag/labs/03_chunking_comparado.py --lexical
    python modulo-03-rag/labs/03_chunking_comparado.py --limit 20
"""

from __future__ import annotations

import argparse
import json
import statistics

from _rag_common import (
    DATA_DIR,
    SearchIndex,
    fixed_word_chunks,
    heading_chunks,
    load_documents,
    paragraph_chunks,
)
from rich.console import Console
from rich.table import Table

console = Console()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--lexical", action="store_true")
    return parser.parse_args()


def evaluate(chunks, cases: list[dict], *, top_k: int, lexical: bool) -> dict[str, float]:
    index = SearchIndex(chunks, lexical=lexical)
    recalls = []
    reciprocal_ranks = []
    for case in cases:
        hits = index.search(case["question"], top_k=top_k)
        expected = set(case["relevant_doc_ids"])
        retrieved = [hit.chunk.doc_id for hit in hits]
        recalls.append(len(expected & set(retrieved)) / len(expected))
        first = next((rank for rank, doc_id in enumerate(retrieved, start=1) if doc_id in expected), None)
        reciprocal_ranks.append(1 / first if first else 0.0)
    sizes = [len(chunk.text.split()) for chunk in chunks]
    return {
        "chunks": float(len(chunks)),
        "words_p50": statistics.median(sizes),
        "words_p95": sorted(sizes)[min(len(sizes) - 1, int(0.95 * len(sizes)))],
        "doc_recall_at_k": statistics.mean(recalls),
        "mrr_at_k": statistics.mean(reciprocal_ranks),
    }


def main() -> int:
    args = parse_args()
    documents = load_documents()
    with (DATA_DIR / "eval_dataset.json").open(encoding="utf-8") as handle:
        cases = json.load(handle)[: args.limit]
    strategies = {
        "fixed 140/30": fixed_word_chunks(documents, size=140, overlap=30),
        "paragraph": paragraph_chunks(documents, max_words=180),
        "heading": heading_chunks(documents, max_words=220),
    }

    table = Table(title=f"Chunking comparado · k={args.top_k} · casos={len(cases)}")
    table.add_column("estrategia")
    table.add_column("chunks", justify="right")
    table.add_column("words p50/p95", justify="right")
    table.add_column("doc recall@k", justify="right")
    table.add_column("MRR@k", justify="right")
    for name, chunks in strategies.items():
        metrics = evaluate(chunks, cases, top_k=args.top_k, lexical=args.lexical)
        table.add_row(
            name,
            str(int(metrics["chunks"])),
            f"{metrics['words_p50']:.0f}/{metrics['words_p95']:.0f}",
            f"{metrics['doc_recall_at_k']:.1%}",
            f"{metrics['mrr_at_k']:.3f}",
        )
    console.print(table)
    console.print(
        "[dim]Doc recall es una señal gruesa: un chunk del documento correcto puede no contener "
        "la frase necesaria. El siguiente paso es anotar relevancia a nivel de chunk.[/dim]"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
