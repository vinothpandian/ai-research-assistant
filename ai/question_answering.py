from fastapi import FastAPI
from pydantic import BaseModel
from ray import serve
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


class RequestData(BaseModel):
    prompt: str


@serve.deployment(num_replicas=2, ray_actor_options={"num_cpus": 0.2, "num_gpus": 0})
@serve.ingress(app)
class QuestionAnswering:
    def __init__(self):
        if settings.qa.type != "huggingface":
            self.model = None
            return

        self.model = pipeline("text2text-generation", model=settings.qa.model)

    @app.post("/")
    def generate_answer(self, data: RequestData):
        if self.model is None:
            return {"response": "Question answering is not available"}

        model_output = self.model(data.prompt)
        response = model_output[0]["generated_text"]
        return {"response": response}


qa_app = QuestionAnswering.bind()  # type: ignore
