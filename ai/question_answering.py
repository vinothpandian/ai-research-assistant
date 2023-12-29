from fastapi import Depends, FastAPI
from pydantic import BaseModel
from transformers import pipeline

from core.settings import settings

app = FastAPI(
    title="QA API",
    description="API to answer questions based on context",
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


def get_model():
    model = pipeline("text2text-generation", model=settings.qa.model)
    try:
        yield model
    finally:
        del model


class Prompt(BaseModel):
    prompt: str


@app.post("/answer/")
async def answer(data: Prompt, model=Depends(get_model)):
    result = model(data.prompt)
    return {
        "response": result[0]["generated_text"],
    }
