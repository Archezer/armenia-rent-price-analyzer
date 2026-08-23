from pathlib import Path

import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split


FEATURE_COLUMNS = [
    "district",
    "rooms",
    "area_sqm",
    "floor",
    "total_floors",
]

TARGET_COLUMN = 'price_amd'
RANDOM_SEED = 42


def load_modeling_dataset(
        input_path: Path
) -> pd.DataFrame:
    """Load the prepared modeling dataset."""
    frame = pd.read_csv(
        input_path,
        parse_dates=['retrieved_at']
    )
    required_columns = (
        set(FEATURE_COLUMNS)
        | {TARGET_COLUMN}
    )

    missing_columns = (
        required_columns
        - set(frame.columns)
    )

    if missing_columns:
        raise ValueError(
            "Modeling dataset is missing columns: "
            f"{sorted(missing_columns)}"
        )

    return frame

def split_dataset(
        frame: pd.DataFrame
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame
]:
    """Create deterministic train, validation, and test datasets."""
    train_validation, test = train_test_split(
        frame,
        test_size=0.20,
        random_state=RANDOM_SEED,
    )

    train, validation = train_test_split(
        train_validation,
        test_size=0.25,
        random_state=RANDOM_SEED,
    )

    return train, validation, test

