from celery import shared_task

from core import ai
from core.lib.db import ArticleDB
from core.lib.vector_db import VectorDB
from core.settings import settings

article_db = ArticleDB(settings)
vector_db = VectorDB(settings)


@shared_task
def generate_summary(article_id: str):
    article = article_db.get_article(article_id)

    prompt = ai.generate_summarization_prompt(article)
    summary = ai.get_summary(prompt)

    article_db.update_article(article_id, ai_summary=summary)


@shared_task
def generate_embeddings(article_id: str):
    article = article_db.get_article(article_id)
    vector = ai.get_embeddings(f"{article.title}\n\n{article.abstract}")

    vector_id = vector_db.save_article(article, vector)
    article_db.update_article(article_id, vector_id=vector_id)


@shared_task
def delete_embeddings(vector_id: str):
    vector_db.remove_article(vector_id)
