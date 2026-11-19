import pytest

from app.core.exceptions import ZDRViolationError
from app.core.zdr import ZDRClientManager, enforce_zdr_policy


def test_zdr_headers_injection() -> None:
    openai_headers = ZDRClientManager.get_zdr_headers(provider="openai")
    assert openai_headers.get("X-Zero-Data-Retention") == "true"
    assert openai_headers.get("X-Enterprise-Privacy") == "enforced"
    assert openai_headers.get("X-ZDR-Enforced") == "true"

    anthropic_headers = ZDRClientManager.get_zdr_headers(provider="anthropic")
    assert anthropic_headers.get("X-Zero-Data-Retention") == "true"
    assert "anthropic-beta" in anthropic_headers

    gemini_headers = ZDRClientManager.get_zdr_headers(provider="gemini")
    assert gemini_headers.get("X-Zero-Data-Retention") == "true"
    assert gemini_headers.get("X-Goog-Data-Governance") == "no-training"


def test_build_request_payload_zdr_enforcement() -> None:
    # OpenAI requires store=False
    openai_payload = ZDRClientManager.build_request_payload(
        provider="openai",
        base_payload={"model": "gpt-4o", "messages": []},
    )
    assert openai_payload["store"] is False

    # Anthropic zero retention metadata
    anthropic_payload = ZDRClientManager.build_request_payload(
        provider="anthropic",
        base_payload={"model": "claude-3-5-sonnet", "messages": []},
    )
    assert anthropic_payload["metadata"]["zero_retention"] is True

    # Gemini no logs
    gemini_payload = ZDRClientManager.build_request_payload(
        provider="gemini",
        base_payload={"model": "gemini-1.5-pro"},
    )
    assert gemini_payload["store_logs"] is False


def test_validate_call_compliance_success() -> None:
    headers = ZDRClientManager.get_zdr_headers("openai")
    payload = ZDRClientManager.build_request_payload("openai", {"model": "gpt-4o"})

    assert ZDRClientManager.validate_call_compliance("openai", payload, headers) is True


def test_validate_call_compliance_raises_on_store_true() -> None:
    illegal_payload = {"model": "gpt-4o", "store": True}
    with pytest.raises(ZDRViolationError) as exc_info:
        ZDRClientManager.validate_call_compliance("openai", illegal_payload)

    assert "store=True" in exc_info.value.message
    assert exc_info.value.error_code == "ZDR_VIOLATION"


def test_validate_call_compliance_raises_on_disabled_header() -> None:
    illegal_headers = {"X-Zero-Data-Retention": "false"}
    with pytest.raises(ZDRViolationError) as exc_info:
        ZDRClientManager.validate_call_compliance("openai", {}, illegal_headers)

    assert "X-Zero-Data-Retention" in exc_info.value.message


def test_zdr_status() -> None:
    status_dict = ZDRClientManager.get_status()
    assert status_dict["zdr_enforced"] is True
    assert status_dict["retention_policy"] == "ZERO_DATA_RETENTION_MANDATORY"
    assert status_dict["gdpr_minor_protection_active"] is True
    assert "mock" in status_dict["supported_providers"]
    assert "openai" in status_dict["supported_providers"]


def test_enforce_zdr_policy_context_manager() -> None:
    with enforce_zdr_policy("openai"):
        pass  # successfully executed within ZDR context
