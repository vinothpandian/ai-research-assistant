import json
from typing import Dict

import httpx

from core.schema.article import Article, ArticlesWithScoreList
from core.settings import Settings


class BaseAIEngine:
    def __init__(self, settings: Settings):
        self.SUMMARIZER_URL = settings.SUMMARIZER_URL
        self.SUMMARIZER_MODEL = settings.SUMMARIZER_MODEL

        self.EMBEDDING_URL = settings.EMBEDDING_URL
        self.EMBEDDING_MODEL = settings.EMBEDDING_MODEL

        self.QA_URL = settings.QA_URL
        self.QA_MODEL = settings.QA_MODEL

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

        response = httpx.post(self.SUMMARIZER_URL, json=data, timeout=None)
        response.raise_for_status()
        result = response.json()
        return result["response"]

    def get_embeddings(self, text: str):
        data = self.get_embeddings_request_data(text)

        response = httpx.post(self.EMBEDDING_URL, json=data, timeout=None)
        response.raise_for_status()
        result = response.json()
        return result["embedding"]

    def __get_answer_from_context(self, question: str, articles: ArticlesWithScoreList):
        data = self.get_question_answer_request_data(question, articles)

        response = httpx.post(self.QA_URL, json=data, timeout=None)
        response.raise_for_status()
        result = response.json()
        return result["response"]

    async def get_answer(self, question: str, articles: ArticlesWithScoreList, with_answer: bool = False):
        response = dict(articles=articles.model_dump(mode="json"))

        yield json.dumps(response)

        if not with_answer:
            return

        yield json.dumps(dict(answer=self.__get_answer_from_context(question, articles)))
