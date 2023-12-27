from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict()

    POCKETBASE_URL: str = "http://127.0.0.1:8080"
    QDRANT_URL: str = ":memory:"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""


settings = Settings()
