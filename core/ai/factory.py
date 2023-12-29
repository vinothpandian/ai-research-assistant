from core.ai.base_engine import BaseAIEngine
from core.ai.ollama_engine import OllamaEngine
from core.ai.openai_engine import OpenAIEngine
from core.settings import Settings


class AIFactory:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.engines = {
            "SUMMARIZER_ENGINE": settings.SUMMARIZER_ENGINE,
            "EMBEDDING_ENGINE": settings.EMBEDDING_ENGINE,
            "QA_ENGINE": settings.QA_ENGINE,
        }

    def create_engine(self, engine_type):
        if engine_type not in self.engines:
            raise ValueError(f"Unknown engine type: {engine_type}")

        engine_name = self.engines[engine_type]
        match engine_name:
            case "ollama":
                return OllamaEngine(self.settings)
            case "base":
                return BaseAIEngine(self.settings)
            case "openai":
                return OpenAIEngine(self.settings)
            case _:
                raise ValueError(f"Unknown engine: {engine_name}")
