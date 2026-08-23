from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "listing_id",
    "city",
    "district",
    "rooms",
    "area_sqm",
    "floor",
    "total_floors",
    "retrieved_at",
    "price_amd",
}


MODELING_COLUMNS = [
    "listing_id",
    "city",
    "district",
    "rooms",
    "area_sqm",
    "floor",
    "total_floors",
    "retrieved_at",
    "price_amd",
]


def load_public_dataset(
    input_path: Path,
) -> pd.DataFrame:
    """Load and validate the public listings dataset."""
    frame = pd.read_csv(
        input_path,
        parse_dates=["retrieved_at"],
    )

    missing_columns = (
        REQUIRED_COLUMNS
        - set(frame.columns)
    )

    if missing_columns:
        raise ValueError(
            "Public dataset is missing columns: "
            f"{sorted(missing_columns)}"
        )

    return frame


def prepare_modeling_dataset(
    frame: pd.DataFrame,
) -> pd.DataFrame:
    """Prepare supported-city listings for model training."""
    result = frame.copy()

    supported_cities = {
        "Yerevan",
        "Gyumri",
    }

    unexpected_cities = (
        set(result["city"])
        - supported_cities
    )

    if unexpected_cities:
        raise ValueError(
            "Modeling dataset contains unsupported cities: "
            f"{sorted(unexpected_cities)}"
        )

    result["district"] = (
        result["district"]
        .fillna("Unknown")
    )

    return result[MODELING_COLUMNS].copy()


def main() -> None:
    input_path = Path(
        "data/public/listings.csv"
    )

    output_path = Path(
        "data/modeling/listings_multicity.csv"
    )

    public_listings = load_public_dataset(
        input_path
    )

    modeling_listings = prepare_modeling_dataset(
        public_listings
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    modeling_listings.to_csv(
        output_path,
        index=False,
    )

    print(
        f"Modeling rows: "
        f"{len(modeling_listings)}"
    )

    print(
        "City distribution:"
    )

    print(
        modeling_listings["city"]
        .value_counts()
        .to_string()
    )

    print(
        f"Saved: {output_path}"
    )


if __name__ == "__main__":
    main()