"""Contratos públicos de la API; mantenerlos estables entre implementaciones."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2_000)
    top_k: int = Field(default=4, ge=1, le=12)

    @field_validator("question")
    @classmethod
    def reject_blank_question(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("question no puede estar vacía")
        return normalized


class Evidence(BaseModel):
    chunk_id: str
    document_id: str
    title: str
    excerpt: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    abstained: bool
    evidence: list[Evidence]
    latency_ms: float
    pipeline: str = "tfidf-extractive-v1"


class HealthResponse(BaseModel):
    status: str
    documents: int
    chunks: int
    pipeline: str
