import pytest

from fastapi import FastAPI

from fastapi_prometheus_metrics.middleware import PrometheusMiddleware


@pytest.fixture(scope="module")
def app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(PrometheusMiddleware)

    @app.get("/path/{retailer_slug}")
    async def test_route(retailer_slug: str) -> dict:
        return {"message": f"Hello {retailer_slug}"}

    return app
