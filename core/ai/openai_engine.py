from typing import List

from openai import OpenAI

from core.ai.ollama_engine import OllamaEngine
from core.schema.article import Article
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
        response = self.client.chat.completions.create(
            model=self.summarizer_model,
            messages=messages,
            stream=False,
        )

        return response["choices"][0]["message"]["content"]

    def get_embeddings(self, chunks: List[str]):
        request_data = super().get_embeddings_request_data(chunks)
        prompt = request_data["prompt"]

        # noinspection PyArgumentList
        response = self.client.embeddings.create(model=self.embedding_model, input=prompt, encoding_format="float")

        return response["embedding"]

    async def get_answer(self, question: str, contexts: List[str]):
        abstracts = self.get_question_info(contexts)

        messages = [
            {
                "role": "system",
                "content": """You are a helpful research assistant. You will help me answer the
                questions based on the extracted contexts from the following research papers.
                The answer you generate should be in english and should be grammatically correct.
                The answer should be less than 500 characters and should never exceed 500 characters.
                The answer should be in complete sentences. The answer can be in markdown and
                can contain any bullet points or lists. The answer should be in the third person
                 and should not contain any personal pronouns. The answer should only contain
                 information that is present in the context provided before the question. You will
                 always add references to the answer in [1, 2, 3..] format if you use any information
                 from the context and always add references at the end in APA citation format. You will
                 never repeat the same reference multiple times. You will only add references you used and
                 keep the references list unique.""",
            },
            {
                "role": "user",
                "content": f"""Contexts: {abstracts}

                ###
                Question: {question}""",
            },
        ]

        # noinspection PyArgumentList
        response = self.client.chat.completions.create(
            model=self.qa_model,
            messages=messages,
            stream=True,
        )

        for chunk in response:
            if chunk.choices[0].finish_reason is not None:
                yield ""
                break

            yield chunk.choices[0].delta.content
