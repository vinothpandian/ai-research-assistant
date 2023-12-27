from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_articles_db
from ..lib.db import ArticleDB
from ..schema.article import CreateArticle

router = APIRouter(
    prefix="/articles",
    tags=["articles"],
)


@router.get("/")
async def get_articles(start: int = 0, limit: int = 10, db: ArticleDB = Depends(get_articles_db)):
    return db.get_articles(start=start, limit=limit)


@router.post("/add/")
def add_article(article: CreateArticle, db: ArticleDB = Depends(get_articles_db)):
    try:
        db.save_article(article)
        return dict(message="Article added successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/remove/")
def remove_article(article_id: str, db: ArticleDB = Depends(get_articles_db)):
    try:
        db.remove_article(article_id)
        return dict(message="Article removed successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
