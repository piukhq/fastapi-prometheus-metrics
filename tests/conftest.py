from typing import Any

import pytest

from fastapi import FastAPI

from fastapi_prometheus_metrics.endpoints import router
from fastapi_prometheus_metrics.middleware import PrometheusMiddleware


@pytest.fixture(scope="module")
def app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(PrometheusMiddleware)
    app.include_router(router)

    @app.get("/path/{retailer_slug}")
    async def test_route(retailer_slug: str) -> dict:
        return {"message": f"Hello {retailer_slug}"}

    @app.get(path="/livez")
    async def livez() -> Any:
        return {}

    @app.get(path="/healthz")
    async def healthz() -> Any:
        return {}

    @app.get(path="/readyz")
    async def readyz() -> Any:
        return {}

    return app
