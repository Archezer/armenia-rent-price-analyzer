# Armenian Rent Estimator frontend

This React and Vite single-page application is the public browser client for the
FastAPI service. It provides a monthly-rent estimate and low-estimate apartment
profiles. The frontend contains no model, dataset, or credentials.

## Local development

From this directory, install dependencies and start Vite:

```powershell
pnpm install
pnpm run dev
```

Vite serves the application at `/armenia-rent-price-analyzer/`, matching the GitHub Pages
repository path. Copy `.env.example` to `.env.local` to override the public API URL
for local development. `.env.local` is intentionally ignored by Git.

## Build and checks

```powershell
pnpm run lint
pnpm run build
```

`pnpm run build` type-checks the TypeScript code and creates static files in `dist/`.
The generated directory is not committed.

## Deployment

`.github/workflows/deploy-frontend.yml` builds `dist/` after a push to `master` and
publishes it with GitHub Pages. The deployed frontend requires the FastAPI service to
allow `https://archezer.github.io` through its `CORS_ALLOWED_ORIGINS` setting.
