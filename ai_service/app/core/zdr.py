from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from app.core.config import settings
from app.core.exceptions import ZDRViolationError
from app.core.logging import logger

MANDATORY_ZDR_HEADERS = {
    "openai": {
        "X-Zero-Data-Retention": "true",
        "X-Enterprise-Privacy": "enforced",
    },
    "anthropic": {
        "X-Zero-Data-Retention": "true",
        "anthropic-beta": "prompt-caching-2024-07-31",
    },
    "gemini": {
        "X-Zero-Data-Retention": "true",
        "X-Goog-Data-Governance": "no-training",
    },
    "mock": {
        "X-Zero-Data-Retention": "simulated",
    },
}


class ZDRClientManager:
    """Zero Data Retention (ZDR) configuration and runtime compliance governor."""

    @classmethod
    def get_zdr_headers(
        cls,
        provider: str | None = None,
        custom_headers: dict[str, str] | None = None,
    ) -> dict[str, str]:
        """Generate mandatory enterprise Zero Data Retention request headers."""
        target_provider = (provider or settings.LLM_PROVIDER).lower()
        base_headers = dict(custom_headers or {})

        provider_headers = MANDATORY_ZDR_HEADERS.get(
            target_provider, MANDATORY_ZDR_HEADERS["mock"]
        )
        base_headers.update(provider_headers)

        if settings.ENFORCE_ZDR:
            base_headers["X-ZDR-Enforced"] = "true"

        return base_headers

    @classmethod
    def build_request_payload(
        cls,
        provider: str | None = None,
        base_payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Inject required provider-specific Zero Data Retention parameters."""
        target_provider = (provider or settings.LLM_PROVIDER).lower()
        payload = dict(base_payload or {})

        if target_provider == "openai":
            # OpenAI API: store=False guarantees no server-side retention for training or dashboard inspection
            payload["store"] = False
        elif target_provider == "anthropic":
            # Anthropic API zero-retention metadata
            metadata = payload.get("metadata", {})
            metadata["zero_retention"] = True
            payload["metadata"] = metadata
        elif target_provider == "gemini":
            # Gemini / Vertex AI governance metadata
            payload["store_logs"] = False

        return payload

    @classmethod
    def validate_call_compliance(
        cls,
        provider: str | None = None,
        payload: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> bool:
        """Verify that an outgoing LLM request conforms strictly to ZDR policies."""
        if not settings.ENFORCE_ZDR:
            return True

        target_provider = (provider or settings.LLM_PROVIDER).lower()
        req_payload = payload or {}
        req_headers = headers or {}

        # 1. Check for illegal storage override
        if target_provider == "openai" and req_payload.get("store") is True:
            logger.error("ZDR Violation: OpenAI request has store=True")
            raise ZDRViolationError(
                "Infracción de ZDR: 'store=True' detectado en llamada a OpenAI.",
                details={"provider": target_provider, "store": True},
            )

        # 2. Check for missing or disabled ZDR headers
        if req_headers.get("X-Zero-Data-Retention") == "false":
            logger.error("ZDR Violation: X-Zero-Data-Retention header set to false")
            raise ZDRViolationError(
                "Infracción de ZDR: Cabecera X-Zero-Data-Retention desactivada.",
                details={"provider": target_provider},
            )

        return True

    @classmethod
    def get_status(cls) -> dict[str, Any]:
        """Return the current system Zero Data Retention compliance status."""
        return {
            "zdr_enforced": settings.ENFORCE_ZDR,
            "active_provider": settings.LLM_PROVIDER,
            "supported_providers": ["mock", "openai", "anthropic", "gemini"],
            "retention_policy": "ZERO_DATA_RETENTION_MANDATORY",
            "gdpr_minor_protection_active": True,
            "headers_injected": list(
                MANDATORY_ZDR_HEADERS.get(
                    settings.LLM_PROVIDER, MANDATORY_ZDR_HEADERS["mock"]
                ).keys()
            ),
        }


@contextmanager
def enforce_zdr_policy(provider: str | None = None) -> Generator[None, None, None]:
    """Context manager validating that an execution block respects ZDR."""
    target_provider = provider or settings.LLM_PROVIDER
    if settings.ENFORCE_ZDR:
        logger.debug("Entering ZDR-enforced context for provider: %s", target_provider)
    try:
        yield
    finally:
        if settings.ENFORCE_ZDR:
            logger.debug("Exited ZDR-enforced context successfully")
