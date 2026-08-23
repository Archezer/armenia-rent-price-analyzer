"""Local browser transport for authorized public List.am pages."""

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256

from .list_am_client import RawPage, ListAmClient


@dataclass(frozen=True, slots=True)
class BrowserFetchOptions:
    """Interactive browser options; CAPTCHA, if shown, remains a human step."""

    wait_seconds: float = 8.0
    headless: bool = False


def fetch_with_local_browser(url: str, options: BrowserFetchOptions | None = None) -> RawPage:
    """Fetch one page with local Chromium and return its rendered HTML."""
    options = options or BrowserFetchOptions()
    ListAmClient._validate_public_url(url)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as error:
        raise RuntimeError(
            "Playwright is not installed. Install project dependencies and run "
            '`playwright install chromium`.'
        ) from error

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=options.headless)
        page = browser.new_page(
            locale="en-US",
            user_agent="armenian-price-parser/0.1 (authorized educational project)",
        )
        page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        page.wait_for_timeout(int(options.wait_seconds * 1000))
        if not options.headless:
            input("If a browser challenge is visible, complete it manually, then press Enter here... ")
        html = page.content()
        browser.close()

    content = html.encode("utf-8")
    return RawPage(
        url=url,
        retrieved_at=datetime.now(timezone.utc),
        content_type="text/html; charset=utf-8",
        sha256=sha256(content).hexdigest(),
        html=html,
    )
