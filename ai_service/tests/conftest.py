from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Test client for FastAPI ai_service."""
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture
def sample_b2_request() -> dict[str, Any]:
    """Valid B2 evaluation request fixture."""
    return {
        "submission_id": "test-sub-1234",
        "student_text": (
            "In recent years, the technology has changed our life. "
            "Many people is using computers and informations are accessible to everyone. "
            "I am agree that digital tools bring benefits, untill we lose personal contact."
        ),
        "task_prompt": "Write an essay discussing the impact of digital technology.",
        "level": "B2",
        "text_type": "essay",
        "min_words": 140,
        "max_words": 190,
    }


@pytest.fixture
def sample_ai_generated_request() -> dict[str, Any]:
    """Request simulating AI-generated phrasing."""
    return {
        "submission_id": "test-ai-synthetic-1",
        "student_text": (
            "In the contemporary era, the paradigm shift in digital education "
            "plays a pivotal role in the tapestry of modern academic institutions. "
            "Moreover, another crucial aspect is the seamless integration of virtual pedagogies. "
            "In conclusion, it is vital to remember that continuous adaptation remains imperative."
        ),
        "task_prompt": "Write an essay on modern educational shifts.",
        "level": "C1",
        "text_type": "essay",
        "min_words": 220,
        "max_words": 260,
    }
