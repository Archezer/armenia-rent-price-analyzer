from fastapi import APIRouter

from app.dependencies import InferenceService
from app.schemas import (
    PredictionRequest,
    PredictionResponse,
)

router = APIRouter(tags=["predictions"])


@router.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict(
    payload: PredictionRequest,
    service: InferenceService,
) -> PredictionResponse:
    """Estimate monthly asking rent in AMD."""
    prediction_amd = service.predict(
        payload.model_dump()
    )

    return PredictionResponse(
        predicted_monthly_rent_amd=round(
            prediction_amd
        ),
        currency="AMD",
        model_version=service.model_version,
    )