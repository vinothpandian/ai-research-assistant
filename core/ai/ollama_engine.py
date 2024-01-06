import contextlib
import json
from json import JSONDecodeError
from typing import Dict

import httpx

from core.ai.base_engine import HuggingfaceAIEngine
from core.schema.article import Article, ArticlesWithScoreList


class OllamaEngine(HuggingfaceAIEngine):
    def get_summarization_request_data(self, article: Article) -> Dict[str, str]:
        prompt = f""""
        {article.abstract}
        ###
        Generate a summary of the above text from a research paper in 100 to 200 words. Do no
        include any other information other than the summary. The summary should be in your own
        words and should not be a copy of the abstract. The summary should be in English and
        should be grammatically correct. The summary should be in complete sentences and should
        not contain any bullet points or lists. The summary should be in the third person and
        should not contain any personal pronouns.
        """

        return {"model": self.summarizer_model, "prompt": prompt, "stream": False}

    def get_embeddings_request_data(self, text: str) -> Dict[str, str]:
        request_data = super().get_embeddings_request_data(text)
        return {"model": self.embedding_model, "prompt": request_data["prompt"], "stream": False}

    def get_question_answer_request_data(self, question: str, articles: ArticlesWithScoreList) -> Dict[str, str]:
        request_data = super().get_question_answer_request_data(question, articles)

        prompt = f"""Answer the question based on the context given below. The answer should only contain information that is present in the context. The answer should not contain any information that is not present in the context.

        ###
        {request_data['prompt']}"""  # noqa: E501

        return {"model": self.qa_model, "prompt": prompt, "stream": True}

    async def get_answer(self, question: str, articles: ArticlesWithScoreList):
        data = self.get_question_answer_request_data(question, articles)

        async with httpx.AsyncClient() as client:
            request = client.build_request("POST", self.qa_url, json=data, timeout=None)
            r = await client.send(request, stream=True)
            async for chunk in r.aiter_text():
                with contextlib.suppress(JSONDecodeError):
                    json_chunk = json.loads(chunk)
                    yield json_chunk["response"]
