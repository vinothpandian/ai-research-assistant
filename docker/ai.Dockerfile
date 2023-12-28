FROM python:3.11-slim as base

ENV POETRY_VERSION=1.4.2 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  build-essential \
  gcc

RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

WORKDIR /app

COPY core ./core
COPY pyproject.toml poetry.lock ./
COPY .env ./.env

RUN poetry install --only core --no-root


FROM base as ai

ARG APP_NAME
ENV PATH="/app/.venv/bin:$PATH"

RUN poetry install --only ai,core-api --no-root

WORKDIR /app

COPY ai ./ai

ENV APP ai.$APP_NAME:app

CMD uvicorn $APP --proxy-headers --host 0.0.0.0 --port 80




