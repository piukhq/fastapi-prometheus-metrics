from unittest import mock

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from fastapi_prometheus_metrics.enums import EventSignals


@mock.patch("fastapi_prometheus_metrics.middleware.signal", autospec=True)
def test_prometheus_middleware(mock_signal: mock.MagicMock, app: FastAPI) -> None:
    client = TestClient(app)
    retailer_slug = "test-retailer"
    endpoint = f"/path/{retailer_slug}"

    resp = client.get(endpoint)

    expected_calls = [  # The expected call stack for signal, in order
        mock.call(EventSignals.RECORD_HTTP_REQ),
        mock.call().send(
            "fastapi_prometheus_metrics.middleware",
            endpoint="/path/[retailer_slug]",
            retailer="test-retailer",
            latency=mock.ANY,
            response_code=status.HTTP_200_OK,
            method="GET",
        ),
        mock.call(EventSignals.INBOUND_HTTP_REQ),
        mock.call().send(
            "fastapi_prometheus_metrics.middleware",
            endpoint="/path/[retailer_slug]",
            retailer="test-retailer",
            response_code=status.HTTP_200_OK,
            method="GET",
        ),
    ]

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == {"message": f"Hello {retailer_slug}"}
    mock_signal.assert_has_calls(expected_calls)


@mock.patch("fastapi_prometheus_metrics.middleware.signal", autospec=True)
def test_prometheus_middleware_does_not_send_metric_for_livez(mock_signal: mock.MagicMock, app: FastAPI) -> None:
    client = TestClient(app)
    for path in ("/metrics", "/livez", "/healthz", "/readyz"):
        resp = client.get(path)

        assert resp.status_code == status.HTTP_200_OK
        mock_signal.assert_not_called()
