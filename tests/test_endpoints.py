from fastapi.applications import FastAPI
from fastapi.testclient import TestClient

from fastapi_prometheus_metrics.endpoints import router


def test_metrics(app: FastAPI) -> None:
    app.include_router(router)
    client = TestClient(app)
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "# HELP python_gc_objects_collected_total" in resp.text
