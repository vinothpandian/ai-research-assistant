from fastapi import Depends, FastAPI
from pydantic import BaseModel
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


def get_encoder() -> SentenceTransformer:
    encoder = SentenceTransformer(settings.embedding.model)

    try:
        if encoder.get_sentence_embedding_dimension() != settings.embedding.dim:
            raise ValueError(f"Embedding encoder should have {settings.embedding.dim} dimensions")

        yield encoder
    finally:
        del encoder


class Prompt(BaseModel):
    prompt: str


@app.post("/embedding/")
async def get_embedding(data: Prompt, encoder: SentenceTransformer = Depends(get_encoder)):
    return {
        "embedding": encoder.encode(data.prompt).tolist(),
    }
