from fastapi import APIRouter, status

from app.graph.pipeline import run_evaluation_pipeline
from app.schemas.request import EvaluationRequest
from app.schemas.response import EvaluationResponse

router = APIRouter()


@router.post(
    "/evaluate",
    response_model=EvaluationResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate writing submission",
    description="Executes the LangGraph evaluation pipeline over the candidate text.",
)
async def evaluate_submission(
    payload: EvaluationRequest,
) -> EvaluationResponse:
    return await run_evaluation_pipeline(payload)
