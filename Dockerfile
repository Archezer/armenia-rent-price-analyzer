FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.5 \
    /uv /uvx /bin/

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV UV_NO_DEV=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PATH="/app/.venv/bin:$PATH"
ENV MODEL_ARTIFACT_DIRECTORY=\
/app/artifacts/rent_model_v1
ENV PORT=8000

COPY pyproject.toml uv.lock ./

RUN uv sync \
    --locked \
    --no-install-project \
    --no-editable

COPY README.md ./
COPY app ./app
COPY src ./src
COPY data/public ./data/public

RUN uv sync --locked --no-editable

RUN python -m \
    price_analyzer.data.prepare_modeling_dataset

RUN python -m \
    price_analyzer.modeling.train_final_model

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s \
    --start-period=15s --retries=3 \
    CMD python -c "\
import urllib.request; \
urllib.request.urlopen(\
'http://127.0.0.1:8000/health'\
)"

CMD [ \
"sh", \
"-c", \
"uvicorn app.main:app --host 0.0.0.0 --port ${PORT}" \
]