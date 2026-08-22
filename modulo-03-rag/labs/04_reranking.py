"""Lab 04 — Recuperación en dos etapas: candidatos baratos y reranking preciso.

El modo normal usa embeddings para recuperar y un cross-encoder multilingüe para reordenar.
``--lexical`` evita descargas: TF-IDF recupera y una función determinista basada en cobertura,
título y densidad reordena. Ese modo es un smoke test, no un sustituto del cross-encoder.

Ejecución:
    python modulo-03-rag/labs/04_reranking.py --lexical
    python modulo-03-rag/labs/04_reranking.py --limit 20
"""

from __future__ import annotations

import argparse
import json
import statistics
from dataclasses import dataclass

from _rag_common import (
    DATA_DIR,
    SearchHit,
    SearchIndex,
    heading_chunks,
    load_documents,
    tokenize,
)
from rich.console import Console
from rich.table import Table

DEFAULT_RERANKER = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
console = Console()


@dataclass(frozen=True)
class RankedHit:
    hit: SearchHit
    rerank_score: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "question",
        nargs="?",
        default="¿Qué debo hacer primero si se filtra una clave API?",
    )
    parser.add_argument("--candidate-k", type=int, default=10)
    parser.add_argument("--final-k", type=int, default=4)
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--lexical", action="store_true")
    parser.add_argument("--model", default=DEFAULT_RERANKER)
    return parser.parse_args()


def lexical_rerank(question: str, hits: list[SearchHit]) -> list[RankedHit]:
    """Fallback explicable para CI: cobertura de términos y prioridad del título."""
    query_terms = set(tokenize(question))
    ranked = []
    for hit in hits:
        body_terms = tokenize(hit.chunk.text)
        title_terms = set(tokenize(hit.chunk.title))
        overlap = query_terms & set(body_terms)
        coverage = len(overlap) / max(1, len(query_terms))
        density = sum(term in overlap for term in body_terms) / max(1, len(body_terms))
        title_bonus = len(query_terms & title_terms) / max(1, len(query_terms))
        score = 0.65 * coverage + 0.20 * title_bonus + 0.10 * density + 0.05 * hit.score
        ranked.append(RankedHit(hit=hit, rerank_score=score))
    return sorted(ranked, key=lambda item: item.rerank_score, reverse=True)


class CrossEncoderReranker:
    def __init__(self, model_name: str) -> None:
        from sentence_transformers import CrossEncoder

        self.model = CrossEncoder(model_name)

    def rerank(self, question: str, hits: list[SearchHit]) -> list[RankedHit]:
        pairs = [
            (question, f"{hit.chunk.title}\n{hit.chunk.text}")
            for hit in hits
        ]
        scores = self.model.predict(pairs, show_progress_bar=False)
        ranked = [
            RankedHit(hit=hit, rerank_score=float(score))
            for hit, score in zip(hits, scores, strict=True)
        ]
        return sorted(ranked, key=lambda item: item.rerank_score, reverse=True)


def doc_metrics(retrieved: list[str], expected: set[str]) -> tuple[float, float]:
    recall = len(set(retrieved) & expected) / max(1, len(expected))
    first = next(
        (rank for rank, doc_id in enumerate(retrieved, start=1) if doc_id in expected),
        None,
    )
    return recall, 1 / first if first else 0.0


def evaluate(
    index: SearchIndex,
    cases: list[dict],
    *,
    candidate_k: int,
    final_k: int,
    lexical: bool,
    reranker: CrossEncoderReranker | None,
) -> dict[str, float]:
    baseline_recalls: list[float] = []
    baseline_rrs: list[float] = []
    reranked_recalls: list[float] = []
    reranked_rrs: list[float] = []
    for case in cases:
        candidates = index.search(case["question"], top_k=candidate_k)
        ordered = (
            lexical_rerank(case["question"], candidates)
            if lexical
            else reranker.rerank(case["question"], candidates)
        )
        expected = set(case["relevant_doc_ids"])
        baseline_ids = [hit.chunk.doc_id for hit in candidates[:final_k]]
        reranked_ids = [item.hit.chunk.doc_id for item in ordered[:final_k]]
        baseline_recall, baseline_rr = doc_metrics(baseline_ids, expected)
        reranked_recall, reranked_rr = doc_metrics(reranked_ids, expected)
        baseline_recalls.append(baseline_recall)
        baseline_rrs.append(baseline_rr)
        reranked_recalls.append(reranked_recall)
        reranked_rrs.append(reranked_rr)
    return {
        "baseline_recall": statistics.mean(baseline_recalls),
        "baseline_mrr": statistics.mean(baseline_rrs),
        "reranked_recall": statistics.mean(reranked_recalls),
        "reranked_mrr": statistics.mean(reranked_rrs),
    }


def validate_args(args: argparse.Namespace) -> None:
    if args.final_k <= 0 or args.candidate_k < args.final_k:
        raise ValueError("se requiere candidate-k >= final-k > 0")
    if args.limit <= 0:
        raise ValueError("limit debe ser > 0")


def main() -> int:
    args = parse_args()
    validate_args(args)
    chunks = heading_chunks(load_documents())
    index = SearchIndex(chunks, lexical=args.lexical)
    reranker = None if args.lexical else CrossEncoderReranker(args.model)

    candidates = index.search(args.question, top_k=args.candidate_k)
    ranked = (
        lexical_rerank(args.question, candidates)
        if args.lexical
        else reranker.rerank(args.question, candidates)
    )
    before = {hit.chunk.chunk_id: rank for rank, hit in enumerate(candidates, start=1)}
    table = Table(title="Retrieval → reranking")
    table.add_column("final")
    table.add_column("inicial")
    table.add_column("chunk")
    table.add_column("retrieval", justify="right")
    table.add_column("reranker", justify="right")
    for rank, item in enumerate(ranked[: args.final_k], start=1):
        table.add_row(
            str(rank),
            str(before[item.hit.chunk.chunk_id]),
            item.hit.chunk.chunk_id,
            f"{item.hit.score:.3f}",
            f"{item.rerank_score:.3f}",
        )
    console.print(table)

    with (DATA_DIR / "eval_dataset.json").open(encoding="utf-8") as handle:
        cases = json.load(handle)[: args.limit]
    metrics = evaluate(
        index,
        cases,
        candidate_k=args.candidate_k,
        final_k=args.final_k,
        lexical=args.lexical,
        reranker=reranker,
    )
    summary = Table(title=f"Evaluación · {len(cases)} casos · final@{args.final_k}")
    summary.add_column("pipeline")
    summary.add_column("doc recall", justify="right")
    summary.add_column("MRR", justify="right")
    summary.add_row(
        "retrieval",
        f"{metrics['baseline_recall']:.1%}",
        f"{metrics['baseline_mrr']:.3f}",
    )
    summary.add_row(
        "retrieval + reranker",
        f"{metrics['reranked_recall']:.1%}",
        f"{metrics['reranked_mrr']:.3f}",
    )
    console.print(summary)
    if args.lexical:
        console.print("[dim]Modo offline: el reranker es una heurística auditable.[/dim]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
