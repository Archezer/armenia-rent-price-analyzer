from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {
    'source',
    'source_url',
    'listing_id',
    'title',
    'price_amount',
    'currency',
    'price_period',
    'district',
    'rooms',
    'area_sqm',
    'floor',
    'total_floors',
    'retrieved_at',
}


REQUIRED_EXCHANGE_RATE_COLUMNS = {
    "currency",
    "requested_date",
    "rate_date",
    "rate_to_amd",
}


YEREVAN_DISTRICT_ALIASES = {
    "Kentron": "Kentron",
    "Կենտրոն": "Kentron",

    "Arabkir": "Arabkir",
    "Արաբկիր": "Arabkir",

    "Ajapnyak": "Ajapnyak",
    "Աջափնյակ": "Ajapnyak",

    "Avan": "Avan",
    "Ավան": "Avan",

    "Davtashen": "Davtashen",
    "Դավթաշեն": "Davtashen",

    "Erebuni": "Erebuni",
    "Էրեբունի": "Erebuni",

    "Kanaker-Zeytun": "Kanaker-Zeytun",
    "Քանաքեռ-Զեյթուն": "Kanaker-Zeytun",

    "Malatia-Sebastia": "Malatia-Sebastia",
    "Մալաթիա-Սեբաստիա": "Malatia-Sebastia",

    "Nor Nork": "Nor Nork",
    "Նոր Նորք": "Nor Nork",

    "Nork-Marash": "Nork-Marash",
    "Նորք-Մարաշ": "Nork-Marash",

    "Nubarashen": "Nubarashen",
    "Նուբարաշեն": "Nubarashen",

    "Shengavit": "Shengavit",
    "Շենգավիթ": "Shengavit",
}


CITY_ALIASES = {
    "Gyumri": "Gyumri",
    "Գյումրի": "Gyumri",

    "Hrazdan": "Hrazdan",
    "Հրազդան": "Hrazdan",

    "Vanadzor": "Vanadzor",
    "Վանաձոր": "Vanadzor",
}


SUPPORTED_CITIES = {
    "Yerevan",
    "Gyumri",
}


PUBLIC_EXCLUDED_COLUMNS = {
    "source_url",
    'raw_text'
}


def load_listings(input_path: Path) -> pd.DataFrame:
    """Load the raw listings CSV into a DataFrame."""
    return pd.read_csv(input_path)

def validate_columns(frame: pd.DataFrame) -> None:
    """Ensure that the input dataset has the required columns."""
    missing_columns = REQUIRED_COLUMNS - set(frame.columns)

    if missing_columns:
        raise ValueError(
            f"Input dataset is missing columns: {sorted(missing_columns)}"
        )

def add_city(frame: pd.DataFrame, city: str) -> pd.DataFrame:
    """Add the city label to every listing in one collection batch."""
    result = frame.copy()
    result['city'] = city
    return result

def find_missing_values(frame: pd.DataFrame) -> dict[str, int]:
    """Count missing values in every column."""
    missing_values = frame.isna().sum()
    return {
        column: int(count)
        for column, count in missing_values.items()
        if count > 0
    }

def convert_numeric_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Convert numeric listing fields to numeric pandas types."""
    result = frame.copy()

    numeric_columns = [
        "price_amount",
        "rooms",
        "area_sqm",
        "floor",
        "total_floors",
    ]

    for column in numeric_columns:
        result[column] = pd.to_numeric(
            result[column],
            errors='coerce'
        )

    return result

def convert_datetime_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Convert collection timestamps to timezone-aware datetimes."""
    result = frame.copy()

    result['retrieved_at'] = pd.to_datetime(
        result['retrieved_at'],
        errors='coerce',
        utc=True
    )

    return result

def find_invalid_values(frame: pd.DataFrame) -> dict[str, int]:
    """Count rows that violate basic domain constraints."""
    invalid_values: dict[str, int] = {}

    invalid_values["non_positive_price"] = int(
        (frame["price_amount"] <= 0).sum()
    )

    invalid_values["non_positive_area"] = int(
        (frame["area_sqm"] <= 0).sum()
    )

    invalid_values["non_positive_rooms"] = int(
        (frame["rooms"] <= 0).sum()
    )

    invalid_values["invalid_floor_relation"] = int(
        (frame["floor"] > frame["total_floors"]).sum()
    )

    invalid_values["non_monthly_period"] = int(
        (frame["price_period"] != "monthly").sum()
    )

    return {
        name: count
        for name, count in invalid_values.items()
        if count > 0
    }

def count_duplicate_listing_ids(frame: pd.DataFrame) -> int:
    """Count repeated listing IDs."""
    return int(
        frame.duplicated(
            subset=["listing_id"],
            keep="first",
        ).sum()
    )

def count_duplicate_urls(frame: pd.DataFrame) -> int:
    """Count repeated source URLs."""
    return int(
        frame.duplicated(
            subset=["source_url"],
            keep="first",
        ).sum()
    )

def print_category_summary(
    frame: pd.DataFrame,
    column: str,
) -> None:
    """Print value counts for one categorical column."""
    counts = frame[column].value_counts(
        dropna=False,
    )

    print(f"\n{column} distribution:")
    print(counts.to_string())

def find_suspicious_values(
    frame: pd.DataFrame,
) -> dict[str, int]:
    """Count plausible but suspicious values for manual review."""
    suspicious_values = {
        "very_small_area": int(
            (frame["area_sqm"] < 10).sum()
        ),
        "very_large_area": int(
            (frame["area_sqm"] > 500).sum()
        ),
        "many_rooms": int(
            (frame["rooms"] > 10).sum()
        ),
        "very_high_floor": int(
            (frame["floor"] > 50).sum()
        ),
        "very_low_price": int(
            (frame["price_amount"] < 100).sum()
        ),
    }

    return {
        name: count
        for name, count in suspicious_values.items()
        if count > 0
    }

def normalize_locations(
    frame: pd.DataFrame,
) -> pd.DataFrame:
    """Normalize city and district labels from List.am location values."""
    result = frame.copy()

    result["location_raw"] = (
        result["district"]
        .astype("string")
        .str.strip()
    )

    result["district"] = result["location_raw"].map(
        YEREVAN_DISTRICT_ALIASES
    )

    result["city"] = result["location_raw"].map(
        CITY_ALIASES
    )

    yerevan_mask = result["district"].notna()
    result.loc[yerevan_mask, "city"] = "Yerevan"

    return result

def find_unknown_districts(
    frame: pd.DataFrame,
) -> list[str]:
    """Return source district labels that are not recognized as Yerevan."""
    unknown_mask = frame["district"].isna()

    return sorted(
        frame.loc[unknown_mask, "district_raw"]
        .dropna()
        .unique()
        .tolist()
    )

def print_unknown_districts(
    frame: pd.DataFrame,
) -> None:
    """Print unrecognized district labels and their frequencies."""
    unknown_rows = frame.loc[
        frame["district"].isna(),
        ["district_raw", "title", "source_url"],
    ]

    if unknown_rows.empty:
        print("Unknown districts: none")
        return

    print("\nUnknown district labels:")
    print(
        unknown_rows["district_raw"]
        .value_counts(dropna=False)
        .to_string()
    )

    print("\nUnknown district examples:")
    print(
        unknown_rows.head(10).to_string(index=False)
    )

def split_by_market_scope(
    frame: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split listings into supported and unsupported city markets."""
    supported_mask = frame["city"].isin(
        SUPPORTED_CITIES
    )

    accepted = frame.loc[supported_mask].copy()
    rejected = frame.loc[~supported_mask].copy()

    return accepted, rejected

def validate_location_contract(
    frame: pd.DataFrame,
) -> dict[str, int]:
    """Validate city and district completeness by market."""
    problems = {
        "missing_city": int(
            frame["city"].isna().sum()
        ),
        "missing_yerevan_district": int(
            (
                frame["city"].eq("Yerevan")
                & frame["district"].isna()
            ).sum()
        ),
    }

    return {
        name: count
        for name, count in problems.items()
        if count > 0
    }

def add_rejection_reasons(
    frame: pd.DataFrame,
) -> pd.DataFrame:
    """Explain why listings are outside the supported market scope."""
    result = frame.copy()

    result["rejection_reason"] = "unsupported_city"

    result.loc[
        result["city"].isna(),
        "rejection_reason",
    ] = "unknown_location"

    return result

def save_validation_outputs(
    accepted: pd.DataFrame,
    rejected: pd.DataFrame,
    output_directory: Path,
) -> None:
    """Save accepted and rejected listings for audit."""
    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    accepted.to_csv(
        output_directory / "listings_accepted.csv",
        index=False,
    )

    rejected.to_csv(
        output_directory / "listings_rejected.csv",
        index=False,
    )

def build_public_dataset(
    frame: pd.DataFrame,
) -> pd.DataFrame:
    """Remove fields excluded from the publishable dataset."""
    missing_columns = (
        PUBLIC_EXCLUDED_COLUMNS
        - set(frame.columns)
    )

    if missing_columns:
        raise ValueError(
            "Cannot build public dataset because excluded "
            f"columns are missing: {sorted(missing_columns)}"
        )

    return frame.drop(
        columns=sorted(PUBLIC_EXCLUDED_COLUMNS)
    ).copy()

def save_public_dataset(
    frame: pd.DataFrame,
    output_path: Path,
) -> None:
    """Save the publication-safe dataset."""
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    frame.to_csv(
        output_path,
        index=False,
    )

def load_exchange_rates(
    input_path: Path,
) -> pd.DataFrame:
    """Load and validate the exchange-rate reference table."""
    rates = pd.read_csv(input_path)

    missing_columns = (
        REQUIRED_EXCHANGE_RATE_COLUMNS
        - set(rates.columns)
    )

    if missing_columns:
        raise ValueError(
            "Exchange-rate table is missing columns: "
            f"{sorted(missing_columns)}"
        )

    return rates

def prepare_exchange_rates(
    rates: pd.DataFrame,
) -> pd.DataFrame:
    """Prepare exchange rates for a many-to-one dataset join."""
    result = rates.copy()

    result["requested_date"] = pd.to_datetime(
        result["requested_date"],
        errors="coerce",
    ).dt.date

    result["rate_date"] = pd.to_datetime(
        result["rate_date"],
        errors="coerce",
    ).dt.date

    result["rate_to_amd"] = pd.to_numeric(
        result["rate_to_amd"],
        errors="coerce",
    )

    return result

def validate_exchange_rates(
    rates: pd.DataFrame,
) -> None:
    """Validate uniqueness and numeric integrity of exchange rates."""
    missing_values = rates[
        [
            "currency",
            "requested_date",
            "rate_date",
            "rate_to_amd",
        ]
    ].isna().sum()

    missing_values = missing_values[
        missing_values > 0
    ]

    if not missing_values.empty:
        raise ValueError(
            "Exchange-rate table contains missing values: "
            f"{missing_values.to_dict()}"
        )

    duplicate_keys = rates.duplicated(
        subset=[
            "currency",
            "requested_date",
        ],
        keep=False,
    )

    if duplicate_keys.any():
        duplicates = rates.loc[
            duplicate_keys,
            [
                "currency",
                "requested_date",
            ],
        ]

        raise ValueError(
            "Exchange-rate table contains duplicate keys: "
            f"{duplicates.to_dict(orient='records')}"
        )

    if (rates["rate_to_amd"] <= 0).any():
        raise ValueError(
            "Exchange rates must be positive"
        )

def normalize_prices_to_amd(
    frame: pd.DataFrame,
    rates: pd.DataFrame,
) -> pd.DataFrame:
    """Attach official rates and calculate monthly asking rent in AMD."""
    result = frame.copy()
    prepared_rates = rates.copy()

    result["exchange_rate_requested_date"] = (
        result["retrieved_at"].dt.date
    )

    prepared_rates = prepared_rates.rename(
        columns={
            "requested_date": "exchange_rate_requested_date",
            "rate_date": "exchange_rate_date",
            "rate_to_amd": "exchange_rate_to_amd",
        }
    )

    result = result.merge(
        prepared_rates[
            [
                "currency",
                "exchange_rate_requested_date",
                "exchange_rate_date",
                "exchange_rate_to_amd",
            ]
        ],
        on=[
            "currency",
            "exchange_rate_requested_date",
        ],
        how="left",
        validate="many_to_one",
    )

    missing_rate_mask = (
        result["exchange_rate_to_amd"].isna()
    )

    if missing_rate_mask.any():
        missing_keys = (
            result.loc[
                missing_rate_mask,
                [
                    "currency",
                    "exchange_rate_requested_date",
                ],
            ]
            .drop_duplicates()
            .to_dict(orient="records")
        )

        raise ValueError(
            "Missing exchange rates for: "
            f"{missing_keys}"
        )
    result["price_amd"] = (
        result["price_amount"]
        * result["exchange_rate_to_amd"]
    ).round(2)

    return result

def print_price_summary_by_city(
    frame: pd.DataFrame,
) -> None:
    """Print normalized asking-rent statistics by city."""
    summary = (
        frame.groupby("city")["price_amd"]
        .agg(
            count="count",
            minimum="min",
            median="median",
            mean="mean",
            maximum="max",
        )
        .round(2)
    )

    print("\nPrice summary by city, AMD:")
    print(summary.to_string())

def print_price_extremes(
    frame: pd.DataFrame,
    count: int = 5,
) -> None:
    """Print the lowest and highest normalized asking rents."""
    columns = [
        "listing_id",
        "city",
        "district",
        "rooms",
        "area_sqm",
        "price_amount",
        "currency",
        "price_amd",
    ]

    print("\nLowest prices:")
    print(
        frame.nsmallest(
            count,
            "price_amd",
        )[columns].to_string(index=False)
    )

    print("\nHighest prices:")
    print(
        frame.nlargest(
            count,
            "price_amd",
        )[columns].to_string(index=False)
    )

if __name__ == "__main__":
    input_path = Path("data/processed/listings.csv")

    listings = load_listings(input_path)
    validate_columns(listings)

    listings = normalize_locations(listings)

    accepted_listings, rejected_listings = split_by_market_scope(
        listings
    )

    location_problems = validate_location_contract(
    accepted_listings
    )

    if location_problems:
        print(f"Location problems: {location_problems}")
    else:
        print("Location problems: none")

    listings = accepted_listings

    rejected_listings = add_rejection_reasons(rejected_listings)

    listings = convert_numeric_columns(listings)
    listings = convert_datetime_columns(listings)

    exchange_rates = load_exchange_rates(
        Path("data/reference/exchange_rates.csv")
    )

    exchange_rates = prepare_exchange_rates(
        exchange_rates
    )

    validate_exchange_rates(
        exchange_rates
    )

    listings = normalize_prices_to_amd(
        listings,
        exchange_rates,
    )

    print_price_summary_by_city(listings)

    public_listings = build_public_dataset(listings)

    save_public_dataset(
        public_listings,
        Path("data/public/listings.csv"),
    )

    print(f"Public rows: {len(public_listings)}")
    print(f"Public columns: {list(public_listings.columns)}")
    print("Public dataset saved to data/public/listings.csv")

    missing_values = find_missing_values(listings)
    invalid_values = find_invalid_values(listings)

    duplicate_listing_ids = count_duplicate_listing_ids(listings)
    duplicate_urls = count_duplicate_urls(listings)
    suspicious_values = find_suspicious_values(listings)

    print(f"Accepted rows: {len(accepted_listings)}")
    print(f"Rejected rows: {len(rejected_listings)}")

    print_category_summary(
        accepted_listings,
        "city",
    )

    if not rejected_listings.empty:
        print("\nRejected city distribution:")
        print(
            rejected_listings["city"]
            .value_counts(dropna=False)
            .to_string()
        )

    save_validation_outputs(
        accepted=accepted_listings,
        rejected=rejected_listings,
        output_directory=Path("data/validated"),
    )

    print(
    "Validated datasets saved to data/validated"
)

    print(
        listings[
            [
                "price_amount",
                "currency",
                "exchange_rate_to_amd",
                "price_amd",
            ]
        ].head(10)
    )