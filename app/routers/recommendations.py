from fastapi import APIRouter

from app.dependencies import InferenceService
from app.schemas import (
    RecommendationItem,
    RecommendationRequest,
    RecommendationResponse,
)
from price_analyzer.inference.recommendations import (
    PREDICTION_COLUMN,
    RecommendationFilters,
)


router = APIRouter(tags=["recommendations"])


@router.post(
    "/recommendations",
    response_model=RecommendationResponse,
)
def recommendations(
    payload: RecommendationRequest,
    service: InferenceService,
) -> RecommendationResponse:
    """Return lowest estimated-rent matching profiles."""
    filters = RecommendationFilters(
        city=payload.city,
        district=payload.district,
        rooms=payload.rooms,
        min_area_sqm=payload.min_area_sqm,
        max_area_sqm=payload.max_area_sqm,
        max_budget_amd=payload.max_budget_amd,
        limit=payload.limit,
    )

    recommendation_frame = service.recommend(
        filters
    )

    items = [
        RecommendationItem(
            city=row.city,
            district=row.district,
            rooms=row.rooms,
            area_sqm=row.area_sqm,
            floor=row.floor,
            total_floors=row.total_floors,
            estimated_monthly_rent_amd=round(
                getattr(
                    row,
                    PREDICTION_COLUMN,
                )
            ),
            currency="AMD",
        )
        for row in recommendation_frame.itertuples(
            index=False
        )
    ]

    return RecommendationResponse(
        model_version=service.model_version,
        recommendations=items,
    )
