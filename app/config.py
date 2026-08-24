import os
from pathlib import Path


DEFAULT_ARTIFACT_DIRECTORY = (
    "artifacts/rent_model_v1"
)

DEFAULT_CORS_ALLOWED_ORIGINS = (
    "http://localhost:5173",
)


def get_artifact_directory() -> Path:
    """Return the model-artifact directory."""
    return Path(
        os.getenv(
            "MODEL_ARTIFACT_DIRECTORY",
            DEFAULT_ARTIFACT_DIRECTORY,
        )
    )

def get_cors_allowed_origins() -> list[str]:
    """Return explicitly allowed browser origins."""
    raw_origins = os.getenv(
        "CORS_ALLOWED_ORIGINS"
    )

    if raw_origins is None:
        return list(
            DEFAULT_CORS_ALLOWED_ORIGINS
        )

    origins = [
        origin.strip().rstrip("/")
        for origin in raw_origins.split(",")
        if origin.strip()
    ]

    if not origins:
        raise ValueError(
            "CORS_ALLOWED_ORIGINS cannot be empty"
        )

    return origins