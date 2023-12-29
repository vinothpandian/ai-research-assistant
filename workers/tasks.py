import dramatiq

from core.ai.factory import AIFactory
from core.lib.db import ArticleDB
from core.lib.vector_db import VectorDB
from core.settings import settings

article_db = ArticleDB(settings)
vector_db = VectorDB(settings)

ai_factory = AIFactory(settings)
summarizer_ai = ai_factory.create_engine("SUMMARIZER_ENGINE")
embedding_ai = ai_factory.create_engine("EMBEDDING_ENGINE")


@dramatiq.actor()
def generate_summary(article_id: str):
    article = article_db.get_article(article_id)

    summary = ""

    if article.abstract:
        summary = summarizer_ai.get_summary(article)

    article_db.update_article(article_id, ai_summary=summary)


@dramatiq.actor()
def generate_embeddings(article_id: str):
    article = article_db.get_article(article_id)

    vector = embedding_ai.get_embeddings(article)

    vector_id = vector_db.save_article(article, vector)
    article_db.update_article(article_id, vector_id=vector_id)


@dramatiq.actor()
def delete_embeddings(vector_id: str):
    vector_db.remove_article(vector_id)
