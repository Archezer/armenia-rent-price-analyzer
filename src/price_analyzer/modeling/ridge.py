from pathlib import Path

import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import Pipeline

from price_analyzer.features.preprocessing import (
    create_preprocessor,
)

from .dataset import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    load_modeling_dataset,
    split_dataset,
)

DEFAULT_ALPHA = 1.0

CANDIDATE_ALPHAS = [
    0.01,
    0.1,
    1.0,
    10.0,
    100.0,
    1000.0,
]


def create_ridge_pipeline(
    alpha: float = DEFAULT_ALPHA,
) -> Pipeline:
    """Create an unfitted preprocessing and Ridge regression pipeline."""
    return Pipeline(
        steps=[
            (
                "preprocessor",
                create_preprocessor(),
            ),
            (
                "regressor",
                Ridge(alpha=alpha),
            ),
        ]
    )

def train_ridge_model(
    train: pd.DataFrame,
    alpha: float = DEFAULT_ALPHA,
) -> Pipeline:
    """Fit the preprocessing and Ridge regression pipeline."""
    model = create_ridge_pipeline(
        alpha=alpha,
    )

    model.fit(
        train[FEATURE_COLUMNS],
        train[TARGET_COLUMN],
    )

    return model

def calculate_mae(
    model: Pipeline,
    dataset: pd.DataFrame,
) -> float:
    """Calculate MAE in AMD for an unseen dataset."""
    predictions = model.predict(
        dataset[FEATURE_COLUMNS]
    )

    return float(
        mean_absolute_error(
            dataset[TARGET_COLUMN],
            predictions,
        )
    )

def evaluate_alpha(
    train: pd.DataFrame,
    validation: pd.DataFrame,
    alpha: float,
) -> float:
    """Train one Ridge model and return its validation MAE."""
    model = train_ridge_model(
        train,
        alpha=alpha,
    )

    return calculate_mae(
        model,
        validation,
    )

def select_alpha(
    train: pd.DataFrame,
    validation: pd.DataFrame,
) -> tuple[float, dict[float, float]]:
    """Choose the alpha with the lowest validation MAE."""
    results: dict[float, float] = {}

    for alpha in CANDIDATE_ALPHAS:
        results[alpha] = evaluate_alpha(
            train,
            validation,
            alpha,
        )

    best_alpha = min(
        results,
        key=results.get,
    )

    return best_alpha, results

def main() -> None:
    """Run the first Ridge regression experiment."""
    dataset = load_modeling_dataset(
        Path(
            "data/modeling/listings_multicity.csv"
        )
    )

    train, validation, test = split_dataset(
        dataset
    )

    best_alpha, alpha_results = select_alpha(
        train,
        validation,
    )

    model = train_ridge_model(
        train,
        alpha=best_alpha,
    )

    validation_mae = calculate_mae(
        model,
        validation,
    )

    print(f"Dataset rows: {len(dataset)}")
    print(f"Train rows: {len(train)}")
    print(f"Validation rows: {len(validation)}")
    print(f"Reserved test rows: {len(test)}")
    print("\nRidge alpha results:")

    for alpha, mae in alpha_results.items():
        print(
            f"alpha={alpha:>7}: "
            f"MAE={mae:,.2f} AMD"
        )

    print(
        f"\nSelected alpha: {best_alpha}"
    )
    print(f"Selected Ridge alpha: {best_alpha}")
    print(
        f"Ridge validation MAE: "
        f"{validation_mae:,.2f} AMD"
    )


if __name__ == "__main__":
    main()