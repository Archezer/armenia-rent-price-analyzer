from pathlib import Path

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import Pipeline

from price_analyzer.features.preprocessing import (
    create_preprocessor,
)
from price_analyzer.modeling.dataset import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    load_modeling_dataset,
    split_dataset,
)

DEFAULT_N_ESTIMATORS = 200
DEFAULT_MIN_SAMPLES_LEAF = 3
RANDOM_SEED = 42


def create_random_forest_pipeline(
    n_estimators: int = DEFAULT_N_ESTIMATORS,
    max_depth: int | None = None,
    min_samples_leaf: int = DEFAULT_MIN_SAMPLES_LEAF,
    max_features: float = 1.0,
) -> Pipeline:
    """Create a configurable random-forest pipeline."""
    return Pipeline(
        steps=[
            ("preprocessor", create_preprocessor()),
            (
                "regressor",
                RandomForestRegressor(
                    n_estimators=n_estimators,
                    max_depth=max_depth,
                    min_samples_leaf=min_samples_leaf,
                    max_features=max_features,
                    random_state=RANDOM_SEED,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def calculate_mae(
    model: Pipeline,
    dataset,
) -> float:
    """Calculate MAE on a dataset split."""
    predictions = model.predict(dataset[FEATURE_COLUMNS])

    return mean_absolute_error(
        dataset[TARGET_COLUMN],
        predictions,
    )


def main() -> None:
    """Train and validate the first random-forest candidate."""
    dataset_path = Path(
        "data/modeling/listings_multicity.csv"
    )
    listings = load_modeling_dataset(dataset_path)
    train, validation, test = split_dataset(listings)

    model = create_random_forest_pipeline()
    model.fit(
        train[FEATURE_COLUMNS],
        train[TARGET_COLUMN],
    )

    validation_mae = calculate_mae(model, validation)

    print(f"Dataset rows: {len(listings)}")
    print(f"Train rows: {len(train)}")
    print(f"Validation rows: {len(validation)}")
    print(f"Reserved test rows: {len(test)}")
    print(
        "Random forest validation MAE: "
        f"{validation_mae:,.2f} AMD"
    )


if __name__ == "__main__":
    main()