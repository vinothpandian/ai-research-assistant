from fastapi import FastAPI
from pydantic import BaseModel
from ray import serve
from sentence_transformers import SentenceTransformer

from core.settings import settings

app = FastAPI(
    title="Sentence embedding API",
    description="API to get vector embedding for a sentence",
    version="0.0.1",
    contact={
        "name": "Vinoth Pandian",
        "url": "https://vinoth.info",
        "email": "vinothpandian@users.noreply.github.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    docs_url="/",
)


class RequestData(BaseModel):
    prompt: str


@serve.deployment(num_replicas=2, ray_actor_options={"num_cpus": 0.2, "num_gpus": 0})
@serve.ingress(app)
class EmbeddingGenerator:
    def __init__(self):
        if settings.embedding.type != "huggingface":
            self.model = None
            return

        self.model = SentenceTransformer(settings.embedding.model)
        if self.model.get_sentence_embedding_dimension() != settings.embedding.dim:
            raise ValueError("Embedding dimension mismatch")

    @app.post("/")
    def generate_embedding(self, data: RequestData):
        if self.model is None:
            return {"response": "Embedding is not available"}

        model_output = self.model.encode(data.prompt).tolist()
        return {"embedding": model_output}


embedding_app = EmbeddingGenerator.bind()
