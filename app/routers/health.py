from fastapi import APIRouter

from app.dependencies import InferenceService
from app.schemas import HealthResponse


router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
)
def health(
    service: InferenceService,
) -> HealthResponse:
    """Report loaded-model readiness."""
    return HealthResponse(
        status="OK",
        model_version=service.model_version,
    )