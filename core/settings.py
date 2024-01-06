import os
import pathlib
import sys
from typing import Literal

import yaml
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


CONFIG_FILE = os.getenv("CONFIG_FILE", "config.yaml")

AIEngineType = Literal["huggingface", "ollama", "openai"]


class RedisSettings(BaseSettings):
    host: str = "localhost"
    port: int = 6379
    db: int = 0


class QdrantSettings(BaseSettings):
    url: str = ":memory:"


class PocketbaseSettings(BaseSettings):
    url: str = "http://localhost:8080/"


class APISettings(BaseSettings):
    url: str = "http://localhost:8000/"


class AIEngineSettings(BaseSettings):
    type: str = ""
    model: str = ""
    url: str = ""


class SummarizerSettings(AIEngineSettings):
    type: AIEngineType = "huggingface"
    model: str = "Falconsai/text_summarization"
    url: str = "http://localhost:9000/summarize/"


class EmbeddingSettings(AIEngineSettings):
    type: AIEngineType = "huggingface"
    model: str = "all-MiniLM-L6-v2"
    url: str = "http://localhost:9001/embedding/"
    dim: int = 384
    distance: str = "dot"


class QASettings(AIEngineSettings):
    type: AIEngineType = "huggingface"
    model: str = "google/flan-t5-base"
    url: str = "http://localhost:9002/answer/"


class OpenAISettings(BaseSettings):
    key: str = ""


class Settings(BaseSettings):
    redis: RedisSettings = RedisSettings()
    qdrant: QdrantSettings = QdrantSettings()
    pocketbase: PocketbaseSettings = PocketbaseSettings()
    api: APISettings = APISettings()
    summarizer: SummarizerSettings = SummarizerSettings()
    embedding: EmbeddingSettings = EmbeddingSettings()
    qa: QASettings = QASettings()
    openai: OpenAISettings = OpenAISettings()


if not pathlib.Path(CONFIG_FILE).exists():
    sys.exit("config.yaml not found")

with open(CONFIG_FILE) as f:
    config = yaml.safe_load(f)

settings = Settings.model_validate(config)
