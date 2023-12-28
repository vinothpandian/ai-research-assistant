import contextlib
import json
from json import JSONDecodeError

import httpx
from loguru import logger

from core.schema.ai import ModelType
from core.schema.article import Article, ArticlesWithScoreList
from core.settings import settings

MODEL_TYPE: ModelType = "summarizer"
if settings.EMBEDDING_MODEL in {"llama2", "dolphin-phi", "phi", "mistral", "orca-mini"}:
    MODEL_TYPE = "general"


def generate_summarization_prompt(article: Article) -> str:
    if MODEL_TYPE == "summarizer":
        return article.abstract

    return f""""
    {article.abstract}
    ###
    Generate a summary of the above text from a research paper in 100 to 200 words. Do no
    include any other information other than the summary. The summary should be in your own
    words and should not be a copy of the abstract. The summary should be in English and
    should be grammatically correct. The summary should be in complete sentences and should
    not contain any bullet points or lists. The summary should be in the third person and
    should not contain any personal pronouns.
    """


def generate_question_answer_prompt(question: str, articles: ArticlesWithScoreList) -> str:
    abstracts = "\n\n".join([article.abstract for article in articles])

    prompt = f"""Context: {abstracts}

    Question: {question}?

    Answer: """

    if MODEL_TYPE == "summarizer":
        return prompt

    return f"""Answer the question based on the context given below. The answer should only contain information that is present in the context. The answer should not contain any information that is not present in the context.

    ###
    {prompt}"""  # noqa: E501


def get_summary(prompt: str):
    data = {"model": settings.SUMMARIZER_MODEL, "prompt": prompt, "stream": False}

    logger.debug(f"Sending request to {settings.SUMMARIZER_URL} with data {data}")

    response = httpx.post(settings.SUMMARIZER_URL, json=data, timeout=None)
    response.raise_for_status()
    result = response.json()
    return result["response"]


def get_answer_from_context(prompt: str):
    data = {"prompt": prompt}

    logger.debug(f"Sending request to {settings.QA_URL} with data {data}")

    response = httpx.post(settings.QA_URL, json=data, timeout=None)
    response.raise_for_status()
    result = response.json()
    return result["response"]


def get_embeddings(prompt: str):
    data = {"model": settings.EMBEDDING_MODEL, "prompt": prompt, "stream": False}

    logger.debug(f"Sending request to {settings.EMBEDDING_URL} with data {data}")

    response = httpx.post(settings.EMBEDDING_URL, json=data, timeout=None)
    response.raise_for_status()
    result = response.json()
    return result["embedding"]


async def get_answer(question: str, articles: ArticlesWithScoreList, with_answer: bool = False):
    response = dict(articles=articles.model_dump(mode="json"))

    yield json.dumps(response)

    if not with_answer:
        return

    question_prompt = generate_question_answer_prompt(question, articles)

    if MODEL_TYPE == "summarizer":
        logger.debug(f"Sending request to {settings.QA_URL} with data {question_prompt}")
        yield json.dumps(dict(answer=get_answer_from_context(question_prompt)))
        return

    async with httpx.AsyncClient() as client:
        data = {"model": settings.QA_MODEL, "prompt": question_prompt, "stream": True}
        logger.debug(f"Streaming response from {settings.QA_URL} with data {data}")
        request = client.build_request("POST", settings.QA_URL, json=data, timeout=None)
        r = await client.send(request, stream=True)
        async for chunk in r.aiter_text():
            with contextlib.suppress(JSONDecodeError):
                json_chunk = json.loads(chunk)
                yield json.dumps(dict(answer=json_chunk["response"]))
