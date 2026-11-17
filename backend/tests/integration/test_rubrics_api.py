import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.seed_rubrics import seed_default_rubrics


@pytest.mark.asyncio
async def test_get_rubrics_with_level_filter_and_seed(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Scenario 1: Consulta de Rúbricas Base en Backend.

    Given: Base de datos inicializada con plantillas Cambridge.
    When: GET /api/v1/rubrics?level=B2
    Then: HTTP 200 con la rúbrica oficial B2 First con 4 criterios y bandas 0-5.
    """
    await seed_default_rubrics(db_session)

    response = await async_client.get("/api/v1/rubrics?level=B2")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1

    b2_rubric = data[0]
    assert b2_rubric["cefr_level"] == "B2"
    assert b2_rubric["is_template"] is True
    assert len(b2_rubric["criteria"]) == 4

    criteria_names = {c["name"] for c in b2_rubric["criteria"]}
    assert criteria_names == {
        "Content",
        "Communicative Achievement",
        "Organisation",
        "Language",
    }

    # Verify band descriptors 0 through 5 are present
    for criterion in b2_rubric["criteria"]:
        for band in ["0", "1", "2", "3", "4", "5"]:
            assert band in criterion["descriptors"]
            assert len(criterion["descriptors"][band]) > 0


@pytest.mark.asyncio
async def test_create_custom_rubric_with_criteria(
    async_client: AsyncClient,
) -> None:
    """Scenario 2: Creación de Rúbrica Personalizada con Criterios.

    Given: Payload válido con metadatos de rúbrica y criterios ponderados.
    When: POST /api/v1/rubrics
    Then: Persiste entidad, responde HTTP 201 y asigna identificadores UUIDv4.
    """
    payload = {
        "name": "Academia Custom B1 Rubric",
        "cefr_level": "B1",
        "description": "Rúbrica institucional personalizada para nivel B1",
        "is_template": False,
        "is_active": True,
        "criteria": [
            {
                "name": "Content",
                "description": "Relevance to prompt",
                "weight": 1.0,
                "max_band": 5,
                "sort_order": 0,
                "descriptors": {"5": "Todo el contenido es relevante."},
            },
            {
                "name": "Grammar & Vocab",
                "description": "Control of basic structures",
                "weight": 1.2,
                "max_band": 5,
                "sort_order": 1,
                "descriptors": {"5": "Uso preciso de gramática básica."},
            },
        ],
    }

    response = await async_client.post("/api/v1/rubrics", json=payload)
    assert response.status_code == 201
    created = response.json()

    assert created["name"] == payload["name"]
    assert created["cefr_level"] == "B1"
    assert created["is_template"] is False
    rubric_id = uuid.UUID(created["id"])
    assert rubric_id.version == 4
    assert len(created["criteria"]) == 2

    for c in created["criteria"]:
        assert uuid.UUID(c["id"]).version == 4
        assert uuid.UUID(c["rubric_id"]) == rubric_id


@pytest.mark.asyncio
async def test_get_rubric_by_id_and_not_found(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Verify retrieving rubric by ID and 404 error handling."""
    seeded = await seed_default_rubrics(db_session)
    target = seeded[0]

    # Valid ID lookup
    response = await async_client.get(f"/api/v1/rubrics/{target.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(target.id)
    assert len(data["criteria"]) == 4

    # Non-existent UUID lookup
    random_uuid = uuid.uuid4()
    not_found_resp = await async_client.get(f"/api/v1/rubrics/{random_uuid}")
    assert not_found_resp.status_code == 404
    error_data = not_found_resp.json()
    assert error_data["detail"]["error_code"] == "RESOURCE_NOT_FOUND"


@pytest.mark.asyncio
async def test_add_criterion_to_existing_rubric(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Verify POST /api/v1/rubrics/{id}/criteria adds criterion to rubric."""
    seeded = await seed_default_rubrics(db_session)
    target = seeded[0]

    crit_payload = {
        "name": "Pronunciation & Punctuation",
        "description": "Additional criterion",
        "weight": 0.5,
        "max_band": 5,
        "sort_order": 4,
        "descriptors": {
            "5": "Excellent punctuation throughout.",
            "0": "Completely lacking punctuation.",
        },
    }

    response = await async_client.post(
        f"/api/v1/rubrics/{target.id}/criteria",
        json=crit_payload,
    )
    assert response.status_code == 201
    created_crit = response.json()
    assert created_crit["name"] == crit_payload["name"]
    assert created_crit["rubric_id"] == str(target.id)
    assert uuid.UUID(created_crit["id"]).version == 4

    # Non-existent rubric returns 404
    non_existent = uuid.uuid4()
    fail_resp = await async_client.post(
        f"/api/v1/rubrics/{non_existent}/criteria",
        json=crit_payload,
    )
    assert fail_resp.status_code == 404
    assert fail_resp.json()["detail"]["error_code"] == "RESOURCE_NOT_FOUND"
