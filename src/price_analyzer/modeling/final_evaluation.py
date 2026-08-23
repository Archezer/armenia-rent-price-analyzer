from pathlib import Path

import pandas as pd

from price_analyzer.modeling.dataset import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    load_modeling_dataset,
    split_dataset,
)
from price_analyzer.modeling.random_forest import (
    calculate_mae,
    create_random_forest_pipeline,
)

BEST_PARAMETERS = {
    "max_depth": None,
    "min_samples_leaf": 2,
    "max_features": 0.47513963344019094,
}


def main() -> None:
    """Fit the selected model and evaluate it once on test data."""
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

    test_mae = calculate_mae(model, test)

    print(
        "Train and validation rows: "
        f"{len(train_and_validation)}"
    )
    print(f"Reserved test rows: {len(test)}")
    print(f"Final test MAE: {test_mae:,.2f} AMD")


if __name__ == "__main__":
    main()