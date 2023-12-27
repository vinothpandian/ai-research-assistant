import pocketbase

from core.redis import RedisCache
from core.settings import settings

from .lib.db import ArticleDB


def get_cache() -> RedisCache:
    cache = RedisCache(settings=settings)

    try:
        cache.ping()
        yield cache
    finally:
        cache.disconnect()


def get_articles_db() -> pocketbase.PocketBase:
    article_db = ArticleDB(settings=settings)

    try:
        yield article_db
    finally:
        article_db.disconnect()
