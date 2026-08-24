from typing import Annotated

from fastapi import Depends, Request

from price_analyzer.inference.service import(
    RentInferenceService
)


def get_inference_service(
        request: Request,
) -> RentInferenceService:
    return request.app.state.inference_service


InferenceService = Annotated[
    RentInferenceService,
    Depends(get_inference_service)
]