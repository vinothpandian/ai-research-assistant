from typing import Annotated

from fastapi import FastAPI
from pydantic import BaseModel, Field
from ray import serve
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


class RequestData(BaseModel):
    prompt: str
    min_length: Annotated[int | None, Field(gt=0)] = 100
    max_length: Annotated[int | None, Field(gt=0)] = 200


@serve.deployment(num_replicas=2, ray_actor_options={"num_cpus": 0.2, "num_gpus": 0})
@serve.ingress(app)
class Summarizer:
    def __init__(self):
        if settings.summarizer.type != "huggingface":
            self.model = None
            return

        self.model = pipeline("summarization", model=settings.summarizer.model)

    @app.post("/")
    def summarize(self, data: RequestData):
        if self.model is None:
            return {"response": "Summarizer is not available"}

        model_output = self.model(data.prompt)
        response = model_output[0]["summary_text"]
        return {"response": response}


summarizer_app = Summarizer.bind()  # type: ignore
