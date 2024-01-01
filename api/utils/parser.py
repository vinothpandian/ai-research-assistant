from typing import List, cast

from pocketbase.models.utils.base_model import BaseModel

from core.schema.article import Article, ArticlesList


def get_article_from_record(record: BaseModel):
    record = cast(Article, record)
    return Article(
        id=record.id,
        arxiv_id=record.arxiv_id,
        title=record.title,
        abstract=record.abstract,
        link=record.link,
        published=record.published,
        authors=record.authors,
        ai_summary=record.ai_summary,
        vector_id=record.vector_id,
    )


def get_articles_from_records(records: List[BaseModel]):
    return ArticlesList([get_article_from_record(record) for record in records])
