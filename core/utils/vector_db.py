import contextlib
from uuid import uuid4

from qdrant_client import QdrantClient, models

from core.schema.article import Article
from core.settings import Settings

DISTANCE_MAP = {
    "cosine": models.Distance.COSINE,
    "euclidean": models.Distance.EUCLID,
    "dot": models.Distance.DOT,
}


class VectorDB:
    def __init__(self, settings: Settings):
        self.client = QdrantClient(settings.qdrant.url)
        self.collection_name = f"articles-{settings.embedding.dim}"

        distance = DISTANCE_MAP.get(settings.embedding.distance)

        with contextlib.suppress(Exception):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=settings.embedding.dim,
                    distance=distance,
                ),
            )

    def save_article(self, article: Article, vector):
        vector_id = str(uuid4())  # generate a random id
        self.client.upload_records(
            collection_name=self.collection_name,
            records=[
                models.Record(
                    id=vector_id,
                    vector=vector,
                    payload=dict(id=article.id),
                )
            ],
        )
        return vector_id

    def remove_article(self, vector_id: str):
        self.client.delete(collection_name=self.collection_name, points_selector=[vector_id])

    def semantic_search(self, vector):
        return self.client.search(collection_name=self.collection_name, query_vector=vector, limit=3)

    def disconnect(self):
        self.client = None
