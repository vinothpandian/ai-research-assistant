from typing import Annotated

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field
from transformers import pipeline

from core.settings import settings

app = FastAPI(
    title="Text summarizer API",
    description="API to summarize text",
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
    model = pipeline("summarization", model=settings.SUMMARIZER_MODEL)
    try:
        yield model
    finally:
        del model


class Prompt(BaseModel):
    prompt: str
    min_length: Annotated[int | None, Field(gt=0)] = 100
    max_length: Annotated[int | None, Field(gt=0)] = 200


@app.post("/summarize/")
async def summarize(data: Prompt, model=Depends(get_model)):
    summaries = model(data.prompt, max_length=data.max_length, min_length=data.min_length, do_sample=False)
    return {
        "response": summaries[0]['summary_text'],
    }
