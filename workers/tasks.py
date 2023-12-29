from celery import Celery
from loguru import logger

from core.ai.factory import AIFactory
from core.lib.db import ArticleDB
from core.lib.vector_db import VectorDB
from core.settings import settings

celery_app = Celery(
    "tasks",
    broker=f"redis://{settings.redis.host}:{settings.redis.port}/1",
    backend=f"redis://{settings.redis.host}:{settings.redis.port}/2",
)

article_db = ArticleDB(settings)
vector_db = VectorDB(settings)

ai_factory = AIFactory(settings)
summarizer_ai = ai_factory.create_engine("SUMMARIZER_ENGINE")
embedding_ai = ai_factory.create_engine("EMBEDDING_ENGINE")


@celery_app.task
def generate_summary(article_id: str):
    article = article_db.get_article(article_id)
    logger.debug(f"Generating summary for article {article_id}")

    summary = ""

    if article.abstract:
        summary = summarizer_ai.get_summary(article)

    article_db.update_article(article_id, ai_summary=summary)


@celery_app.task
def generate_embeddings(article_id: str):
    article = article_db.get_article(article_id)

    vector = embedding_ai.get_embeddings(article.abstract)

    vector_id = vector_db.save_article(article, vector)
    article_db.update_article(article_id, vector_id=vector_id)


@celery_app.task
def delete_embeddings(vector_id: str):
    vector_db.remove_article(vector_id)
