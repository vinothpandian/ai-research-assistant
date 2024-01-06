from core.ai.base_engine import HuggingfaceAIEngine
from core.ai.ollama_engine import OllamaEngine
from core.ai.openai_engine import OpenAIEngine
from core.schema.article import Article, ArticlesWithScoreList
from core.settings import Settings


class AIAgent:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.summarizer = self.__create_engine(settings.summarizer.type)
        self.embedding = self.__create_engine(settings.embedding.type)
        self.qa = self.__create_engine(settings.qa.type)

    def __create_engine(self, engine_name: str) -> HuggingfaceAIEngine:
        match engine_name:
            case "ollama":
                return OllamaEngine(self.settings)
            case "huggingface":
                return HuggingfaceAIEngine(self.settings)
            case "openai":
                return OpenAIEngine(self.settings)
            case _:
                raise ValueError(f"Unknown engine: {engine_name}")

    def get_summary(self, article: Article) -> str:
        return self.summarizer.get_summary(article)

    def get_embeddings(self, content: str | Article) -> list[float]:
        if isinstance(content, str):
            return self.embedding.get_embeddings(content)

        authors = ", ".join(content.authors)
        text = f"Title: {content.title}\n\nAuthors: {authors}\n\nAbstract: {content.abstract}"
        return self.embedding.get_embeddings(text)

    def get_answer(self, question: str, articles: ArticlesWithScoreList) -> str:
        return self.qa.get_answer(question, articles)
