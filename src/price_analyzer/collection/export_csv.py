"""Export parsed raw pages to a normalized CSV file."""

import csv
import json
from dataclasses import fields
from datetime import datetime
from pathlib import Path

from .list_am_parser import parse_rental_listings


def export_raw_directory(raw_directory: Path, output_csv: Path) -> int:
    """Parse saved HTML pages, deduplicate listings, and write a CSV."""
    rows = {}
    for html_path in sorted(raw_directory.glob("*.html")):
        metadata_path = html_path.with_suffix(".json")
        if not metadata_path.exists():
            continue
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        listings = parse_rental_listings(
            html_path.read_text(encoding="utf-8"),
            source_url=metadata["url"],
            retrieved_at=datetime.fromisoformat(metadata["retrieved_at"]),
        )
        for listing in listings:
            rows[listing.listing_id or listing.source_url] = listing

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [field.name for field in fields(next(iter(rows.values())))] if rows else []
    with output_csv.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if fieldnames:
            writer.writeheader()
            for listing in rows.values():
                writer.writerow({field: getattr(listing, field) for field in fieldnames})
    return len(rows)
