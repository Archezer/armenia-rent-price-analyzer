from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Request

from app.schemas import (
    HealthResponse,
    PredictionRequest,
    PredictionResponse,
)
from price_analyzer.inference.service import (
    RentInferenceService,
)

ARTIFACT_DIRECTORY = Path(
    "artifacts/rent_model_v1"
)

@asynccontextmanager
async def lifespan(
    app: FastAPI
) -> AsyncIterator[None]:
    app.state.inference_service = (
        RentInferenceService.load(
            ARTIFACT_DIRECTORY
        )
    )

    yield

app = FastAPI(
    title='Armenian Rent Estimator',
    version='1.0.0',
    lifespan=lifespan
)

def get_inference_service(
        request: Request
) -> RentInferenceService:
    return request.app.state.inference_service

InferenceService = Annotated[
    RentInferenceService,
    Depends(get_inference_service)
]


@app.get(
    '/health',
    response_model=HealthResponse
)
def health(
    service: InferenceService
) -> HealthResponse:
    return HealthResponse(
        status='OK',
        model_version=service.model_version
    )

@app.post(
    '/predict',
    response_model=PredictionResponse
)
def predict(
    payload: PredictionRequest,
    service: InferenceService
) -> PredictionResponse:
    prediction_amd = service.predict(
        payload.model_dump()
    )

    return PredictionResponse(
        predicted_monthly_rent_amd=round(
            prediction_amd
        ),
        currency='AMD',
        model_version=service.model_version
    )