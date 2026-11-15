import logging

from app.core.config import Settings
from app.core.exceptions import (
    AIServiceException,
    LLMProviderError,
    LLMTimeoutError,
)
from app.core.logging import JSONFormatter, setup_logging


def test_core_exceptions_properties() -> None:
    exc = AIServiceException(
        error_code="TEST_ERR",
        message="Test message",
        status_code=400,
        details={"info": 123},
    )
    assert exc.error_code == "TEST_ERR"
    assert exc.message == "Test message"
    assert exc.status_code == 400
    assert exc.details == {"info": 123}

    timeout_exc = LLMTimeoutError()
    assert timeout_exc.error_code == "LLM_TIMEOUT"
    assert timeout_exc.status_code == 504

    provider_exc = LLMProviderError("Provider failure")
    assert provider_exc.error_code == "LLM_PROVIDER_ERROR"
    assert provider_exc.status_code == 502


def test_core_settings() -> None:
    s = Settings(
        ENVIRONMENT="staging",
        LLM_PROVIDER="openai",
        LLM_TIMEOUT_SECONDS=30,
    )
    assert s.ENVIRONMENT == "staging"
    assert s.LLM_PROVIDER == "openai"
    assert s.LLM_TIMEOUT_SECONDS == 30


def test_json_formatter() -> None:
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test_ai_logger",
        level=logging.ERROR,
        pathname="test.py",
        lineno=25,
        msg="Error record message",
        args=(),
        exc_info=None,
    )
    formatted = formatter.format(record)
    assert "timestamp" in formatted
    assert "test_ai_logger" in formatted
    assert "Error record message" in formatted


def test_setup_logging() -> None:
    setup_logging()
    root_logger = logging.getLogger()
    assert len(root_logger.handlers) > 0
