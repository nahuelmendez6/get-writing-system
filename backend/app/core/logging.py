import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """Custom formatter producing JSON-formatted log records."""

    def format(self, record: logging.LogRecord) -> str:
        log_payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include extra attributes if present (excluding standard log record fields)
        standard_attrs = {
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
            "taskName",
        }
        extras = {k: v for k, v in record.__dict__.items() if k not in standard_attrs}
        if extras:
            log_payload["details"] = extras

        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_payload, default=str)


def setup_logging() -> None:
    """Configure system-wide structured JSON logging."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Avoid duplicate handlers
    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        root_logger.addHandler(handler)
    else:
        for existing_handler in root_logger.handlers:
            existing_handler.setFormatter(JSONFormatter())


logger = logging.getLogger("get_idiomas.backend")
