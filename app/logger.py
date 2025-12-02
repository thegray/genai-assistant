import logging
import os
import json
from contextvars import ContextVar

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
APP_MODE = os.getenv("APP_MODE", "local")

# Per-request context (e.g. correlation id)
_request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


def set_request_id(request_id: str | None):
    return _request_id_ctx.set(request_id)


def get_request_id() -> str | None:
    return _request_id_ctx.get()

def reset_request_id(token):
    _request_id_ctx.reset(token)

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "app_mode": APP_MODE,
            "time": self.formatTime(record, self.datefmt),
        }

        req_id = get_request_id()
        if req_id:
            log_record["request_id"] = req_id

        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)

        for key, value in record.__dict__.items():
            if key not in (
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
            ):
                log_record[key] = value

        return json.dumps(log_record)


logger = logging.getLogger("axrail_assistant")
logger.setLevel(LOG_LEVEL)

if not logger.handlers:
    handler = logging.StreamHandler()
    # Use JSON structured format for easy CloudWatch parsing
    formatter = JsonFormatter(datefmt="%Y-%m-%dT%H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
