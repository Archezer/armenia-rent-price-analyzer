from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import (
    get_artifact_directory,
    get_cors_allowed_origins,
)
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_allowed_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
    max_age=600,
)

app.include_router(health_router)
app.include_router(predictions_router)
app.include_router(recommendations_router)