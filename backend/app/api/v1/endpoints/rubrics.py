import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db_session
from app.core.exceptions import NotFoundError
from app.models.rubric import Rubric, RubricCriterion
from app.schemas.rubric import (
    RubricCreate,
    RubricCriterionCreate,
    RubricCriterionRead,
    RubricRead,
)

router = APIRouter()


@router.get(
    "",
    response_model=list[RubricRead],
    status_code=status.HTTP_200_OK,
    summary="List rubrics",
    description="Retrieve all rubrics with optional level filtering and pagination.",
)
async def list_rubrics(
    level: str | None = Query(
        None,
        description="Filter rubrics by CEFR level (e.g. B1, B2, C1, C2)",
    ),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100,
        ge=1,
        le=100,
        description="Max number of records to return",
    ),
    db: AsyncSession = Depends(get_db_session),
) -> list[Rubric]:
    query = (
        select(Rubric)
        .options(selectinload(Rubric.criteria))
        .order_by(Rubric.created_at.desc())
    )

    if level:
        query = query.where(Rubric.cefr_level.ilike(level.strip()))

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get(
    "/{id}",
    response_model=RubricRead,
    status_code=status.HTTP_200_OK,
    summary="Get rubric by ID",
    description="Retrieve rubric details including criteria and band descriptors.",
)
async def get_rubric(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
) -> Rubric:
    query = select(Rubric).options(selectinload(Rubric.criteria)).where(Rubric.id == id)
    result = await db.execute(query)
    rubric = result.scalar_one_or_none()

    if rubric is None:
        raise NotFoundError(message=f"Rubric with ID '{id}' was not found.")

    return rubric


@router.post(
    "",
    response_model=RubricRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create rubric",
    description="Create a new assessment rubric with optional nested criteria.",
)
async def create_rubric(
    payload: RubricCreate,
    db: AsyncSession = Depends(get_db_session),
) -> Rubric:
    rubric = Rubric(
        name=payload.name,
        cefr_level=payload.cefr_level.upper(),
        description=payload.description,
        is_template=payload.is_template,
        is_active=payload.is_active,
    )

    for item in payload.criteria:
        criterion = RubricCriterion(
            name=item.name,
            description=item.description,
            weight=item.weight,
            max_band=item.max_band,
            sort_order=item.sort_order,
            descriptors=item.descriptors,
        )
        rubric.criteria.append(criterion)

    db.add(rubric)
    await db.commit()
    await db.refresh(rubric)
    return rubric


@router.post(
    "/{id}/criteria",
    response_model=RubricCriterionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add criterion to rubric",
    description="Attach an individual assessment criterion to an existing rubric.",
)
async def add_criterion_to_rubric(
    id: uuid.UUID,
    payload: RubricCriterionCreate,
    db: AsyncSession = Depends(get_db_session),
) -> RubricCriterion:
    rubric_query = select(Rubric).where(Rubric.id == id)
    rubric_result = await db.execute(rubric_query)
    rubric = rubric_result.scalar_one_or_none()

    if rubric is None:
        raise NotFoundError(message=f"Rubric with ID '{id}' was not found.")

    criterion = RubricCriterion(
        rubric_id=rubric.id,
        name=payload.name,
        description=payload.description,
        weight=payload.weight,
        max_band=payload.max_band,
        sort_order=payload.sort_order,
        descriptors=payload.descriptors,
    )

    db.add(criterion)
    await db.commit()
    await db.refresh(criterion)
    return criterion
