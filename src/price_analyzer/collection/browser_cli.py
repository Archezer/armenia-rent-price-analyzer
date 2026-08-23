"""Interactive smoke test using local Chromium."""

import argparse
from pathlib import Path

from .browser_client import BrowserFetchOptions, fetch_with_local_browser
from .list_am_client import ListAmClient
from .list_am_parser import parse_rental_listings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--output", type=Path, default=Path("data/raw"))
    parser.add_argument("--wait-seconds", type=float, default=8.0)
    parser.add_argument("--pages", type=int, default=1, help="Number of consecutive category pages")
    args = parser.parse_args()

    if args.pages < 1 or args.pages > 10:
        raise SystemExit("--pages must be between 1 and 10")

    for offset in range(args.pages):
        page_url = _page_url(args.url, offset)
        page = fetch_with_local_browser(
            page_url,
            BrowserFetchOptions(wait_seconds=args.wait_seconds, headless=False),
        )
        html_path, metadata_path = ListAmClient().save(page, args.output)
        listings = parse_rental_listings(
            page.html, source_url=page.url, retrieved_at=page.retrieved_at
        )
        print(f"Saved HTML: {html_path}")
        print(f"Saved metadata: {metadata_path}")
        print(f"Parsed listings: {len(listings)}")


def _page_url(url: str, offset: int) -> str:
    """Return consecutive category URLs without changing the search query."""
    if offset == 0:
        return url
    from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

    parts = urlsplit(url)
    segments = [segment for segment in parts.path.split("/") if segment]
    if segments and segments[-1].isdigit():
        segments[-1] = str(int(segments[-1]) + offset)
    else:
        segments.append(str(offset + 1))
    return urlunsplit((parts.scheme, parts.netloc, "/" + "/".join(segments), parts.query, parts.fragment))


if __name__ == "__main__":
    main()
