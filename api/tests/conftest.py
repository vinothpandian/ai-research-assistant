import logging
from typing import Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from core.lib.db import ArticleDB
from core.lib.vector_db import VectorDB

from ..dependencies import get_articles_db, get_vector_db
from ..main import app

pocketbase_db = MagicMock(name="ArticleDB", spec=ArticleDB)
qdrant_db = MagicMock(name="VectorDB", spec=VectorDB)


def override_get_articles_db():
    yield pocketbase_db


def override_get_vector_db():
    yield qdrant_db


app.dependency_overrides[get_articles_db] = override_get_articles_db  # type: ignore
app.dependency_overrides[get_vector_db] = override_get_vector_db  # type: ignore


@pytest.fixture(scope="session")
def api_client():
    client = TestClient(app)
    yield client


@pytest.fixture(scope="session")
def articles_db() -> Generator[ArticleDB, None, None]:
    yield pocketbase_db


@pytest.fixture(scope="session")
def vector_db() -> Generator[VectorDB, None, None]:
    yield qdrant_db


# suppress DeprecationWarning
logging.getLogger("factory").setLevel(logging.WARN)
