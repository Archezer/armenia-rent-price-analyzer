from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler,
)


CATEGORICAL_FEATURES = [
    "city",
    "district",
]


NUMERIC_FEATURES = [
    "rooms",
    "area_sqm",
    "floor",
    "total_floors",
]


def create_preprocessor() -> ColumnTransformer:
    """Create the shared preprocessing contract for model training and inference."""
    categorical_pipeline = Pipeline(
        steps=[
            (
                'imputer',
                SimpleImputer(
                    strategy='constant',
                    fill_value='Unknown'
                ),
            ),
            (
                'encoder',
                OneHotEncoder(
                    handle_unknown='ignore',
                    sparse_output=False
                )
            )
        ]
    )

    numeric_pipeline = Pipeline(
        steps=[
            (
                'imputer',
                SimpleImputer(
                    strategy='median',
                ),
            ),
            (
                'scaler',
                StandardScaler()
            )
        ]
    )

    return ColumnTransformer(
        transformers=[
            (
                'categorical',
                categorical_pipeline,
                CATEGORICAL_FEATURES
            ),
            (
                'numeric',
                numeric_pipeline,
                NUMERIC_FEATURES
            )
        ]
    )