from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

from app.settings import settings

encoder = SentenceTransformer("all-MiniLM-L6-v2")


class VectorDB:

    def __init__(self):
        self.db = QdrantClient(settings.QDRANT_URL)
        self.db.recreate_collection(collection_name='articles', vectors_config=models.VectorParams(
            size=encoder.get_sentence_embedding_dimension(),
            distance=models.Distance.COSINE,
        ))

    def save_article(self, article):
        self.db.upload_records(
            collection_name='articles',
            records=[models.Record(
                id=str(article.uuid),
                vector=encoder.encode(f"{article.title}\n\n{article.summary}").tolist(),
                payload=article.model_dump(),
            )]
        )

    def remove_article(self, article):
        self.db.delete(collection_name='articles', points_selector=[str(article.uuid)])

    def semantic_search(self, text):
        vector = encoder.encode(text).tolist()
        return self.db.search(
            collection_name='articles',
            query_vector=vector,
            limit=5
        )


vector_db = VectorDB()
