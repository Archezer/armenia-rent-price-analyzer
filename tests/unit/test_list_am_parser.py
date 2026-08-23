from datetime import datetime, timezone

from price_analyzer.collection.list_am_parser import (
    parse_rental_listings,
)


def test_parse_english_rental_card() -> None:
    html = """
    <a
        href="/en/item/123456?ld_src=2"
        data-testid="favorite-ad-card-123456"
    >
        <div class="p">$1,000 monthly</div>
        <div class="l">
            2 room apartment in Arabkir
        </div>
        <div class="at">
            Arabkir, 2 rm., 60 sq.m., 3/9 floor
        </div>
    </a>
    """

    retrieved_at = datetime(
        2026,
        8,
        23,
        tzinfo=timezone.utc,
    )

    listings = parse_rental_listings(
        html,
        source_url=(
            "https://www.list.am/en/category/56"
        ),
        retrieved_at=retrieved_at,
    )

    assert len(listings) == 1

    listing = listings[0]

    assert listing.listing_id == "123456"
    assert listing.price_amount == 1000.0
    assert listing.currency == "USD"
    assert listing.price_period == "monthly"
    assert listing.district == "Arabkir"
    assert listing.rooms == 2
    assert listing.area_sqm == 60.0
    assert listing.floor == 3
    assert listing.total_floors == 9


def test_parse_armenian_rental_card() -> None:
    html = """
    <a
        href="/item/654321?ld_src=2"
        data-testid="favorite-ad-card-654321"
    >
        <div class="p">
            250,000 ֏ ամսական
        </div>
        <div class="l">
            3 սենյականոց բնակարան կենտրոնում
        </div>
        <div class="at">
            Կենտրոն, 3 սեն., 85 քմ, 4/5 հարկ
        </div>
    </a>
    """

    retrieved_at = datetime(
        2026,
        8,
        23,
        tzinfo=timezone.utc,
    )

    listings = parse_rental_listings(
        html,
        source_url=(
            "https://www.list.am/category/56"
        ),
        retrieved_at=retrieved_at,
    )

    assert len(listings) == 1

    listing = listings[0]

    assert listing.listing_id == "654321"
    assert listing.price_amount == 250000.0
    assert listing.currency == "AMD"
    assert listing.price_period == "monthly"
    assert listing.district == "Կենտրոն"
    assert listing.rooms == 3
    assert listing.area_sqm == 85.0
    assert listing.floor == 4
    assert listing.total_floors == 5