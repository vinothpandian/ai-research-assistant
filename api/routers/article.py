from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pocketbase.utils import ClientResponseError
from starlette.responses import StreamingResponse

from core.ai.factory import AIFactory
from core.lib.db import ArticleDB
from core.lib.vector_db import VectorDB
from core.schema.article import ArticlesWithScoreList, CreateArticle
from core.settings import settings
from workers.tasks import delete_embeddings, generate_embeddings, generate_summary

from ..dependencies import get_articles_db, get_vector_db

router = APIRouter(
    prefix="/articles",
    tags=["articles"],
)

ai_factory = AIFactory(settings)
embedding_ai = ai_factory.create_engine("EMBEDDING_ENGINE")
qa_ai = ai_factory.create_engine("QA_ENGINE")


@router.get("/")
async def get_articles(start: int = 0, limit: int = 10, db: ArticleDB = Depends(get_articles_db)):
    try:
        return db.get_articles(start=start, limit=limit)
    except ClientResponseError as e:
        raise HTTPException(status_code=e.status, detail=str(e.data))


@router.post("/", status_code=201)
def add_article(article: CreateArticle, db: ArticleDB = Depends(get_articles_db)):
    try:
        record = db.create_article(article)
        generate_embeddings.delay(record.id)
        generate_summary.delay(record.id)
        return dict(message="Article added successfully")
    except ClientResponseError as e:
        raise HTTPException(status_code=e.status, detail=str(e.data))


@router.delete("/{article_id}/", status_code=204)
def remove_article(article_id: str, db: ArticleDB = Depends(get_articles_db)):
    try:
        vector_id = db.get_article(article_id).vector_id
        delete_embeddings.delay(vector_id)
        db.remove_article(article_id)
    except ClientResponseError as e:
        raise HTTPException(status_code=e.status, detail=str(e.data))


@router.get("/search/")
def search_articles(
    question: str,
    score_threshold: Annotated[float, Query(gt=0, lt=1)] = 0.1,
    with_answer: bool = False,
    db: ArticleDB = Depends(get_articles_db),
    vector_db: VectorDB = Depends(get_vector_db),
):
    try:
        vector = embedding_ai.get_embeddings(question)
        vector_db_articles = vector_db.semantic_search(vector)

        article_ids = [article.payload["id"] for article in vector_db_articles if article.score > score_threshold]

        if not article_ids:
            return HTTPException(status_code=404, detail="No relevant articles found for the given question")

        articles = db.get_articles_by_ids(article_ids)
        articles_with_score = ArticlesWithScoreList(
            [
                dict(article.model_dump(mode="json"), score=vector_db_article.score)
                for article, vector_db_article in zip(articles, vector_db_articles)
            ]
        )

        return StreamingResponse(
            qa_ai.get_answer(question, articles_with_score, with_answer), media_type="application/json"
        )
    except ClientResponseError as e:
        raise HTTPException(status_code=e.status, detail=str(e.data))
