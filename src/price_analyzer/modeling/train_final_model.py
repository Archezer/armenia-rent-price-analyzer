from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from price_analyzer.modeling.dataset import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    load_modeling_dataset,
    split_dataset,
)
from price_analyzer.modeling.persistence import (
    ModelMetadata,
    save_model_artifact,
)
from price_analyzer.modeling.random_forest import (
    create_random_forest_pipeline,
)

MODEL_VERSION = "1.0.0"
FINAL_TEST_MAE_AMD = 79_208.43
ARTIFACT_DIRECTORY = Path("artifacts/rent_model_v1")

BEST_PARAMETERS = {
    "max_depth": None,
    "min_samples_leaf": 2,
    "max_features": 0.47513963344019094,
}


def main() -> None:
    """Train the selected model and save its artifact."""
    listings = load_modeling_dataset(
        Path("data/modeling/listings_multicity.csv")
    )
    train, validation, test = split_dataset(listings)

    train_and_validation = pd.concat(
        [train, validation],
        ignore_index=True,
    )

    model = create_random_forest_pipeline(
        **BEST_PARAMETERS,
    )
    model.fit(
        train_and_validation[FEATURE_COLUMNS],
        train_and_validation[TARGET_COLUMN],
    )

    metadata = ModelMetadata(
        model_version=MODEL_VERSION,
        created_at_utc=datetime.now(
            timezone.utc,
        ).isoformat(),
        feature_columns=FEATURE_COLUMNS,
        target_column=TARGET_COLUMN,
        target_currency="AMD",
        dataset_rows=len(listings),
        training_rows=len(train_and_validation),
        test_rows=len(test),
        test_mae_amd=FINAL_TEST_MAE_AMD,
        best_parameters=BEST_PARAMETERS,
    )

    model_path, metadata_path = save_model_artifact(
        model,
        metadata,
        ARTIFACT_DIRECTORY,
    )

    candidate_profiles = (
        train_and_validation[FEATURE_COLUMNS]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    profiles_path = (
        ARTIFACT_DIRECTORY
        / "candidate_profiles.csv"
    )
    candidate_profiles.to_csv(
        profiles_path,
        index=False,
    )

    print(f"Saved model: {model_path}")
    print(f"Saved metadata: {metadata_path}")
    print(
        "Saved recommendation profiles: "
        f"{profiles_path}"
    )


if __name__ == "__main__":
    main()