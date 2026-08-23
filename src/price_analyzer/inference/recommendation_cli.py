import argparse
from pathlib import Path

import joblib

from .recommendations import (
    RecommendationFilters,
    load_candidate_profiles,
    recommend_lowest_rent,
)

DEFAULT_MODEL_PATH = Path(
    "artifacts/rent_model_v1/model.joblib"
)
DEFAULT_PROFILES_PATH = Path(
    "artifacts/rent_model_v1/"
    "candidate_profiles.csv"
)


def main() -> None:
    """Load the trusted artifact and print recommendations."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--city",
        required=True,
    )
    parser.add_argument("--district")
    parser.add_argument(
        "--rooms",
        type=int,
    )
    parser.add_argument(
        "--min-area-sqm",
        type=float,
    )
    parser.add_argument(
        "--max-area-sqm",
        type=float,
    )
    parser.add_argument(
        "--max-budget-amd",
        type=float,
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
    )

    args = parser.parse_args()

    model = joblib.load(DEFAULT_MODEL_PATH)
    profiles = load_candidate_profiles(
        DEFAULT_PROFILES_PATH
    )

    filters = RecommendationFilters(
        city=args.city,
        district=args.district,
        rooms=args.rooms,
        min_area_sqm=args.min_area_sqm,
        max_area_sqm=args.max_area_sqm,
        max_budget_amd=args.max_budget_amd,
        limit=args.limit,
    )

    recommendations = recommend_lowest_rent(
        model,
        profiles,
        filters,
    )

    if recommendations.empty:
        print("No matching candidate profiles found.")
        return

    print(
        recommendations.to_string(
            index=False,
        )
    )


if __name__ == "__main__":
    main()