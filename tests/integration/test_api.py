"""Integration tests for the public FastAPI contract."""

from collections.abc import Iterator

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sklearn.dummy import DummyRegressor
from sklearn.pipeline import Pipeline

import app.main as api_main
from price_analyzer.modeling.dataset import FEATURE_COLUMNS
from price_analyzer.modeling.persistence import (
    ModelMetadata,
    save_model_artifact,
)


@pytest.fixture
def client(tmp_path, monkeypatch) -> Iterator[TestClient]:
    """Create an API client backed by a temporary trusted artifact."""
    profiles = pd.DataFrame(
        {
            "city": ["Yerevan", "Yerevan", "Gyumri"],
            "district": ["Ajapnyak", "Arabkir", "Unknown"],
            "rooms": [2, 2, 1],
            "area_sqm": [50.0, 65.0, 45.0],
            "floor": [1, 3, 2],
            "total_floors": [5, 9, 5],
        }
    )

    model = Pipeline(
        steps=[
            (
                "regressor",
                DummyRegressor(
                    strategy="constant",
                    constant=250_000.4,
                ),
            )
        ]
    )
    model.fit(
        profiles[FEATURE_COLUMNS],
        [250_000.4] * len(profiles),
    )

    metadata = ModelMetadata(
        model_version="test-1.0.0",
        created_at_utc="2026-08-24T00:00:00+00:00",
        feature_columns=FEATURE_COLUMNS,
        target_column="price_amd",
        target_currency="AMD",
        dataset_rows=3,
        training_rows=2,
        test_rows=1,
        test_mae_amd=1.0,
        best_parameters={},
    )

    artifact_directory = tmp_path / "artifact"
    save_model_artifact(
        model,
        metadata,
        artifact_directory,
    )
    profiles.to_csv(
        artifact_directory / "candidate_profiles.csv",
        index=False,
    )

    monkeypatch.setattr(
        api_main,
        "get_artifact_directory",
        lambda: artifact_directory,
    )

    with TestClient(api_main.app) as test_client:
        yield test_client


def test_health_reports_loaded_model(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "model_version": "test-1.0.0",
    }


def test_predict_returns_rounded_amd_estimate(
    client: TestClient,
) -> None:
    response = client.post(
        "/predict",
        json={
            "city": "Yerevan",
            "district": "Arabkir",
            "rooms": 2,
            "area_sqm": 65.0,
            "floor": 3,
            "total_floors": 9,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "predicted_monthly_rent_amd": 250000,
        "currency": "AMD",
        "model_version": "test-1.0.0",
    }


def test_predict_rejects_invalid_floor(client: TestClient) -> None:
    response = client.post(
        "/predict",
        json={
            "city": "Yerevan",
            "district": "Arabkir",
            "rooms": 2,
            "area_sqm": 65.0,
            "floor": 10,
            "total_floors": 9,
        },
    )

    assert response.status_code == 422


def test_recommendations_return_matching_profiles(
    client: TestClient,
) -> None:
    response = client.post(
        "/recommendations",
        json={
            "city": "Yerevan",
            "rooms": 2,
            "limit": 5,
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["model_version"] == "test-1.0.0"
    assert len(payload["recommendations"]) == 2
    assert {
        item["district"]
        for item in payload["recommendations"]
    } == {"Ajapnyak", "Arabkir"}
    assert all(
        item["estimated_monthly_rent_amd"] == 250000
        for item in payload["recommendations"]
    )
