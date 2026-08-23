from pathlib import Path

import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error

from .dataset import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    load_modeling_dataset,
    split_dataset,
)


def train_global_median_baseline(
    train: pd.DataFrame,
) -> DummyRegressor:
    """Fit a baseline that predicts one global median price."""
    model = DummyRegressor(
        strategy="median",
    )

    model.fit(
        train[FEATURE_COLUMNS],
        train[TARGET_COLUMN],
    )

    return model

def calculate_mae(
    model: DummyRegressor,
    dataset: pd.DataFrame,
) -> float:
    """Calculate mean absolute error in AMD."""
    predictions = model.predict(
        dataset[FEATURE_COLUMNS]
    )

    return float(
        mean_absolute_error(
            dataset[TARGET_COLUMN],
            predictions,
        )
    )

def train_city_median_baseline(
    train: pd.DataFrame,
) -> tuple[pd.Series, float]:
    """Calculate one median target value for each city."""
    city_medians = (
        train.groupby("city")[TARGET_COLUMN]
        .median()
    )

    global_median = float(
        train[TARGET_COLUMN].median()
    )

    return city_medians, global_median

def predict_city_median(
    dataset: pd.DataFrame,
    city_medians: pd.Series,
    fallback_prediction: float,
) -> pd.Series:
    """Predict each listing with its city's training median."""
    predictions = dataset["city"].map(
        city_medians
    )

    return predictions.fillna(
        fallback_prediction
    )

def calculate_city_median_mae(
    train: pd.DataFrame,
    validation: pd.DataFrame,
) -> tuple[float, pd.Series]:
    """Evaluate the city-aware median baseline."""
    city_medians, global_median = (
        train_city_median_baseline(train)
    )

    predictions = predict_city_median(
        validation,
        city_medians,
        global_median,
    )

    mae = mean_absolute_error(
        validation[TARGET_COLUMN],
        predictions,
    )

    return float(mae), city_medians


def main() -> None:
    dataset = load_modeling_dataset(
        Path(
            "data/modeling/listings_multicity.csv"
        )
    )

    train, validation, test = split_dataset(
        dataset
    )

    baseline = train_global_median_baseline(
        train
    )

    validation_mae = calculate_mae(
        baseline,
        validation,
    )

    city_median_mae, city_medians = (
        calculate_city_median_mae(
            train,
            validation,
        )
    )

    predicted_price = float(
        baseline.constant_.item()
    )

    print(f"Dataset rows: {len(dataset)}")
    print(f"Train rows: {len(train)}")
    print(f"Validation rows: {len(validation)}")
    print(f"Reserved test rows: {len(test)}")

    print(
        f"Global median prediction: "
        f"{predicted_price:,.2f} AMD"
    )

    print(
            f"Validation MAE: "
            f"{validation_mae:,.2f} AMD"
        )

    print("\nCity median predictions:")
    print(city_medians.to_string())

    print(
        f"City median validation MAE: "
        f"{city_median_mae:,.2f} AMD"
    )

    


if __name__ == "__main__":
    main()