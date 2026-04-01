# --- STAGE 1: Builder ---
FROM python:3.11-slim AS builder

ENV POETRY_VERSION=2.3.2 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root --no-ansi

# --- STAGE 2: Runtime ---
FROM python:3.11-slim AS runtime

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

COPY provider-service/ /app/provider-service/

ENV PYTHONPATH=/app/provider-service

WORKDIR /app/provider-service

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]