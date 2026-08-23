from pathlib import Path

import optuna
from optuna.samplers import TPESampler

from price_analyzer.modeling.dataset import (
    load_modeling_dataset,
    split_dataset,
)
from price_analyzer.modeling.random_forest import (
    calculate_mae,
    create_random_forest_pipeline,
)

N_TRIALS = 25
RANDOM_SEED = 42


def objective(
    trial: optuna.Trial,
    train,
    validation,
) -> float:
    """Train one candidate and return its validation MAE."""
    model = create_random_forest_pipeline(
        max_depth=trial.suggest_categorical(
            "max_depth",
            [None, 4, 6, 8, 10, 12],
        ),
        min_samples_leaf=trial.suggest_int(
            "min_samples_leaf",
            1,
            10,
        ),
        max_features=trial.suggest_float(
            "max_features",
            0.4,
            1.0,
        ),
    )

    model.fit(
        train[
            [
                "city",
                "district",
                "rooms",
                "area_sqm",
                "floor",
                "total_floors",
            ]
        ],
        train["price_amd"],
    )

    return calculate_mae(model, validation)


def main() -> None:
    """Optimize random-forest hyperparameters on validation MAE."""
    listings = load_modeling_dataset(
        Path("data/modeling/listings_multicity.csv")
    )
    train, validation, _ = split_dataset(listings)

    study = optuna.create_study(
        direction="minimize",
        sampler=TPESampler(seed=RANDOM_SEED),
    )
    study.optimize(
        lambda trial: objective(trial, train, validation),
        n_trials=N_TRIALS,
    )

    print(f"Best validation MAE: {study.best_value:,.2f} AMD")
    print(f"Best parameters: {study.best_params}")


if __name__ == "__main__":
    main()