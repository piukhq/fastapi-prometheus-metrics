from unittest import mock

import pytest

from blinker import signal

from fastapi_prometheus_metrics.enums import EventSignals
from fastapi_prometheus_metrics.manager import PrometheusManager, Singleton


@pytest.fixture(autouse=True)
def prometheus_signal_manager() -> PrometheusManager:
    return PrometheusManager("some-app")


class TestSingleton:
    def test_singleton(self) -> None:
        class mock_class(metaclass=Singleton):
            pass

        first = mock_class()
        second = mock_class()

        assert first is second


class TestPrometheus:
    @mock.patch("fastapi_prometheus_metrics.manager.Counter.inc", autospec=True)
    def test_inbound_http_request(self, mock_prometheus_counter_inc: mock.MagicMock) -> None:
        """
        Test that the inbound http request counter increments
        """
        signal(EventSignals.INBOUND_HTTP_REQ).send(
            self, endpoint="/some/endpoint", retailer="some-retailer", response_code=200, method="get"
        )
        mock_prometheus_counter_inc.assert_called_once()

    @mock.patch("fastapi_prometheus_metrics.manager.Histogram.observe", autospec=True)
    def test_record_http_request(self, mock_prometheus_histogram_observe: mock.MagicMock) -> None:
        """
        Test that the record http request histogram's observe() is called without error
        """
        signal(EventSignals.RECORD_HTTP_REQ).send(
            self,
            endpoint="/some/endpoint",
            retailer="some-retailer",
            response_code=500,
            method="POST",
            latency=1.234,
        )
        mock_prometheus_histogram_observe.assert_called_once()
