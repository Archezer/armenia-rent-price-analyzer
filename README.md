# Armenian Rent Price Analyzer

A full-stack machine-learning project that estimates the monthly asking rent of a
long-term apartment in Armenia. The model uses structured listing attributes and
returns estimates in Armenian dram (AMD).

**Live application:** [archezer.github.io/armenia-rent-price-analyzer](https://archezer.github.io/armenia-rent-price-analyzer/)

**API documentation:** [armenian-rent-estimator-api.onrender.com/docs](https://armenian-rent-estimator-api.onrender.com/docs)

## What the application does

The public interface provides two functions:

1. **Rent estimate** — predicts monthly asking rent for an apartment using city,
   district, room count, area, floor, and total floors.
2. **Lowest estimates** — returns the lowest model-estimated apartment profiles that
   match optional filters such as city, rooms, area, and maximum budget.

The result is an estimate of an advertised long-term rent, not a property appraisal,
guaranteed price, or financial recommendation.

## Architecture

```text
Public React application
GitHub Pages
https://archezer.github.io/armenia-rent-price-analyzer/
             |
             | HTTPS JSON requests
             v
FastAPI inference service
Render + Docker
https://armenian-rent-estimator-api.onrender.com
             |
             v
Serialized scikit-learn pipeline
Random forest + fitted preprocessing
```

The frontend contains no dataset or trained model. It is a static Vite/React build
published through GitHub Actions. The API image trains the model from the sanitized
public dataset during its Docker build, persists the artifact inside the image, and
loads it once when the service starts.

## Model and evaluation

The model is a scikit-learn `Pipeline` containing:

- a `ColumnTransformer` that preprocesses numeric and categorical features;
- categorical encoding with safe handling for categories not seen during training;
- a `RandomForestRegressor` selected after validation and Optuna hyperparameter search.

| Item | Value |
|---|---:|
| Model version | `1.0.0` |
| Dataset rows | 582 |
| Train rows | 348 |
| Validation rows | 117 |
| Reserved test rows | 117 |
| Final test MAE | 79,208.43 AMD |

MAE (*mean absolute error*) means that, on the reserved test set, the average absolute
difference between the predicted and listed monthly price was about 79 thousand AMD.
The test set was kept separate from hyperparameter selection; it is reported as a final
evaluation, not used to choose a better model.

### Input features

```text
city, district, rooms, area_sqm, floor, total_floors
```

The target is `price_amd`: monthly listing price normalized to AMD.

## Data

The public dataset is [`data/public/listings.csv`](data/public/listings.csv). It has
582 sanitized rental-listing records:

| City | Records |
|---|---:|
| Yerevan | 396 |
| Gyumri | 186 |

Raw HTML, original page URLs, listing text, and generated training artifacts are
excluded from Git. The collection work was performed for the student project with
written permission from the source. The collector does not bypass CAPTCHA, rate limits,
or other access controls; a visible browser challenge must be completed manually when
authorized.

## API

The FastAPI service exposes:

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Confirms that the service and model are ready. |
| `POST` | `/predict` | Returns one estimated monthly rent. |
| `POST` | `/recommendations` | Returns low-estimate profiles matching filters. |

Example prediction request:

```json
{
  "city": "Yerevan",
  "district": "Kentron",
  "rooms": 2,
  "area_sqm": 60,
  "floor": 3,
  "total_floors": 9
}
```

Example response:

```json
{
  "predicted_monthly_rent_amd": 421517,
  "currency": "AMD",
  "model_version": "1.0.0"
}
```

Request validation is implemented with Pydantic. For example, an apartment floor cannot
be greater than the building's `total_floors`; malformed input receives a standard HTTP
validation error instead of reaching the model.

## Local development

### Backend

Requirements: Python 3.12+, [uv](https://docs.astral.sh/uv/), and Docker for the
containerized run.

Install dependencies and run tests:

```powershell
uv sync
uv run pytest -q
```

Build and run the complete reproducible API image:

```powershell
docker build -t armenian-rent-estimator .
docker run --rm -p 8000:8000 armenian-rent-estimator
```

Then open `http://localhost:8000/docs`.

### Frontend

Requirements: Node.js 22+ and pnpm 11+.

```powershell
cd frontend
pnpm install
pnpm run lint
pnpm run dev
```

Vite serves the application at
`http://localhost:5173/armenia-rent-price-analyzer/`. The public API URL is configured
through `VITE_API_BASE_URL`; see [`frontend/.env.example`](frontend/.env.example).

Create an optimized static build with:

```powershell
pnpm run build
```

## Deployment

- The backend is deployed to Render from [`Dockerfile`](Dockerfile) and
  [`render.yaml`](render.yaml).
- The frontend is built and deployed to GitHub Pages by
  [`.github/workflows/deploy-frontend.yml`](.github/workflows/deploy-frontend.yml) on
  every push to `master` that changes frontend files.
- Render must set `CORS_ALLOWED_ORIGINS=https://archezer.github.io` so browsers may make
  requests from the Pages origin. The path is not part of a CORS origin.

## Project structure

```text
app/                         FastAPI application, routes, schemas, configuration
src/price_analyzer/
  collection/                Permitted collection and HTML parsing utilities
  data/                      Dataset cleaning and validation
  features/                  Preprocessing definition
  inference/                 Framework-independent prediction and recommendations
  modeling/                  Training, evaluation, and artifact persistence
data/public/listings.csv     Sanitized publishable dataset
frontend/                    Vite + React client
tests/                       Unit and integration tests
Dockerfile                   Reproducible backend image
render.yaml                  Render deployment specification
```

## Limitations and responsible use

- The dataset is small and covers only the observed listing period and locations.
- Prices are advertised asking rents, which may be stale, duplicated, negotiable, or
  inaccurate.
- The model has no exact address, condition, renovation, furnishing, photo, or building
  features, so it cannot capture every property difference.
- Results should be used for education and rough market exploration only.
- The repository has no code license yet; reuse and redistribution rights should not be
  assumed. Third-party data remains subject to its own terms.

## Verification

The latest local verification completed successfully:

```text
15 passed, 8 warnings
```

The warnings originate in third-party testing and serialization dependencies; the test
suite itself passed. It covers parsing, data/model artifact persistence, recommendations,
API validation, health readiness, and CORS preflight behavior.
