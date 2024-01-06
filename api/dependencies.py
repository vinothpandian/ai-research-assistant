import contextlib
from typing import Generator

from core.ai.agent import AIAgent
from core.redis import RedisCache
from core.settings import settings
from core.utils.db import ArticleDB
from core.utils.vector_db import VectorDB


def get_cache() -> Generator[RedisCache, None, None]:
    cache = RedisCache(settings=settings)

    try:
        cache.ping()
        yield cache
    finally:
        cache.disconnect()


def get_articles_db() -> Generator[ArticleDB, None, None]:
    article_db = ArticleDB(settings=settings)

    try:
        yield article_db
    finally:
        article_db.disconnect()


def get_vector_db() -> Generator[VectorDB, None, None]:
    vector_db = VectorDB(settings=settings)

    try:
        yield vector_db
    finally:
        vector_db.disconnect()


def get_ai_agent():
    ai_agent = AIAgent(settings=settings)

    with contextlib.suppress(Exception):
        yield ai_agent
