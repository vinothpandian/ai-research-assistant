from loguru import logger

from core.ai.agent import AIAgent
from core.lib.db import ArticleDB
from core.lib.vector_db import VectorDB
from core.schema.article import Article
from core.settings import settings


def generate_summary_task(article: Article):
    logger.debug(f"Generating summary for article {article.id}")

    articles_db = ArticleDB(settings=settings)
    ai_agent = AIAgent(settings=settings)

    summary = ""

    try:
        if article.abstract:
            summary = ai_agent.get_summary(article)

        articles_db.update_article(article_id=article.id, ai_summary=summary)
    except Exception as e:
        logger.error(f"Error generating summary for article {article.id}: {e}")
    else:
        logger.debug(f"Generated summary for article {article.id}")
    finally:
        articles_db.disconnect()


def generate_embeddings_task(article: Article):
    articles_db = ArticleDB(settings=settings)
    vector_db = VectorDB(settings=settings)
    ai_agent = AIAgent(settings=settings)

    try:
        vector = ai_agent.get_embeddings(article)
        vector_id = vector_db.save_article(article, vector)
        articles_db.update_article(article_id=article.id, vector_id=vector_id)
    except Exception as e:
        logger.error(f"Error generating embeddings for article {article.id}: {e}")
    else:
        logger.debug(f"Generated embeddings for article {article.id}")
    finally:
        articles_db.disconnect()
        vector_db.disconnect()
