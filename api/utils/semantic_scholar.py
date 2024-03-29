import httpx

from core.schema.pagination import Pagination
from core.schema.semantic_scholar import SemanticScholarArticlesList
from core.settings import settings


def get_semantic_scholar_feed(q: str, start: int = 0, limit: int = 10) -> Pagination[SemanticScholarArticlesList]:
    headers = {}

    if api_key := settings.semantic_scholar.api_key:
        headers["x-api-key"] = api_key

    response = httpx.get(
        "https://api.semanticscholar.org/graph/v1/paper/search",
        headers=headers,
        params=dict(
            fields="paperId,title,abstract,url,authors,publicationDate,openAccessPdf",
            fieldsOfStudy="Computer Science",
            publicationTypes="JournalArticle",
            query=q,
            offset=start,
            limit=limit,
        ),
        timeout=None,
    )

    response.raise_for_status()

    result = response.json()

    data = result.get("data", [])

    return Pagination(
        total_items=result["total"],
        start=start,
        limit=limit,
        items=SemanticScholarArticlesList.model_validate(data),
    )
