import os
from pathlib import Path


DEFAULT_ARTIFACT_DIRECTORY = (
    "artifacts/rent_model_v1"
)


def get_artifact_directory() -> Path:
    """Return the model-artifact directory."""
    return Path(
        os.getenv(
            "MODEL_ARTIFACT_DIRECTORY",
            DEFAULT_ARTIFACT_DIRECTORY,
        )
    )