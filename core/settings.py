from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict()

    POCKETBASE_URL: str = "http://127.0.0.1:8080"
    QDRANT_URL: str = ":memory:"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    SUMMARIZER_MODEL: str = "Falconsai/text_summarization"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    QA_MODEL: str = "google/flan-t5-base"
    EMBEDDING_DIM: int = 384

    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    SUMMARIZER_URL: str = "http://localhost:9000/summarize/"
    EMBEDDING_URL: str = "http://localhost:9001/embedding/"
    QA_URL: str = "http://localhost:9002/answer/"


settings = Settings()
