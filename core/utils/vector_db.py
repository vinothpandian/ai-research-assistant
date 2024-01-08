import contextlib
from typing import List
from uuid import uuid4

from qdrant_client import QdrantClient, models
from qdrant_client.models import ScoredPoint

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

    def save_article(self, article_id: str, chunks: List[str], vectors: List[List[float]]):
        vector_ids = [str(uuid4()) for _ in range(len(vectors))]
        records = [
            models.Record(
                id=vector_id,
                vector=vector,
                payload=dict(id=article_id, text=chunk),
            )
            for vector_id, chunk, vector in zip(vector_ids, chunks, vectors)
        ]

        self.client.upload_records(
            collection_name=self.collection_name,
            records=records,
        )

    def remove_article(self, article_id: str) -> None:
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="id",
                            match=models.MatchValue(value=article_id),
                        ),
                    ]
                )
            ),
        )

    def semantic_search(self, vector: List[float]) -> List[ScoredPoint]:
        return self.client.search(collection_name=self.collection_name, query_vector=vector, limit=10)

    def disconnect(self):
        self.client = None
