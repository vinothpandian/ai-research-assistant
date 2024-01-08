from typing import Dict, List

import httpx

from core.schema.article import Article
from core.settings import Settings


class HuggingfaceAIEngine:
    def __init__(self, settings: Settings):
        self.summarizer_url = settings.summarizer.url
        self.summarizer_model = settings.summarizer.model

        self.embedding_url = settings.embedding.url
        self.embedding_model = settings.embedding.model

        self.qa_url = settings.qa.url
        self.qa_model = settings.qa.model

    def get_summarization_request_data(self, article: Article) -> Dict[str, str]:
        return {"prompt": article.abstract}

    def get_embeddings_request_data(self, chunks: List[str]) -> dict:
        return {"prompt": chunks}

    def get_question_answer_request_data(self, question: str, contexts: List[str]) -> Dict[str, str]:
        prompt_context = self.get_question_info(contexts)

        prompt = f"""Context: {prompt_context}

        Question: {question}?

        Answer: """

        return {"prompt": prompt}

    def get_question_info(self, contexts: List[str]):
        return "\n\n".join(contexts)

    def get_summary(self, article: Article):
        data = self.get_summarization_request_data(article)

        response = httpx.post(self.summarizer_url, json=data, timeout=None)
        response.raise_for_status()
        result = response.json()
        return result["response"]

    def get_embeddings(self, chunks: List[str]):
        data = self.get_embeddings_request_data(chunks)

        response = httpx.post(self.embedding_url, json=data, timeout=None)
        response.raise_for_status()
        result = response.json()
        return result["embedding"]

    def __get_answer_from_context(self, question: str, contexts: List[str]):
        data = self.get_question_answer_request_data(question, contexts)

        response = httpx.post(self.qa_url, json=data, timeout=None)
        response.raise_for_status()
        result = response.json()
        return result["response"]

    async def get_answer(self, question: str, contexts: List[str]):
        yield self.__get_answer_from_context(question, contexts)
