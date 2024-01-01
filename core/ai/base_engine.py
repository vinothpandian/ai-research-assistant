from typing import Dict

import httpx

from core.schema.article import Article, ArticlesWithScoreList
from core.settings import Settings


class BaseAIEngine:
    def __init__(self, settings: Settings):
        self.summarizer_url = settings.summarizer.url
        self.summarizer_model = settings.summarizer.model

        self.embedding_url = settings.embedding.url
        self.embedding_model = settings.embedding.model

        self.qa_url = settings.qa.url
        self.qa_model = settings.qa.model

    def get_summarization_request_data(self, article: Article) -> Dict[str, str]:
        return {"prompt": article.abstract}

    def get_embeddings_request_data(self, text: str) -> Dict[str, str]:
        return {"prompt": text}

    def get_question_answer_request_data(self, question: str, articles: ArticlesWithScoreList) -> Dict[str, str]:
        abstracts = self.get_question_info(articles)

        prompt = f"""Context: {abstracts}

        Question: {question}?

        Answer: """

        return {"prompt": prompt}

    def get_question_info(self, articles):
        return "\n\n".join(
            [
                f"Article #{i}:\nTitle: {article.title}\nAuthors:{article.authors}\nAbsract:{article.abstract}"
                for i, article in enumerate(articles)
            ]
        )

    def get_summary(self, article: Article):
        data = self.get_summarization_request_data(article)

        response = httpx.post(self.summarizer_url, json=data, timeout=None)
        response.raise_for_status()
        result = response.json()
        return result["response"]

    def get_embeddings(self, text: str):
        data = self.get_embeddings_request_data(text)

        response = httpx.post(self.embedding_url, json=data, timeout=None)
        response.raise_for_status()
        result = response.json()
        return result["embedding"]

    def __get_answer_from_context(self, question: str, articles: ArticlesWithScoreList):
        data = self.get_question_answer_request_data(question, articles)

        response = httpx.post(self.qa_url, json=data, timeout=None)
        response.raise_for_status()
        result = response.json()
        return result["response"]

    async def get_answer(self, question: str, articles: ArticlesWithScoreList):
        yield self.__get_answer_from_context(question, articles)
