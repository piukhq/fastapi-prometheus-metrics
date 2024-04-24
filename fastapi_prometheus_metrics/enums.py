from enum import StrEnum


class EventSignals(StrEnum):
    INBOUND_HTTP_REQ = "inbound-http-request"
    RECORD_HTTP_REQ = "record-http-request"
