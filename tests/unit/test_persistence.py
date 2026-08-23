import json

import joblib
from sklearn.dummy import DummyRegressor
from sklearn.pipeline import Pipeline

from price_analyzer.modeling.persistence import (
    ModelMetadata,
    save_model_artifact,
)


def test_save_model_artifact_writes_loadable_model_and_metadata(
    tmp_path,
) -> None:
    model = Pipeline(
        steps=[
            (
                "regressor",
                DummyRegressor(strategy="mean"),
            )
        ]
    )
    model.fit([[1.0], [3.0]], [100.0, 300.0])

    metadata = ModelMetadata(
        model_version="1.0.0",
        created_at_utc="2026-08-23T00:00:00+00:00",
        feature_columns=["area_sqm"],
        target_column="price_amd",
        target_currency="AMD",
        dataset_rows=582,
        training_rows=465,
        test_rows=117,
        test_mae_amd=79_208.43,
        best_parameters={
            "min_samples_leaf": 2,
            "max_depth": None,
        },
    )

    model_path, metadata_path = save_model_artifact(
        model,
        metadata,
        tmp_path / "artifact",
    )

    loaded_model = joblib.load(model_path)
    saved_metadata = json.loads(
        metadata_path.read_text(encoding="utf-8")
    )

    assert loaded_model.predict([[2.0]]).tolist() == [200.0]
    assert saved_metadata["model_version"] == "1.0.0"
    assert saved_metadata["test_mae_amd"] == 79_208.43
    assert saved_metadata["best_parameters"] == {
        "min_samples_leaf": 2,
        "max_depth": None,
    }
