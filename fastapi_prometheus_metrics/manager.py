import logging

from typing import Union

from blinker import signal
from prometheus_client import Counter, Histogram

from .enums import EventSignals

logger = logging.getLogger(__name__)


class Singleton(type):
    """Singleton metaclass"""

    _instances: dict = {}

    def __call__(cls, *args, **kwargs):  # type:ignore
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        else:
            logger.warning(f"singleton already instantiated; using {str(cls._instances[cls])}")
        return cls._instances[cls]


class PrometheusManager(metaclass=Singleton):
    def __init__(self, app_name: str) -> None:
        self.app_name = app_name
        self.metric_types = self._get_metric_types()
        signal(EventSignals.INBOUND_HTTP_REQ).connect(self.inbound_http_request)
        signal(EventSignals.RECORD_HTTP_REQ).connect(self.record_http_request)

    def __str__(self) -> str:
        return f"PrometheusManager(app_name={self.app_name})"

    def inbound_http_request(
        self, sender: Union[object, str], endpoint: str, retailer: str, response_code: int, method: str
    ) -> None:
        """
        :param sender: Could be a class instance, or a string description of who the sender is
        :param app: the application e.g. polaris
        :param endpoint: inbound URL stripped of mutable values
        :param retailer: retailer slug
        :param response_code: HTTP status code e.g. 200
        :param method: HTTP method e.g. "GET"
        """
        counter = self.metric_types["counters"]["inbound_http_request"]
        counter.labels(
            app=self.app_name,
            endpoint=endpoint,
            retailer=retailer,
            response_code=response_code,
            method=method,
        ).inc()

    def record_http_request(
        self,
        sender: Union[object, str],
        endpoint: str,
        retailer: str,
        response_code: int,
        method: str,
        latency: Union[int, float],
    ) -> None:
        """
        :param sender: Could be a class instance, or a string description of who the sender is
        :param app: the application e.g. polaris
        :param endpoint: inbound URL stripped of mutable values
        :param retailer: retailer slug
        :param response_code: HTTP status code e.g. 200
        :param method: HTTP method e.g. "POST"
        :param latency: HTTP request time in seconds
        """

        histogram = self.metric_types["histograms"]["request_latency"]
        histogram.labels(
            app=self.app_name,
            endpoint=endpoint,
            retailer=retailer,
            response_code=response_code,
            method=method,
        ).observe(latency)

    @staticmethod
    def _get_metric_types() -> dict:
        """
        Define metric types here (see https://prometheus.io/docs/concepts/metric_types/),
        with the name, description and a list of the labels they expect.
        """

        metric_types = {
            "counters": {
                "inbound_http_request": Counter(
                    name="inbound_http_request_total",
                    documentation="Incremental count of inbound HTTP requests",
                    labelnames=("app", "endpoint", "retailer", "response_code", "method"),
                ),
            },
            "histograms": {
                "request_latency": Histogram(
                    name="request_latency_seconds",
                    documentation="Request latency seconds",
                    labelnames=("app", "endpoint", "retailer", "response_code", "method"),
                )
            },
        }

        return metric_types
