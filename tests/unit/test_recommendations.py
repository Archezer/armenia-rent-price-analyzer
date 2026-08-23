import pandas as pd
import pytest

from price_analyzer.inference.recommendations import (
    PREDICTION_COLUMN,
    RecommendationFilters,
    recommend_lowest_rent,
)


class AreaPriceModel:
    """Predict rent from area for deterministic recommendation tests."""

    def predict(self, features: pd.DataFrame) -> pd.Series:
        return features["area_sqm"] * 1_000


def build_profiles() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "city": [
                "Yerevan",
                "Yerevan",
                "Yerevan",
                "Gyumri",
            ],
            "district": [
                "Ajapnyak",
                "Arabkir",
                "Kentron",
                "Unknown",
            ],
            "rooms": [2, 2, 1, 2],
            "area_sqm": [60.0, 50.0, 80.0, 45.0],
            "floor": [3, 1, 5, 2],
            "total_floors": [4, 5, 9, 5],
        }
    )


def test_recommendations_apply_filters_and_sort_by_price() -> None:
    recommendations = recommend_lowest_rent(
        AreaPriceModel(),
        build_profiles(),
        RecommendationFilters(
            city="Yerevan",
            rooms=2,
            min_area_sqm=45.0,
            max_area_sqm=65.0,
            max_budget_amd=60_000.0,
            limit=2,
        ),
    )

    assert recommendations["district"].tolist() == [
        "Arabkir",
        "Ajapnyak",
    ]
    assert recommendations[PREDICTION_COLUMN].tolist() == [
        50_000.0,
        60_000.0,
    ]


def test_recommendations_return_empty_frame_without_matching_city() -> None:
    recommendations = recommend_lowest_rent(
        AreaPriceModel(),
        build_profiles(),
        RecommendationFilters(city="Vanadzor"),
    )

    assert recommendations.empty
    assert PREDICTION_COLUMN in recommendations.columns


def test_recommendations_reject_nonpositive_limit() -> None:
    with pytest.raises(
        ValueError,
        match="limit must be positive",
    ):
        recommend_lowest_rent(
            AreaPriceModel(),
            build_profiles(),
            RecommendationFilters(
                city="Yerevan",
                limit=0,
            ),
        )


def test_recommendations_reject_inverted_area_range() -> None:
    with pytest.raises(
        ValueError,
        match="Minimum area cannot exceed",
    ):
        recommend_lowest_rent(
            AreaPriceModel(),
            build_profiles(),
            RecommendationFilters(
                city="Yerevan",
                min_area_sqm=70.0,
                max_area_sqm=50.0,
            ),
        )
