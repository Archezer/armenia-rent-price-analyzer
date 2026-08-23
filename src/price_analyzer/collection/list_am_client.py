"""Shared page and public-URL validation for collection transports."""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True, slots=True)
class RawPage:
    url: str
    retrieved_at: datetime
    content_type: str
    sha256: str
    html: str


class ListAmClient:
    """Utilities shared by direct and local-browser collection."""

    @staticmethod
    def _validate_public_url(url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.netloc.lower() not in {"list.am", "www.list.am"}:
            raise ValueError("Only public HTTPS pages on www.list.am are supported")
        if parsed.path.lower().startswith(("/login", "/logout", "/add", "/edit", "/srv", "/xlink")):
            raise ValueError("Authenticated, editing, service, and internal URLs are not supported")

    def save(self, page: RawPage, directory: Path) -> tuple[Path, Path]:
        directory.mkdir(parents=True, exist_ok=True)
        stem = page.sha256[:16]
        html_path = directory / f"{stem}.html"
        metadata_path = directory / f"{stem}.json"
        html_path.write_text(page.html, encoding="utf-8")
        metadata_path.write_text(
            json.dumps(
                {"url": page.url, "retrieved_at": page.retrieved_at.isoformat(),
                 "content_type": page.content_type, "sha256": page.sha256},
                ensure_ascii=False, indent=2,
            ) + "\n",
            encoding="utf-8",
        )
        return html_path, metadata_path
