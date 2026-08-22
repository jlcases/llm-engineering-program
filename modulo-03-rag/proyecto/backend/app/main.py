"""FastAPI del baseline RAG de NebulaOps."""

from __future__ import annotations

import os
import time
from pathlib import Path

from fastapi import FastAPI

from app.rag import TfidfRagService
from app.schemas import Evidence, HealthResponse, QueryRequest, QueryResponse

DEFAULT_CORPUS = Path(__file__).resolve().parents[3] / "labs" / "data"
CORPUS_DIR = Path(os.getenv("RAG_CORPUS_DIR", str(DEFAULT_CORPUS))).resolve()
service = TfidfRagService(CORPUS_DIR)

app = FastAPI(
    title="NebulaOps Knowledge Assistant",
    version="1.0.0",
    description="Baseline RAG offline y trazable para el proyecto del módulo III.",
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        documents=service.document_count,
        chunks=len(service.chunks),
        pipeline=service.pipeline,
    )


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    started = time.perf_counter()
    hits = service.search(request.question, request.top_k)
    answer, abstained = service.answer(request.question, hits)
    evidence = [
        Evidence(
            chunk_id=hit.chunk.chunk_id,
            document_id=hit.chunk.document_id,
            title=hit.chunk.title,
            excerpt=hit.chunk.text[:500],
            score=hit.score,
        )
        for hit in hits
    ]
    return QueryResponse(
        answer=answer,
        abstained=abstained,
        evidence=evidence,
        latency_ms=round((time.perf_counter() - started) * 1_000, 3),
    )
