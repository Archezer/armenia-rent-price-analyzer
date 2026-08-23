"""Recommendation logic based on predicted rent."""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sklearn.pipeline import Pipeline

from price_analyzer.modeling.dataset import (
    FEATURE_COLUMNS,
)


PREDICTION_COLUMN = (
    "estimated_monthly_rent_amd"
)


@dataclass(frozen=True, slots=True)
class RecommendationFilters:
    """Optional constraints for rent recommendations."""

    city: str
    district: str | None = None
    rooms: int | None = None
    min_area_sqm: float | None = None
    max_area_sqm: float | None = None
    max_budget_amd: float | None = None
    limit: int = 5


def load_candidate_profiles(
    profiles_path: Path,
) -> pd.DataFrame:
    """Load feature-only profiles used as recommendation candidates."""
    return pd.read_csv(profiles_path)


def recommend_lowest_rent(
    model: Pipeline,
    profiles: pd.DataFrame,
    filters: RecommendationFilters,
) -> pd.DataFrame:
    """Return the lowest estimated-rent profiles matching constraints."""
    if filters.limit < 1:
        raise ValueError(
            "Recommendation limit must be positive"
        )

    if (
        filters.min_area_sqm is not None
        and filters.max_area_sqm is not None
        and filters.min_area_sqm > filters.max_area_sqm
    ):
        raise ValueError(
            "Minimum area cannot exceed maximum area"
        )

    candidates = profiles.copy()

    candidates = candidates[
        candidates["city"].eq(filters.city)
    ]

    if filters.district is not None:
        candidates = candidates[
            candidates["district"].eq(
                filters.district
            )
        ]

    if filters.rooms is not None:
        candidates = candidates[
            candidates["rooms"].eq(filters.rooms)
        ]

    if filters.min_area_sqm is not None:
        candidates = candidates[
            candidates["area_sqm"].ge(
                filters.min_area_sqm
            )
        ]

    if filters.max_area_sqm is not None:
        candidates = candidates[
            candidates["area_sqm"].le(
                filters.max_area_sqm
            )
        ]

    if candidates.empty:
        candidates[PREDICTION_COLUMN] = pd.Series(
            dtype="float64"
        )
        return candidates

    candidates[PREDICTION_COLUMN] = model.predict(
        candidates[FEATURE_COLUMNS]
    )

    if filters.max_budget_amd is not None:
        candidates = candidates[
            candidates[PREDICTION_COLUMN].le(
                filters.max_budget_amd
            )
        ]

    return (
        candidates.sort_values(PREDICTION_COLUMN)
        .head(filters.limit)
        .reset_index(drop=True)
    )
