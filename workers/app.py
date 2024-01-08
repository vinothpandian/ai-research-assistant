import dramatiq
from dramatiq.brokers.redis import RedisBroker
from loguru import logger

from core.ai.agent import AIAgent
from core.settings import settings
from core.utils.chunking import get_chunks_from_article
from core.utils.db import ArticleDB
from core.utils.vector_db import VectorDB

redis_broker = RedisBroker(host=settings.redis.host, port=settings.redis.port)
dramatiq.set_broker(redis_broker)


@dramatiq.actor(max_retries=5)
def generate_summary_task(article_id: str):
    articles_db = ArticleDB(settings=settings)
    ai_agent = AIAgent(settings=settings)

    logger.debug(f"Generating summary for article {article_id}")
    summary = ""

    try:
        article = articles_db.get_article(article_id)

        if article.abstract:
            summary = ai_agent.get_summary(article)

        articles_db.update_article(article_id=article_id, ai_summary=summary)
    except Exception as e:
        logger.error(f"Error generating summary for article {article_id}: {e}")
    else:
        logger.debug(f"Generated summary for article {article_id}")
    finally:
        articles_db.disconnect()


@dramatiq.actor(max_retries=5)
def generate_embeddings_task(article_id: str):
    articles_db = ArticleDB(settings=settings)
    vector_db = VectorDB(settings=settings)
    ai_agent = AIAgent(settings=settings)

    try:
        article = articles_db.get_article(article_id)
        chunks = get_chunks_from_article(article=article)
        vectors = ai_agent.get_embeddings(chunks)
        vector_db.save_article(article_id, chunks, vectors)
        articles_db.update_article(article_id=article_id, embeddings_generated=True)
    except Exception as e:
        logger.error(f"Error generating embeddings for article {article.id}: {e}")
    else:
        logger.debug(f"Generated embeddings for article {article.id}")
    finally:
        articles_db.disconnect()
        vector_db.disconnect()
