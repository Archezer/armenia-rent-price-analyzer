"""Parse rendered List.am rental category pages."""

import re
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from .models import RentalListing

_PRICE_PATTERNS = (
    re.compile(r"(?P<amount>[\d\s,]+)\s*(?P<symbol>֏|\$|€)"),
    re.compile(r"(?P<symbol>֏|\$|€)\s*(?P<amount>[\d\s,]+)"),
)
_EN_DETAILS_RE = re.compile(
    r"(?P<district>[^,]+),\s*(?P<rooms>\d+)\s*rm\.,\s*"
    r"(?P<area>[\d.,]+)\s*sq\.\s*m\.(?:,\s*(?P<floor>\d+)\s*/\s*(?P<total>\d+)\s*floor)?",
    re.IGNORECASE,
)
_HY_DETAILS_RE = re.compile(
    r"(?P<district>[^,]+),\s*(?P<rooms>\d+)\s*սեն\.,\s*"
    r"(?P<area>[\d.,]+)\s*քմ(?:,\s*(?P<floor>\d+)\s*/\s*(?P<total>\d+)\s*հարկ)?"
)
_CURRENCY = {"֏": "AMD", "$": "USD", "€": "EUR"}


def parse_rental_listings(html: str, *, source_url: str, retrieved_at: datetime) -> list[RentalListing]:
    """Extract normalized rental listings from one rendered category page."""
    soup = BeautifulSoup(html, "html.parser")
    listings: list[RentalListing] = []
    for card in soup.select('a[data-testid^="favorite-ad-card-"]'):
        listing = _parse_card(card, source_url=source_url, retrieved_at=retrieved_at)
        if listing is not None:
            listings.append(listing)
    return listings


def _parse_card(card: Tag, *, source_url: str, retrieved_at: datetime) -> RentalListing | None:
    price_text = _text(card.select_one(".p"))
    title = _text(card.select_one(".l"))
    details = _text(card.select_one(".at"))
    link = card.get("href")
    if not price_text or not title or not details or not link:
        return None

    price_match = next(
        (pattern.search(price_text) for pattern in _PRICE_PATTERNS if pattern.search(price_text)),
        None,
    )
    details_match = _EN_DETAILS_RE.search(details) or _HY_DETAILS_RE.search(details)
    if not price_match or not details_match:
        return None

    test_id = str(card.get("data-testid", ""))
    listing_id = test_id.removeprefix("favorite-ad-card-") or None
    return RentalListing(
        source="list.am",
        source_url=urljoin(source_url, link),
        listing_id=listing_id,
        title=title,
        price_amount=_parse_number(price_match.group("amount")),
        currency=_CURRENCY[price_match.group("symbol")],
        price_period="monthly" if "monthly" in price_text.lower() or "ամսական" in price_text.lower() else "unknown",
        district=details_match.group("district").strip(),
        rooms=int(details_match.group("rooms")),
        area_sqm=_parse_number(details_match.group("area")),
        floor=_optional_int(details_match.group("floor")),
        total_floors=_optional_int(details_match.group("total")),
        retrieved_at=retrieved_at,
        raw_text=" ".join(card.stripped_strings),
    )


def _text(element: Tag | None) -> str:
    return element.get_text(" ", strip=True) if element else ""


def _parse_number(value: str) -> float:
    return float(value.replace(" ", "").replace(",", ""))


def _optional_int(value: str | None) -> int | None:
    return int(value) if value else None
