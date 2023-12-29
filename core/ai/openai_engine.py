import json

from openai import OpenAI

from core.ai.ollama_engine import OllamaEngine
from core.schema.article import Article, ArticlesWithScoreList
from core.settings import Settings


class OpenAIEngine(OllamaEngine):
    def __init__(self, settings: Settings):
        super().__init__(settings)
        self.client = OpenAI(
            api_key=settings.openai.key,
        )

    def get_summary(self, article: Article):
        messages = [
            {
                "role": "system",
                "content": """You are a helpful research assistant. You will help me summarize the
                abstract from the following research paper. The summary you generate should be
                in english and should be grammatically correct. The summary should be in complete
                sentences and should not contain any bullet points or lists. The summary should be
                in the third person and should not contain any personal pronouns.""",
            },
            {
                "role": "user",
                "content": f"Title: {article.title}\nAbstract: {article.abstract}",
            },
        ]

        # noinspection PyArgumentList
        response = self.client.completions.create(
            model=self.summarizer_model,
            messages=messages,
            stream=False,
        )

        return response["choices"][0]["message"]["content"]

    def get_embeddings(self, text: str):
        request_data = super().get_embeddings_request_data(text)
        prompt = request_data["prompt"]

        # noinspection PyArgumentList
        response = self.client.embeddings.create(model=self.embedding_model, input=prompt, encoding_format="float")

        return response["embedding"]

    async def get_answer(self, question: str, articles: ArticlesWithScoreList, with_answer: bool = False):
        response = dict(articles=articles.model_dump(mode="json"))

        yield json.dumps(response)

        if not with_answer:
            return

        abstracts = self.get_question_info(articles)

        messages = [
            {
                "role": "system",
                "content": f"""You are a helpful research assistant. You will help me answer the
                following question based on the abstracts from the following research papers.
                The answer you generate should be in english and should be grammatically correct.
                The answer should be in complete sentences. The answer can be in markdown and
                can contain any bullet points or lists. The answer should be in the third person
                 and should not contain any personal pronouns. The answer should only contain
                 information that is present in the abstracts. The answer should not contain
                 any information that is not present in the abstracts.

                Abstracts: {abstracts}""",
            },
            {
                "role": "user",
                "content": f"Question: {question}",
            },
        ]

        # noinspection PyArgumentList
        response = self.client.completions.create(
            model=self.qa_model,
            messages=messages,
            stream=True,
        )

        for chunk in response:
            value = chunk.choices[0].delta.content
            yield json.dumps(dict(answer=value))
