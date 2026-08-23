"""Command-line CSV export for saved raw pages."""

import argparse
from pathlib import Path

from .export_csv import export_raw_directory


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, default=Path("data/raw"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/listings.csv"))
    args = parser.parse_args()
    count = export_raw_directory(args.raw, args.output)
    print(f"Exported unique listings: {count}")
    print(f"CSV: {args.output}")


if __name__ == "__main__":
    main()
