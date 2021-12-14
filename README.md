# FastAPI Prometheus Metrics

Utilities for providing internal HTTP metrics for FastAPI.

## Provides

* /metrics endpoint
* Middleware to ensure /metrics is accessed only on port 9100 and other URLs not accessible on port 9100
* Middleware to manipulate prometheus_client metric objects

## Environment Variables

* PROMETHEUS_MULTIPROC_DIR (required - the location to store metrics data)
* METRICS_DEBUG (false by default - to view /metrics endpoing on standard port)
