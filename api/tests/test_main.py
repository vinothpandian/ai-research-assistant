from unittest.mock import patch

from starlette import status

from core.schema.pagination import Pagination


def test_check_articles(api_client, articles_db):
    articles_db.get_articles.return_value = Pagination(
        start=0,
        limit=10,
        total_items=0,
        items=[],
    )

    response = api_client.get("/articles/")
    assert response.status_code == status.HTTP_200_OK
    assert articles_db.get_articles.call_count == 1

    assert response.json() == {
        "start": 0,
        "limit": 10,
        "total_items": 0,
        "items": [],
    }


@patch("api.routers.article.generate_embeddings_task")
@patch("api.routers.article.generate_summary_task")
def test_create_article_validation(mock_generate_embeddings, mock_generate_summary, api_client, articles_db):
    response = api_client.post(
        "/articles/",
        json={
            "title": "Test",
            "content": "Test",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert mock_generate_summary.delay.call_count == 0
    assert mock_generate_embeddings.delay.call_count == 0
    assert articles_db.create_article.call_count == 0


@patch("api.routers.article.generate_embeddings_task")
@patch("api.routers.article.generate_summary_task")
def test_create_article(mock_generate_embeddings, mock_generate_summary, api_client, articles_db):
    response = api_client.post(
        "/articles/",
        json={
            "arxiv_id": "1234.5678",
            "title": "Test",
            "abstract": "Test",
            "link": "https://example.com",
            "published": "2021-01-01",
            "authors": ["John Doe"],
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert mock_generate_summary.call_count == 1
    assert mock_generate_embeddings.call_count == 1
    assert articles_db.create_article.call_count == 1


def test_delete_article(api_client, articles_db, vector_db):
    response = api_client.delete("/articles/1234/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert articles_db.get_article.call_count == 1
    assert vector_db.remove_article.call_count == 1
    assert articles_db.remove_article.call_count == 1
