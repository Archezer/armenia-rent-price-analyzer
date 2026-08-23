import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from xml.etree import ElementTree

import requests

CBA_API_URL = "https://api.cba.am/exchangerates.asmx"


@dataclass(frozen=True, slots=True)
class ExchangeRate:
    currency: str
    requested_date: date
    rate_date: date
    currency_amount: float
    rate_amd: float

    @property
    def rate_to_amd(self) -> float:
        return self.rate_amd / self.currency_amount

def fetch_exchange_rate(
    currency: str,
    rate_date: date,
) -> ExchangeRate:
    """Fetch one official exchange rate from the Central Bank of Armenia."""
    envelope = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <ExchangeRatesByDateByISO xmlns="http://www.cba.am/">
            <date>{rate_date.isoformat()}</date>
            <ISO>{currency}</ISO>
        </ExchangeRatesByDateByISO>
    </soap:Body>
</soap:Envelope>"""

    response = requests.post(
        CBA_API_URL,
        data=envelope.encode("utf-8"),
        headers={
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://www.cba.am/ExchangeRatesByDateByISO",
            "User-Agent": "armenian-price-parser/0.1",
        },
        timeout=20,
    )

    response.raise_for_status()

    return parse_exchange_rate_response(
        response.content,
        requested_date=rate_date,
    )

def parse_exchange_rate_response(
    xml_content: bytes,
    *,
    requested_date: date,
) -> ExchangeRate:
    """Parse one CBA exchange-rate SOAP response."""
    root = ElementTree.fromstring(xml_content)

    currency = _find_xml_text(root, "ISO")
    amount = _find_xml_text(root, "Amount")
    rate = _find_xml_text(root, "Rate")
    current_date = _find_xml_text(root, "CurrentDate")

    return ExchangeRate(
        currency=currency,
        requested_date=requested_date,
        rate_date=date.fromisoformat(
            current_date[:10]
        ),
        currency_amount=float(amount),
        rate_amd=float(rate),
    )

def _find_xml_text(
    root: ElementTree.Element,
    local_name: str,
) -> str:
    """Find required XML text regardless of namespace prefix."""
    suffix = f"}}{local_name}"

    for element in root.iter():
        if (
            element.tag == local_name
            or element.tag.endswith(suffix)
        ) and element.text:
            return element.text.strip()

    raise ValueError(
        f"CBA response does not contain {local_name}"
    )

def create_amd_rate(
    requested_date: date,
) -> ExchangeRate:
    """Create the identity exchange rate for AMD."""
    return ExchangeRate(
        currency="AMD",
        requested_date=requested_date,
        rate_date=requested_date,
        currency_amount=1.0,
        rate_amd=1.0,
    )

def save_exchange_rates(
    rates: list[ExchangeRate],
    output_path: Path,
) -> None:
    """Save exchange rates used by the dataset pipeline."""
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "currency",
                "requested_date",
                "rate_date",
                "currency_amount",
                "rate_amd",
                "rate_to_amd",
                "source",
            ],
        )

        writer.writeheader()

        for rate in rates:
            writer.writerow(
                {
                    "currency": rate.currency,
                    "requested_date": rate.requested_date.isoformat(),
                    "rate_date": rate.rate_date.isoformat(),
                    "currency_amount": rate.currency_amount,
                    "rate_amd": rate.rate_amd,
                    "rate_to_amd": rate.rate_to_amd,
                    "source": "Central Bank of Armenia",
                }
            )

if __name__ == "__main__":
    collection_dates = [
        date(2026, 8, 19),
        date(2026, 8, 23),
    ]

    rates: list[ExchangeRate] = []

    for collection_date in collection_dates:
        rates.extend(
            [
                create_amd_rate(collection_date),
                fetch_exchange_rate(
                    "USD",
                    collection_date,
                ),
                fetch_exchange_rate(
                    "EUR",
                    collection_date,
                ),
            ]
        )

    save_exchange_rates(
        rates,
        Path("data/reference/exchange_rates.csv"),
    )