import pathlib
import sys

import yaml
from pydantic_settings import BaseSettings


class RedisSettings(BaseSettings):
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str = ""


class QdrantSettings(BaseSettings):
    url: str = ":memory:"


class PocketbaseSettings(BaseSettings):
    url: str = "http://localhost:8080/"


class CelerySettings(BaseSettings):
    broker_url: str = "redis://localhost:6379/1"
    result_backend: str = "redis://localhost:6379/2"


class APISettings(BaseSettings):
    url: str = "http://localhost:8000/"


class AIEngineSettings(BaseSettings):
    type: str = ""
    model: str = ""
    url: str = ""


class SummarizerSettings(AIEngineSettings):
    type: str = "base"
    model: str = "Falconsai/text_summarization"
    url: str = "http://localhost:9000/summarize/"


class EmbeddingSettings(AIEngineSettings):
    type: str = "base"
    model: str = "all-MiniLM-L6-v2"
    url: str = "http://localhost:9001/embedding/"
    dim: int = 384
    distance: str = "dot"


class QASettings(AIEngineSettings):
    type: str = "base"
    model: str = "google/flan-t5-base"
    url: str = "http://localhost:9002/answer/"


class OpenAISettings(BaseSettings):
    key: str = ""


class Settings(BaseSettings):
    redis: RedisSettings = RedisSettings()
    qdrant: QdrantSettings = QdrantSettings()
    pocketbase: PocketbaseSettings = PocketbaseSettings()
    celery: CelerySettings = CelerySettings()
    api: APISettings = APISettings()
    summarizer: SummarizerSettings = SummarizerSettings()
    embedding: EmbeddingSettings = EmbeddingSettings()
    qa: QASettings = QASettings()
    openai: OpenAISettings = OpenAISettings()


if not pathlib.Path("config.yaml").exists():
    sys.exit("config.yaml not found")

with open("config.yaml") as f:
    config = yaml.safe_load(f)

settings = Settings.model_validate(config)
