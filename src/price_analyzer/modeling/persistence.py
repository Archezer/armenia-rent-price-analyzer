"""Persistence utilities for trusted model artifacts."""

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import joblib
from sklearn.pipeline import Pipeline


@dataclass(frozen=True, slots=True)
class ModelMetadata:
    """Describe one trained model artifact."""

    model_version: str
    created_at_utc: str
    feature_columns: list[str]
    target_column: str
    target_currency: str
    dataset_rows: int
    training_rows: int
    test_rows: int
    test_mae_amd: float
    best_parameters: dict[str, int | float | None]


def save_model_artifact(
    model: Pipeline,
    metadata: ModelMetadata,
    artifact_directory: Path,
) -> tuple[Path, Path]:
    """Save a trusted fitted pipeline and its JSON metadata."""
    artifact_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_path = artifact_directory / "model.joblib"
    metadata_path = artifact_directory / "metadata.json"

    joblib.dump(model, model_path)

    metadata_path.write_text(
        json.dumps(
            asdict(metadata),
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    return model_path, metadata_path