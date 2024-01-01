from typing import Generator

import httpx

from core.schema.article import ArticlesList, ArticlesWithScoreList, CreateArticle
from core.schema.pagination import Pagination
from core.schema.semantic_scholar import SemanticScholarArticlesList
from core.settings import Settings


class ApiClient:
    def __init__(self, settings: Settings):
        self.base_url = settings.api.url

    def search_articles(self, query: str, start: int = 0, limit: int = 10) -> Pagination[SemanticScholarArticlesList]:
        response = httpx.get(f"{self.base_url}semantic_scholar/search/", params=dict(q=query, start=start, limit=limit))
        response.raise_for_status()
        result = response.json()
        return Pagination(
            total_items=result["total_items"],
            start=result["start"],
            limit=result["limit"],
            items=SemanticScholarArticlesList.model_validate(result["items"]),
        )

    def get_articles(self, start: int = 0, limit: int = 10) -> Pagination[ArticlesList]:
        response = httpx.get(f"{self.base_url}articles/", params=dict(start=start, limit=limit))
        response.raise_for_status()
        result = response.json()
        return Pagination(
            total_items=result["total_items"],
            start=result["start"],
            limit=result["limit"],
            items=ArticlesList.model_validate(result["items"]),
        )

    def create_article(self, article: CreateArticle) -> None:
        response = httpx.post(f"{self.base_url}articles/", json=article.model_dump(mode="json"))
        response.raise_for_status()

    def delete_article(self, article_id: int) -> None:
        response = httpx.delete(f"{self.base_url}articles/{article_id}/")
        response.raise_for_status()

    def regenerate_summary(self, article_id: int) -> None:
        response = httpx.post(f"{self.base_url}tasks/generate_summary/{article_id}/")
        response.raise_for_status()

    def regenerate_embeddings(self, article_id: int) -> None:
        response = httpx.post(f"{self.base_url}tasks/generate_embeddings/{article_id}/")
        response.raise_for_status()

    def semantic_search(self, question: str, score_threshold: float = 0.1) -> ArticlesWithScoreList:
        response = httpx.get(
            f"{self.base_url}articles/search/",
            params=dict(
                question=question,
                score_threshold=score_threshold,
            ),
        )
        response.raise_for_status()
        data = response.json().get("articles", [])
        return ArticlesWithScoreList.model_validate(data)

    def question_answering(self, question: str, score_threshold: float = 0.1) -> Generator[str, None, None]:
        with httpx.stream(
            "GET",
            f"{self.base_url}articles/question_answering/",
            params=dict(
                question=question,
                score_threshold=score_threshold,
            ),
            timeout=None,
        ) as response:
            for i, line in enumerate(response.iter_text()):
                yield line
