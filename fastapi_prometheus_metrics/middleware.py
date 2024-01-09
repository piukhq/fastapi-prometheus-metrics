import os
import time

from collections.abc import Callable

from blinker import signal
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import Response, UJSONResponse
from sentry_sdk import Hub, start_span
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.routing import Match

from .enums import EventSignals


def _metrics_debug() -> bool:
    return os.getenv("METRICS_DEBUG", "False").lower() == "true"


class MetricsSecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        local_port = request.scope["server"][1]
        if (request.url.path == "/metrics" and local_port != 9100 and not _metrics_debug()) or (
            request.url.path != "/metrics" and local_port == 9100
        ):
            return UJSONResponse({"detail": "Not found"}, status_code=status.HTTP_404_NOT_FOUND)
        return await call_next(request)


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Time our code
        parent_span = Hub.current.scope.span
        trace: Callable = start_span if parent_span is None else parent_span.start_child  # type: ignore [assignment]

        with trace(op="prometheus-middleware") as span:
            before_time = time.perf_counter()
            with span.start_child(op="endpoint-function"):
                response = await call_next(request)
            after_time = time.perf_counter()

            latency = after_time - before_time
            method = request.method
            endpoint, retailer = self._get_endpoint_and_retailer(request)
            routes_to_ignore = ["/metrics", "/livez", "/healthz", "/readyz"]
            if endpoint not in routes_to_ignore:
                with span.start_child(op="prometheus-signals"):
                    signal(EventSignals.RECORD_HTTP_REQ).send(
                        __name__,
                        endpoint=endpoint,
                        retailer=retailer,
                        latency=latency,
                        response_code=response.status_code,
                        method=method,
                    )

                    signal(EventSignals.INBOUND_HTTP_REQ).send(
                        __name__,
                        endpoint=endpoint,
                        retailer=retailer,
                        response_code=response.status_code,
                        method=method,
                    )

            return response

    def _get_endpoint_and_retailer(self, request: Request) -> tuple[str, str]:
        url = request.url.path
        path_params = request.path_params

        # path_params are populated when calling "call_next" in a middleware,
        # so if we return before calling it we need to parse the endpoint manually to extract them.
        if not path_params:
            for route in request.app.router.routes:
                match, scope = route.matches(request)
                if match == Match.FULL:
                    path_params = scope["path_params"]
                    break

        for k, v in path_params.items():
            url = url.replace(v, f"[{k}]")

        return url, path_params.get("retailer_slug", "")
