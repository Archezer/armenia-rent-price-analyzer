import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd
from sklearn.pipeline import Pipeline

from price_analyzer.inference.recommendations import (
    RecommendationFilters,
    load_candidate_profiles,
    recommend_lowest_rent,
)
from price_analyzer.modeling.dataset import (
    FEATURE_COLUMNS,
)


@dataclass(frozen=True, slots=True)
class RentInferenceService:
    """Serve predictions from one trusted model artifact."""

    model: Pipeline
    model_version: str
    candidate_profiles: pd.DataFrame

    @classmethod
    def load(
        cls,
        artifact_directory: Path,
    ) -> "RentInferenceService":
        """Load a trusted local artifact and its profiles."""
        model_path = artifact_directory / "model.joblib"
        metadata_path = artifact_directory / "metadata.json"
        profiles_path = (
            artifact_directory
            / "candidate_profiles.csv"
        )

        missing_paths = [
            path
            for path in [
                model_path,
                metadata_path,
                profiles_path,
            ]
            if not path.exists()
        ]

        if missing_paths:
            missing_names = ", ".join(
                path.name
                for path in missing_paths
            )
            raise FileNotFoundError(
                "Model artifact is incomplete: "
                f"{missing_names}"
            )

        metadata = json.loads(
            metadata_path.read_text(
                encoding="utf-8",
            )
        )

        return cls(
            model=joblib.load(model_path),
            model_version=metadata["model_version"],
            candidate_profiles=load_candidate_profiles(
                profiles_path
            ),
        )

    def predict(
        self,
        features: Mapping[str, object],
    ) -> float:
        """Predict monthly rent in AMD for one apartment."""
        feature_frame = pd.DataFrame(
            [features],
            columns=FEATURE_COLUMNS,
        )

        return float(
            self.model.predict(feature_frame)[0]
        )

    def recommend(
        self,
        filters: RecommendationFilters,
    ) -> pd.DataFrame:
        """Return lowest predicted-rent matching profiles."""
        return recommend_lowest_rent(
            self.model,
            self.candidate_profiles,
            filters,
        )