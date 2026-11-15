import logging

import pytest

from app.core.config import Settings, _parse_origins
from app.core.database import get_db_session
from app.core.logging import JSONFormatter, setup_logging


def test_parse_origins_helper() -> None:
    # 1. Comma-separated string
    assert _parse_origins("http://localhost:3000,http://example.com") == [
        "http://localhost:3000",
        "http://example.com",
    ]

    # 2. JSON array string
    assert _parse_origins('["http://site.com", "http://api.com"]') == [
        "http://site.com",
        "http://api.com",
    ]

    # 3. Invalid JSON string fallback
    assert _parse_origins("[invalid-json") == [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    # 4. Native list
    assert _parse_origins(["http://a.com", "http://b.com"]) == [
        "http://a.com",
        "http://b.com",
    ]

    # 5. Fallback for other types
    assert _parse_origins(12345) == [
        "http://localhost:3000",
        "http://localhost:5173",
    ]


def test_settings_database_url_formatting() -> None:
    settings = Settings(
        DATABASE_URL="postgresql://user:pass@testhost:5432/testdb",
    )
    assert (
        settings.async_database_url
        == "postgresql+asyncpg://user:pass@testhost:5432/testdb"
    )


def test_json_formatter() -> None:
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Test log message",
        args=(),
        exc_info=None,
    )
    output = formatter.format(record)
    assert "timestamp" in output
    assert "test_logger" in output
    assert "Test log message" in output


def test_setup_logging() -> None:
    setup_logging()
    root_logger = logging.getLogger()
    assert len(root_logger.handlers) > 0


@pytest.mark.asyncio
async def test_get_db_session_lifecycle() -> None:
    gen = get_db_session()
    session = await anext(gen)
    assert session is not None
    with pytest.raises(StopAsyncIteration):
        await anext(gen)
