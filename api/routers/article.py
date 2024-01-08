from collections import defaultdict
from typing import Annotated, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pocketbase.utils import ClientResponseError
from starlette.responses import StreamingResponse

from core.ai.agent import AIAgent
from core.schema.article import ArticlesWithScoreList, CreateArticle
from core.utils.db import ArticleDB
from core.utils.vector_db import VectorDB
from workers.app import generate_embeddings_task, generate_summary_task

from ..dependencies import get_ai_agent, get_articles_db, get_vector_db

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
    articles_db: ArticleDB = Depends(get_articles_db),
):
    try:
        created_article = articles_db.create_article(article)
        generate_summary_task.send(article_id=created_article.id)
        generate_embeddings_task.send(article_id=created_article.id)
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
        vector_db.remove_article(article_id)
        articles_db.remove_article(article_id)
    except ClientResponseError as e:
        raise HTTPException(status_code=e.status, detail=str(e.data))


@router.get("/search/")
def search_articles(
    question: str,
    score_threshold: Annotated[float, Query(gt=0, lt=1)] = 0.1,
    articles_db: ArticleDB = Depends(get_articles_db),
    vector_db: VectorDB = Depends(get_vector_db),
    ai_agent: AIAgent = Depends(get_ai_agent),
):
    try:
        [vector] = ai_agent.get_embeddings([question])
        vector_db_articles = vector_db.semantic_search(vector)

        chunks_map: Dict[str, List[str]] = defaultdict(list)
        scores_map: Dict[str, float] = defaultdict(float)

        for article in vector_db_articles:
            if article.score > score_threshold:
                chunks_map[article.payload["id"]].append(article.payload["text"])
                scores_map[article.payload["id"]] = (scores_map[article.payload["id"]] + article.score) / 2

        article_ids = list(chunks_map.keys())

        if not article_ids:
            return HTTPException(status_code=404, detail="No relevant articles found for the given question")

        articles = articles_db.get_articles_by_ids(article_ids)

        articles_with_score = ArticlesWithScoreList(
            [
                dict(**article.model_dump(mode="json"), score=scores_map[article.id], chunks=chunks_map[article.id])
                for article in articles
            ]
        )

        return {"articles": articles_with_score}
    except ClientResponseError as e:
        raise HTTPException(status_code=e.status, detail=str(e.data))


@router.get("/question_answering/")
def question_answering(
    question: str,
    score_threshold: Annotated[float, Query(gt=0, lt=1)] = 0.1,
    articles_db: ArticleDB = Depends(get_articles_db),
    vector_db: VectorDB = Depends(get_vector_db),
    ai_agent: AIAgent = Depends(get_ai_agent),
):
    try:
        [vector] = ai_agent.get_embeddings([question])
        vector_db_articles = vector_db.semantic_search(vector)

        chunks_map = defaultdict(list)
        for article in vector_db_articles:
            if article.score > score_threshold:
                chunks_map[article.payload["id"]].append(article.payload["text"])
        article_ids = list(chunks_map.keys())

        if not article_ids:
            return HTTPException(status_code=404, detail="No relevant articles found for the given question")

        articles = articles_db.get_articles_by_ids(article_ids)
        articles_map = {article.id: article for article in articles}
        contexts = [
            f"""Title: {articles_map[article_id].title}

            Authors: {articles_map[article_id].authors}

            Extracted text: {chunks_map[article_id]}
            """
            for article_id in article_ids
        ]

        return StreamingResponse(ai_agent.get_answer(question, contexts), media_type="application/json")

    except ClientResponseError as e:
        raise HTTPException(status_code=e.status, detail=str(e.data))
