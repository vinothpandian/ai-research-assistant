import logging
from typing import Generator
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from core.lib.db import ArticleDB

from ..dependencies import get_articles_db
from ..main import app

db = Mock(name="ArticleDB", spec=ArticleDB)


def override_get_articles_db():
    yield db


app.dependency_overrides[get_articles_db] = override_get_articles_db  # type: ignore


@pytest.fixture(scope="session")
def api_client():
    client = TestClient(app)
    yield client


@pytest.fixture(scope="session")
def articles_db() -> Generator[ArticleDB, None, None]:
    yield db


# suppress DeprecationWarning
logging.getLogger("factory").setLevel(logging.WARN)
