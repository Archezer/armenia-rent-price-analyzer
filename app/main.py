from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_artifact_directory
from app.routers.health import router as health_router
from app.routers.predictions import (
    router as predictions_router,
)
from app.routers.recommendations import (
    router as recommendations_router,
)
from price_analyzer.inference.service import (
    RentInferenceService,
)


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncIterator[None]:
    app.state.inference_service = (
        RentInferenceService.load(
            get_artifact_directory()
        )
    )

    yield

app = FastAPI(
    title="Armenian Rent Estimator",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(predictions_router)
app.include_router(recommendations_router)