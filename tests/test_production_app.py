from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "modulo-08-production-engineering/docker/app.py"
SPEC = importlib.util.spec_from_file_location("llmec_production_app", APP_PATH)
assert SPEC and SPEC.loader
production = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = production
SPEC.loader.exec_module(production)


def test_health_readiness_answer_and_validation_contracts() -> None:
    with TestClient(production.app) as client:
        assert client.get("/health").json() == {"status": "ok"}
        ready = client.get("/ready")
        assert ready.status_code == 200
        assert ready.json()["pipeline"] == production.PIPELINE

        answer = client.post("/v1/answer", json={"question": "He expuesto una clave API"})
        assert answer.status_code == 200
        assert answer.json()["category"] == "security"
        assert len(answer.json()["request_fingerprint"]) == 16

        billing = client.post("/v1/answer", json={"question": "  Revisa mi factura  "})
        assert billing.json()["category"] == "billing"
        general = client.post("/v1/answer", json={"question": "Necesito contexto adicional"})
        assert general.json()["category"] == "general"

        assert client.post("/v1/answer", json={"question": "  "}).status_code == 422
        assert client.post("/v1/answer", json={"question": "x" * 2_001}).status_code == 422

    without_lifespan = TestClient(production.app)
    response = without_lifespan.get("/ready")
    assert response.status_code == 503
    assert response.json() == {"status": "not_ready"}


def test_prometheus_labels_use_route_templates_and_bound_unknown_paths() -> None:
    with TestClient(production.app) as client:
        for index in range(25):
            assert client.get(f"/random-unmatched-{index}").status_code == 404
        metrics = client.get("/metrics").text

    assert 'endpoint="__unmatched__",status="404"' in metrics
    assert 'endpoint="/health",status="200"' in metrics
    assert "/random-unmatched-0" not in metrics
    assert "/random-unmatched-24" not in metrics
