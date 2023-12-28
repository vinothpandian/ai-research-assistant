from fastapi import APIRouter, Depends, HTTPException

from core.redis import RedisCache
from core.schema.arxiv import ArxivArticle, ArxivArticlesList
from core.schema.pagination import Pagination

from ..dependencies import get_cache
from ..lib.arxiv import get_arxiv_feed

router = APIRouter(
    prefix="/arxiv",
    tags=["arxiv"],
)


@router.get("/search/")
async def search_arxiv(q: str | None = None, start: int = 0, limit: int = 10, cache: RedisCache = Depends(get_cache)):
    if not q:
        raise HTTPException(status_code=400, detail="Query is required")

    if value := cache.get([q, start, limit]):
        return value

    feed = get_arxiv_feed(q, start, limit, mock=True)

    total_items = feed.get("feed", {}).get("opensearch_totalresults", 0)
    articles = ArxivArticlesList.model_validate(feed.get("entries", []))

    response = Pagination[ArxivArticle](
        total_items=total_items,
        start=start,
        limit=limit,
        items=articles,
    )

    cache.set([q, start, limit], response.model_dump(mode="json"))

    return response
