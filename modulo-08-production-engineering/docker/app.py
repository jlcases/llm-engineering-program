"""API de entrenamiento contenida: health, readiness, respuesta y métricas Prometheus."""

from __future__ import annotations

import hashlib
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field, field_validator

REQUESTS = Counter(
    "llmops_requests_total",
    "Peticiones procesadas por endpoint y estado.",
    ("endpoint", "status"),
)
LATENCY = Histogram(
    "llmops_request_duration_seconds",
    "Duración de la petición sin labels de usuario.",
    ("endpoint",),
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
)
PIPELINE = os.getenv("PIPELINE_VERSION", "deterministic-training-v1")
UNMATCHED_ENDPOINT = "__unmatched__"


class AnswerRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2_000)

    @field_validator("question")
    @classmethod
    def strip_question(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("question no puede estar vacía")
        return normalized


class AnswerResponse(BaseModel):
    answer: str
    category: str
    request_fingerprint: str
    pipeline: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.ready = True
    yield
    app.state.ready = False


app = FastAPI(
    title="LLMOps container lab",
    version="1.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def observe(request: Request, call_next):
    started = time.perf_counter()
    status = "500"
    try:
        response = await call_next(request)
        status = str(response.status_code)
        return response
    finally:
        route = request.scope.get("route")
        endpoint = getattr(route, "path", None)
        if not isinstance(endpoint, str) or not endpoint.startswith("/"):
            endpoint = UNMATCHED_ENDPOINT
        REQUESTS.labels(endpoint=endpoint, status=status).inc()
        LATENCY.labels(endpoint=endpoint).observe(time.perf_counter() - started)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness: el proceso puede atender HTTP; no llama a ningún proveedor."""
    return {"status": "ok"}


@app.get("/ready")
def ready(request: Request, response: Response) -> dict[str, str]:
    """Readiness: la inicialización local terminó."""
    if not getattr(request.app.state, "ready", False):
        response.status_code = 503
        return {"status": "not_ready"}
    return {"status": "ready", "pipeline": PIPELINE}


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/v1/answer", response_model=AnswerResponse)
def answer(payload: AnswerRequest) -> AnswerResponse:
    lowered = payload.question.casefold()
    if any(term in lowered for term in ("clave", "mfa", "token", "seguridad")):
        category = "security"
        text = "Revoca primero la credencial afectada y valida el alcance del incidente."
    elif any(term in lowered for term in ("factura", "pago", "cobro")):
        category = "billing"
        text = "Verifica el identificador y el estado de la factura antes de modificarla."
    else:
        category = "general"
        text = "Aclara el resultado esperado y aporta evidencia verificable."
    fingerprint = hashlib.sha256(payload.question.encode("utf-8")).hexdigest()[:16]
    return AnswerResponse(
        answer=text,
        category=category,
        request_fingerprint=fingerprint,
        pipeline=PIPELINE,
    )
