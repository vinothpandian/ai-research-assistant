FROM python:3.11-slim-bookworm as base

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

WORKDIR /src

COPY core ./core
COPY pyproject.toml poetry.lock ./

RUN poetry install --only core --no-root


FROM base as api

ENV PATH="/src/.venv/bin:$PATH"

RUN poetry install --only core-api,api --no-root

WORKDIR /src

COPY api ./api
COPY config.yaml ./config.yaml

CMD uvicorn api.main:app --proxy-headers --host 0.0.0.0 --port 8000


