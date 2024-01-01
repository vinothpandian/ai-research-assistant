from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pocketbase.utils import ClientResponseError
from starlette.responses import StreamingResponse

from core.ai.agent import AIAgent
from core.lib.db import ArticleDB
from core.lib.vector_db import VectorDB
from core.schema.article import ArticlesWithScoreList, CreateArticle

from ..dependencies import get_ai_agent, get_articles_db, get_vector_db
from ..tasks import generate_embeddings_task, generate_summary_task

router = APIRouter(
    prefix="/articles",
    tags=["articles"],
)


@router.get("/")
async def get_articles(start: int = 0, limit: int = 10, articles_db: ArticleDB = Depends(get_articles_db)):
    try:
        return articles_db.get_articles(start=start, limit=limit)
    except ClientResponseError as e:
        raise HTTPException(status_code=e.status, detail=str(e.data))


@router.post("/", status_code=201)
def add_article(
    article: CreateArticle,
    background_tasks: BackgroundTasks,
    articles_db: ArticleDB = Depends(get_articles_db),
):
    try:
        created_article = articles_db.create_article(article)
        background_tasks.add_task(generate_summary_task, article=created_article)
        background_tasks.add_task(generate_embeddings_task, article=created_article)
        return created_article
    except ClientResponseError as e:
        raise HTTPException(status_code=e.status, detail=str(e.data))


@router.delete("/{article_id}/", status_code=204)
def remove_article(
    article_id: str,
    articles_db: ArticleDB = Depends(get_articles_db),
    vector_db: VectorDB = Depends(get_vector_db),
):
    try:
        vector_id = articles_db.get_article(article_id).vector_id
        vector_db.remove_article(vector_id)
        articles_db.remove_article(article_id)
    except ClientResponseError as e:
        raise HTTPException(status_code=e.status, detail=str(e.data))


@router.get("/search/")
def search_articles(
    question: str,
    score_threshold: Annotated[float, Query(gt=0, lt=1)] = 0.1,
    with_answer: bool = False,
    articles_db: ArticleDB = Depends(get_articles_db),
    vector_db: VectorDB = Depends(get_vector_db),
    ai_agent: AIAgent = Depends(get_ai_agent),
):
    try:
        vector = ai_agent.get_embeddings(question)
        vector_db_articles = vector_db.semantic_search(vector)

        article_ids = [article.payload["id"] for article in vector_db_articles if article.score > score_threshold]

        if not article_ids:
            return HTTPException(status_code=404, detail="No relevant articles found for the given question")

        articles = articles_db.get_articles_by_ids(article_ids)
        articles_with_score = ArticlesWithScoreList(
            [
                dict(article.model_dump(mode="json"), score=vector_db_article.score)
                for article, vector_db_article in zip(articles, vector_db_articles)
            ]
        )

        return StreamingResponse(
            ai_agent.get_answer(question, articles_with_score, with_answer),
            media_type="application/json",
        )
    except ClientResponseError as e:
        raise HTTPException(status_code=e.status, detail=str(e.data))
