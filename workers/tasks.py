from typing import Literal

import httpx
from celery import shared_task

from api.lib.db import ArticleDB
from api.lib.vector_db import VectorDB
from api.schema.article import Article
from core.settings import settings

article_db = ArticleDB(settings)
vector_db = VectorDB(settings)

ModelType = Literal["general", "summarizer"]


def generate_summarization_prompt(article: Article, model_type: ModelType = "summarizer") -> str:
    if model_type == "summarizer":
        return article.abstract

    return f""""
    {article.abstract}
    ###
    Generate a summary of the above text from a research paper in 100 to 200 words. Do no
    include any other information other than the summary. The summary should be in your own
    words and should not be a copy of the abstract. The summary should be in English and
    should be grammatically correct. The summary should be in complete sentences and should
    not contain any bullet points or lists. The summary should be in the third person and
    should not contain any personal pronouns.
    """


@shared_task
def generate_summary(article_id: str):
    article = article_db.get_article(article_id)

    model_type: ModelType = "summarizer"
    if settings.EMBEDDING_MODEL in {"llama2"}:
        model_type = "general"

    prompt = generate_summarization_prompt(article, model_type)
    data = {'model': settings.SUMMARIZER_MODEL, 'prompt': prompt, 'stream': False}

    response = httpx.post(settings.SUMMARIZER_URL, json=data, timeout=None)
    response.raise_for_status()

    result = response.json()

    article_db.update_article(article_id, ai_summary=result['response'])


@shared_task
def generate_embeddings(article_id: str):
    article = article_db.get_article(article_id)
    data = {'model': settings.EMBEDDING_MODEL,
            'prompt': f"{article.title}\n\n{article.abstract}",
            'stream': False}

    response = httpx.post(settings.EMBEDDING_URL, json=data, timeout=None)
    response.raise_for_status()

    result = response.json()

    vector_id = vector_db.save_article(article, result['embedding'])
    article_db.update_article(article_id, vector_id=vector_id)


@shared_task
def delete_embeddings(vector_id: str):
    vector_db.remove_article(vector_id)
