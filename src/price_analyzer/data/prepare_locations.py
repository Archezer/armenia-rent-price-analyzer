from pathlib import Path

from .clean_listings import (
    add_rejection_reasons,
    load_listings,
    normalize_locations,
    split_by_market_scope,
    validate_columns,
)


def main() -> None:
    listings = load_listings(
        Path("data/processed/listings.csv")
    )

    validate_columns(listings)

    listings = normalize_locations(
        listings
    )

    accepted, rejected = split_by_market_scope(
        listings
    )

    rejected = add_rejection_reasons(
        rejected
    )

    output_directory = Path("data/interim")
    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    accepted.to_csv(
        output_directory
        / "listings_location_accepted.csv",
        index=False,
    )

    rejected.to_csv(
        output_directory
        / "listings_location_rejected.csv",
        index=False,
    )

    print(f"Input rows: {len(listings)}")
    print(f"Accepted rows: {len(accepted)}")
    print(f"Rejected rows: {len(rejected)}")

    print("\nAccepted city distribution:")
    print(
        accepted["city"]
        .value_counts(dropna=False)
        .to_string()
    )

    print("\nRejected city distribution:")
    print(
        rejected["city"]
        .value_counts(dropna=False)
        .to_string()
    )


if __name__ == "__main__":
    main()