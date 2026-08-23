import pandas as pd

from price_analyzer.data.clean_listings import (
    normalize_locations,
    split_by_market_scope,
)


def test_normalize_locations_maps_language_aliases() -> None:
    frame = pd.DataFrame(
        {
            "district": [
                "Կենտրոն",
                "Kentron",
                "Գյումրի",
                "Gyumri",
                "Hrazdan",
            ]
        }
    )

    result = normalize_locations(frame)

    assert result["city"].tolist() == [
        "Yerevan",
        "Yerevan",
        "Gyumri",
        "Gyumri",
        "Hrazdan",
    ]

    assert result["district"].iloc[0] == "Kentron"
    assert result["district"].iloc[1] == "Kentron"

    assert pd.isna(
        result["district"].iloc[2]
    )

def test_split_by_market_scope_rejects_unsupported_cities() -> None:
    frame = pd.DataFrame(
        {
            "city": [
                "Yerevan",
                "Gyumri",
                "Hrazdan",
                "Vanadzor",
            ]
        }
    )

    accepted, rejected = split_by_market_scope(
        frame
    )

    assert accepted["city"].tolist() == [
        "Yerevan",
        "Gyumri",
    ]

    assert rejected["city"].tolist() == [
        "Hrazdan",
        "Vanadzor",
    ]