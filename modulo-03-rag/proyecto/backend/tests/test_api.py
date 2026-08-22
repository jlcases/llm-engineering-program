"""Pruebas sin red del contrato y el baseline."""

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
    assert all(item["chunk_id"] in body["answer"] or item["score"] >= 0 for item in body["evidence"])


def test_unknown_query_abstains() -> None:
    response = client.post(
        "/query",
        json={"question": "¿Cuál es la masa orbital del exoplaneta ZXQ-919?", "top_k": 4},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["abstained"] is True
    assert body["answer"] == "No hay evidencia suficiente en el corpus."


def test_invalid_query_is_rejected() -> None:
    response = client.post("/query", json={"question": "  ", "top_k": 0})
    assert response.status_code == 422
