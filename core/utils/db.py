import pocketbase
from pocketbase.models.utils import BaseModel

from api.utils.parser import get_article_from_record, get_articles_from_records
from core.schema.article import Article, ArticlesList, CreateArticle
from core.schema.pagination import Pagination
from core.settings import Settings


class ArticleDB:
    collection_name = "articles"

    def __init__(self, settings: Settings):
        self.client = pocketbase.PocketBase(settings.pocketbase.url)

    @property
    def collections(self):
        return self.client.collection(self.collection_name)

    def get_article(self, article_id: str) -> Article:
        record = self.collections.get_one(article_id)
        return get_article_from_record(record)

    def create_article(self, article: CreateArticle) -> Article:
        record = self.collections.create(article.model_dump(mode="json"))
        return get_article_from_record(record)

    def update_article(self, article_id: str, **kwargs) -> BaseModel:
        return self.collections.update(article_id, kwargs)

    def remove_article(self, article_id: str) -> bool:
        return self.collections.delete(article_id)

    def get_articles(self, start: int = 0, limit: int = 10, sort_by="-created") -> Pagination[Article]:
        page = start // limit + 1
        response = self.collections.get_list(page=page, per_page=limit, query_params={"sort": sort_by})

        return Pagination(
            start=start,
            limit=limit,
            total_items=response.total_items,
            items=get_articles_from_records(response.items),
        )

    def get_articles_by_ids(self, article_ids: list) -> ArticlesList:
        filters = " || ".join(f"id = '{article_id}'" for article_id in article_ids)
        response = self.collections.get_full_list(query_params={"filter": filters})
        return get_articles_from_records(response)

    def disconnect(self):
        self.client = None
