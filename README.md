# Yerevan Rent Estimator

Yerevan Rent Estimator is a learning-focused, production-minded machine-learning
service for estimating the monthly asking rent of long-term apartments in Yerevan,
Armenia. The project covers the path from lawful data collection and validation to a
versioned model artifact and a typed FastAPI inference endpoint.

> **Project status:** collection prototype. An authorized local-browser collector can
> save rendered public List.am pages with provenance metadata. CSV normalization,
> training, and the prediction API are not implemented yet.

## Problem statement

Given the characteristics of an apartment listing, estimate the monthly price at which
a comparable long-term apartment is advertised in Yerevan.

The target is **monthly asking rent**, not the final price of a signed lease. Listing
prices can be stale, negotiable, duplicated, or inaccurate, so predictions must be
presented as market estimates with documented uncertainty.

The first version will use Armenian dram (`AMD`) as its canonical currency and focus on
one city to avoid pretending that sparse observations from different Armenian housing
markets are interchangeable.

## Learning goals

This project develops practical AI engineering skills:

- converting external data into a validated, traceable dataset;
- parsing HTML safely and testing parsers against local fixtures;
- handling numeric, categorical, geographic, and temporal features;
- detecting duplicates, relisted apartments, currency errors, and outliers;
- preventing leakage with grouped, time-aware data splits;
- fitting preprocessing and regression in one scikit-learn pipeline;
- comparing a transparent baseline with stronger candidate models;
- serializing the complete fitted pipeline with model metadata;
- running inference outside Jupyter notebooks;
- exposing stable request and response contracts with FastAPI and Pydantic;
- testing data, model, artifact, and HTTP boundaries.

## System flow

```text
permitted source / official API / local HTML fixtures
    |
    v
fetching and HTML parsing
    |
    v
schema validation and provenance metadata
    |
    v
currency normalization and duplicate detection
    |
    v
grouped, time-aware train / validation / test split
    |
    v
scikit-learn preprocessing + regression pipeline
    |
    v
evaluation and versioned artifact
    |
    v
FastAPI: POST /predict
```

Fetching and parsing are deliberately separate. A parser consumes stored HTML and can
therefore be tested without repeatedly contacting a third-party service.

## Data collection laboratory

The repository includes an educational collection laboratory covering HTTP clients,
local browser rendering, DOM selectors, pagination, rate limiting, provenance, schema
drift, and fixture-based parser tests.

The current successful target is:

```text
https://www.list.am/en/category/56?q=yerevan
```

The first saved page contained roughly 96 listing cards. A second page was collected
from `https://www.list.am/category/56/2?q=yerevan` and contained roughly 103 unique
listing IDs. Available fields include listing ID and URL, price, currency, monthly
period, district, rooms, area in square metres, floor, total floors, title, and some
optional descriptive flags.

The browser collector saves rendered HTML and a JSON sidecar with URL, retrieval time,
content type, and SHA-256 hash. Raw pages may contain analytics or IP data and must
not be committed or published. The normalized CSV must retain only modeling fields
and necessary provenance.

Run a bounded collection with:

```powershell
$env:PYTHONPATH = "src"
uv run playwright install chromium
uv run python -m price_analyzer.collection.browser_cli `
  "https://www.list.am/category/56/3?q=yerevan" `
  --pages 3 --output data/raw
```

If a browser challenge appears, it may only be completed manually under the written
project authorization. The code must not automate CAPTCHA solving or extract tokens.

Educational or non-commercial use does not automatically permit automated access.
Booking.com explicitly prohibits scraping its live platform without prior express
permission. Consequently, this project will not crawl Booking.com pages or attempt to
evade bot controls. Booking-style extraction will be learned using synthetic or locally
stored HTML fixtures. Authorized real Booking data may be explored through the official
[Booking.com Demand API](https://developers.booking.com/demand/docs/getting-started/overview).

Booking prices describe short-term accommodation for specific dates, guests, inventory,
fees, and cancellation terms. They are not labels for the long-term-rent model. A future
temporary-stay estimator may use them as a separate dataset and product.

Any real long-term-rental source must be reviewed for:

- terms of service and automated-access rules;
- API or export availability;
- copyright and dataset licensing;
- personal information and redistribution constraints;
- stable identifiers and collection provenance.

Raw third-party pages and datasets will not be committed unless their license clearly
allows redistribution.

## Intended feature contract

The final schema will follow the selected dataset. An illustrative request is:

```json
{
  "district": "Arabkir",
  "area_sqm": 62.0,
  "rooms": 2,
  "floor": 5,
  "total_floors": 12,
  "building_type": "new_construction",
  "renovation_condition": "modern",
  "furnished": true,
  "listing_date": "2026-08-19"
}
```

Illustrative response:

```json
{
  "estimated_monthly_rent": 280000.0,
  "likely_range": {
    "lower": 245000.0,
    "upper": 325000.0
  },
  "currency": "AMD",
  "market": "Yerevan long-term rental listings",
  "model_version": "0.1.0"
}
```

The uncertainty range is a product requirement, although the exact interval method
will be chosen only after a trustworthy baseline exists.

Planned endpoints:

- `GET /health` reports application and artifact readiness.
- `POST /predict` validates apartment characteristics and returns one rent estimate.

## Evaluation strategy

Random row splitting is unsafe for marketplace listings. The same apartment can be
posted repeatedly or by multiple agencies, allowing near-duplicates to appear on both
sides of a naive split. The project will group probable duplicates and evaluate on a
later time period.

| Split | Purpose |
|---|---|
| Train | Fit preprocessing statistics and model parameters on earlier listings. |
| Validation | Compare approaches and make tuning decisions. |
| Test | Evaluate once on the latest held-out period. |

Mean absolute error (`MAE`) in AMD is the planned primary metric. Results will also be
broken down by district and price segment so an acceptable global score cannot hide
systematic failures. A median-rent baseline must be established before complex models
are introduced.

## Planned project structure

```text
.
|-- app/                              # FastAPI transport and lifecycle
|-- src/price_analyzer/
|   |-- collection/                   # permitted clients and HTML parsers
|   |-- data/                         # validation and dataset construction
|   |-- features/                     # preprocessing definitions
|   |-- modeling/                     # training, evaluation, persistence
|   `-- inference/                    # framework-independent prediction
|-- tests/
|   |-- fixtures/html/                # synthetic or authorized HTML samples
|   |-- unit/
|   `-- integration/
|-- data/                             # local data; not automatically distributable
|-- artifacts/                        # generated pipelines and metadata
|-- AGENTS.md                         # engineering and teaching rules
|-- pyproject.toml
`-- README.md
```

Directories will be added with working vertical slices rather than as empty
placeholders.

## Initial implementation plan

1. Define the listing schema, target semantics, supported cities, and data-quality
   rules.
2. Build synthetic Booking-like HTML fixtures and a pure, tested listing parser.
3. Add a permitted-source HTTP client and local-browser transport with timeouts,
   conservative rate limits, provenance metadata, and raw-response size limits.
4. Obtain a lawful long-term-rental dataset and create a reproducible dataset snapshot.
5. Normalize currencies and categories, then detect duplicate or relisted apartments.
6. Create grouped, time-aware train, validation, and test sets.
7. Train a median baseline and a scikit-learn preprocessing/regression pipeline.
8. Evaluate overall, by district, and by price segment; add an uncertainty strategy.
9. Serialize the fitted pipeline and metadata, then implement framework-independent
   inference.
10. Add FastAPI `/health` and `/predict`, integration tests, and verified run commands.

## Development

The repository requires Python 3.12 or newer and uses `pyproject.toml` for package
metadata. The browser command is a raw-page smoke test; deterministic parsing and CSV
export remain separate steps.

## Public web application

The backend is a Dockerized FastAPI service deployed independently from the browser
client. The React frontend lives in [`frontend/`](frontend/), calls the public API, and
is built as static files for GitHub Pages. Its deployment workflow is
[`deploy-frontend.yml`](.github/workflows/deploy-frontend.yml). The API must allow the
Pages origin through `CORS_ALLOWED_ORIGINS`; this is required because the browser client
and API use different domains.

## Market scope: Yerevan and Gyumri

The first baseline should remain Yerevan-only. Gyumri can be added later, but every
record must include an explicit `city` field and evaluation must be reported by city.
Otherwise the model may learn an unobserved market difference and produce misleading
errors. The recommended experiment is one multi-city model with `city` as a categorical
feature, compared against a Yerevan-only baseline. Separate city models are an option
only if each city has enough observations.

## Limitations and ethics

- Predictions represent advertised prices, not completed rental transactions.
- Market coverage will initially be limited to Yerevan and the collection period.
- Duplicate, fraudulent, stale, and selectively advertised listings can bias results.
- Exact addresses, contact information, cookies, and account data are unnecessary for
  the model and must not be collected.
- A prediction is not a guaranteed rent, appraisal, or financial recommendation.
- Model and dataset documentation must disclose source, license, dates, exclusions,
  exchange-rate policy, and known gaps.

## Contributing

This is an educational project. Changes should remain small, testable, and consistent
with [`AGENTS.md`](AGENTS.md). Source code, API contracts, documentation, tests, and
commit messages are written in professional English for an international audience;
teaching explanations may be provided in Russian.

## License

No code license has been selected. Until a license file is added, reuse and
redistribution rights should not be assumed. Third-party data remains governed by its
own terms regardless of the future code license.
