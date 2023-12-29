from fastapi import APIRouter, Depends, HTTPException
from pocketbase.utils import ClientResponseError

from core.redis import RedisCache

from ..dependencies import get_cache
from ..lib.semantic_scholar import get_semantic_scholar_feed

router = APIRouter(
    prefix="/semantic_scholar",
    tags=["semantic scholar"],
)


@router.get("/search/")
async def search_semantic_scholar(
    q: str | None = None, start: int = 0, limit: int = 10, cache: RedisCache = Depends(get_cache)
):
    if not q:
        raise HTTPException(status_code=400, detail="Query is required")

    if value := cache.get([q, start, limit]):
        return value

    try:
        response = get_semantic_scholar_feed(q, start, limit)
    except ClientResponseError as e:
        raise HTTPException(status_code=e.status, detail=str(e.data))

    cache.set([q, start, limit], response.model_dump(mode="json"))

    return response
