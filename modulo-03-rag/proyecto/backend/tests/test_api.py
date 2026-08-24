"""Pruebas sin red del contrato y el baseline."""

from pathlib import Path

import pytest
from app import rag
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_exposes_loaded_index() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["documents"] == 6
    assert body["chunks"] >= body["documents"]
    assert body["pipeline"] == "tfidf-extractive-v1"


def test_query_returns_traceable_evidence() -> None:
    response = client.post(
        "/query",
        json={"question": "¿Cuánto dura un enlace de recuperación de contraseña?", "top_k": 4},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["abstained"] is False
    assert "30 minutos" in body["answer"]
    assert 1 <= len(body["evidence"]) <= 4
    assert any(item["document_id"] == "seguridad-cuentas" for item in body["evidence"])
    cited_ids = {item["chunk_id"] for item in body["evidence"] if item["chunk_id"] in body["answer"]}
    assert cited_ids
    assert all(item["score"] > 0 for item in body["evidence"])


def test_unknown_query_abstains() -> None:
    response = client.post(
        "/query",
        json={"question": "¿Cuál es la masa orbital del exoplaneta ZXQ-919?", "top_k": 4},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["abstained"] is True
    assert body["answer"] == "No hay evidencia suficiente en el corpus."
    assert body["evidence"] == []


@pytest.mark.parametrize(
    "payload",
    [
        {"question": "  ", "top_k": 4},
        {"question": "ok", "top_k": 0},
        {"question": "ok", "top_k": 13},
        {"question": "ok", "top_k": 1.5},
    ],
)
def test_each_invalid_query_boundary_is_rejected(payload: dict) -> None:
    response = client.post("/query", json=payload)
    assert response.status_code == 422


def test_section_chunks_reject_duplicate_document_ids(tmp_path: Path) -> None:
    for name in ("one.md", "two.md"):
        (tmp_path / name).write_text(
            f"---\ndoc_id: duplicate\ntitle: {name}\n---\n\n## Section\nContent.\n",
            encoding="utf-8",
        )
    with pytest.raises(ValueError, match="doc_id duplicado"):
        rag.section_chunks(tmp_path)


def test_service_rejects_invalid_direct_calls() -> None:
    with pytest.raises(ValueError, match="question"):
        rag.TfidfRagService.search(object(), " ", 4)
    with pytest.raises(ValueError, match="top_k"):
        rag.TfidfRagService.search(object(), "valid", 0)
