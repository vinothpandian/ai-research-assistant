from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pocketbase.utils import ClientResponseError
from starlette import status

from core.ai.agent import AIAgent
from core.lib.db import ArticleDB
from core.lib.vector_db import VectorDB

from ..dependencies import get_ai_agent, get_articles_db, get_vector_db
from ..tasks import generate_embeddings_task, generate_summary_task

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)


@router.post("/generate_embeddings/{article_id}/", status_code=status.HTTP_200_OK)
async def generate_embeddings(
    article_id: str,
    background_tasks: BackgroundTasks,
    articles_db: ArticleDB = Depends(get_articles_db),
    vector_db: VectorDB = Depends(get_vector_db),
    ai_agent: AIAgent = Depends(get_ai_agent),
):
    try:
        article = articles_db.get_article(article_id)
        background_tasks.add_task(generate_embeddings_task, article=article)
    except ClientResponseError as e:
        raise HTTPException(status_code=e.status, detail=str(e.data))


@router.post("/generate_summary/{article_id}/", status_code=status.HTTP_200_OK)
async def generate_summary(
    article_id: str,
    background_tasks: BackgroundTasks,
    articles_db: ArticleDB = Depends(get_articles_db),
    ai_agent: AIAgent = Depends(get_ai_agent),
):
    try:
        article = articles_db.get_article(article_id)
        background_tasks.add_task(generate_summary_task, article=article)
    except ClientResponseError as e:
        raise HTTPException(status_code=e.status, detail=str(e.data))
