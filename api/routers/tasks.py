from fastapi import APIRouter
from starlette import status

from workers.app import generate_embeddings_task, generate_summary_task

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)


@router.post("/generate_embeddings/{article_id}/", status_code=status.HTTP_200_OK)
async def generate_embeddings(article_id: str):
    generate_embeddings_task.send(article_id=article_id)


@router.post("/generate_summary/{article_id}/", status_code=status.HTTP_200_OK)
async def generate_summary(article_id: str):
    generate_summary_task.send(article_id=article_id)
