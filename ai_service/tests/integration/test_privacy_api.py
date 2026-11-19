import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_privacy_sanitize_endpoint(async_client: AsyncClient) -> None:
    payload = {
        "text": "Hello, my name is Carlos Gomez and my email is carlos@example.com with DNI 12345678Z.",
    }
    response = await async_client.post("/internal/v1/privacy/sanitize", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["pii_detected_count"] >= 3
    assert "[EMAIL_REDACTED]" in data["sanitized_text"]
    assert "[ID_REDACTED]" in data["sanitized_text"]
    assert "[STUDENT_NAME_REDACTED]" in data["sanitized_text"]
    assert len(data["redactions"]) >= 3


@pytest.mark.asyncio
async def test_privacy_status_endpoint(async_client: AsyncClient) -> None:
    response = await async_client.get("/internal/v1/privacy/status")

    assert response.status_code == 200
    data = response.json()
    assert data["zdr_enforced"] is True
    assert data["retention_policy"] == "ZERO_DATA_RETENTION_MANDATORY"
    assert data["gdpr_minor_protection_active"] is True
    assert "openai" in data["supported_providers"]


@pytest.mark.asyncio
async def test_validate_minor_consent_endpoint(async_client: AsyncClient) -> None:
    # 12 years old without guardian consent
    payload_fail = {
        "birth_date": "2014-01-01",
        "reference_date": "2026-11-19",
    }
    res_fail = await async_client.post(
        "/internal/v1/privacy/validate-minor-consent", json=payload_fail
    )
    assert res_fail.status_code == 200
    data_fail = res_fail.json()
    assert data_fail["is_minor"] is True
    assert data_fail["requires_guardian_consent"] is True
    assert data_fail["is_valid"] is False

    # 12 years old with guardian consent
    payload_ok = {
        "birth_date": "2014-01-01",
        "reference_date": "2026-11-19",
        "guardian_consent": {
            "guardian_name": "Laura Perez",
            "guardian_email": "laura@example.com",
            "guardian_phone": "+34 654 321 000",
            "relationship": "PARENT",
            "verification_method": "DIGITAL_SIGNATURE",
            "consent_date": "2026-09-01",
            "document_hash": "abcdef1234567890",
            "status": "ACTIVE",
        },
    }
    res_ok = await async_client.post(
        "/internal/v1/privacy/validate-minor-consent", json=payload_ok
    )
    assert res_ok.status_code == 200
    data_ok = res_ok.json()
    assert data_ok["is_valid"] is True


@pytest.mark.asyncio
async def test_right_to_erasure_endpoint(async_client: AsyncClient) -> None:
    payload = {
        "student_id": "test-student-999",
        "submission_text": "Sensitive essay text to be erased.",
        "photo_paths": ["uploads/photo_1.png"],
    }
    response = await async_client.post(
        "/internal/v1/privacy/right-to-erasure", json=payload
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert len(data["student_id_hash"]) == 64
    assert len(data["verification_hash"]) == 64


@pytest.mark.asyncio
async def test_evaluate_endpoint_returns_zdr_and_pii_metadata(
    async_client: AsyncClient,
) -> None:
    request_data = {
        "submission_id": "sub-zdr-001",
        "student_text": (
            "My name is Carlos Gomez. I believe environmental protection is essential. "
            "Firstly, renewable energy helps reduce emissions. Secondly, recycling avoids waste. "
            "In conclusion, governments and citizens must collaborate. Contact carlos@test.com."
        ),
        "task_prompt": "Write an essay about environmental protection and renewable energy.",
        "level": "B2",
        "text_type": "essay",
        "min_words": 140,
        "max_words": 190,
    }
    response = await async_client.post("/internal/v1/evaluate", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["zdr_enforced"] is True
    assert data["sanitized_pii_count"] >= 1
    assert (
        "EMAIL" in data["pii_types_detected"]
        or "STUDENT_NAME" in data["pii_types_detected"]
    )
