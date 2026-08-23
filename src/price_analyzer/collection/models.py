"""Normalized collection models."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class RentalListing:
    source: str
    source_url: str
    listing_id: str | None
    title: str
    price_amount: float
    currency: str
    price_period: str
    district: str | None
    rooms: int | None
    area_sqm: float | None
    floor: int | None
    total_floors: int | None
    retrieved_at: datetime
    raw_text: str
