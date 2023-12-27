from fastapi import APIRouter, Depends, HTTPException
from pocketbase.utils import ClientResponseError

from workers.tasks import delete_embeddings, generate_embeddings, generate_summary

from ..dependencies import get_articles_db
from ..lib.db import ArticleDB
from ..schema.article import CreateArticle

router = APIRouter(
    prefix="/articles",
    tags=["articles"],
)


@router.get("/")
async def get_articles(start: int = 0, limit: int = 10, db: ArticleDB = Depends(get_articles_db)):
    try:
        return db.get_articles(start=start, limit=limit)
    except ClientResponseError as e:
        raise HTTPException(status_code=e.status, detail=str(e.data))


@router.post("/add/")
def add_article(article: CreateArticle, db: ArticleDB = Depends(get_articles_db)):
    try:
        record = db.create_article(article)
        generate_embeddings.delay(record.id)
        generate_summary.delay(record.id)
        return dict(message="Article added successfully")
    except ClientResponseError as e:
        raise HTTPException(status_code=e.status, detail=str(e.data))


@router.delete("/remove/")
def remove_article(article_id: str, db: ArticleDB = Depends(get_articles_db)):
    try:
        vector_id = db.get_article(article_id).vector_id
        delete_embeddings.delay(vector_id)
        db.remove_article(article_id)
        return dict(message="Article removed successfully")
    except ClientResponseError as e:
        raise HTTPException(status_code=e.status, detail=str(e.data))
