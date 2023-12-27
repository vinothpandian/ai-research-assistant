import httpx

from core.schema.ai import ModelType
from core.schema.article import Article, ArticlesList
from core.settings import settings


def generate_summarization_prompt(article: Article, model_type: ModelType = "summarizer") -> str:
    if model_type == "summarizer":
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


def generate_question_answer_prompt(question: str, articles: ArticlesList, model_type: ModelType = "summarizer") -> str:
    abstracts = "\n\n".join([article.abstract for article in articles])
    if model_type == "summarizer":
        return abstracts

    return f""""
    Context:
    {abstracts}
    ###
    Answer the following question based on the above text. Do not include any other
    information other than the answer to the question. The answer should be in your own
    words and should not be a copy of the abstract. The answer should be in English and
    should be grammatically correct. The answer should be in complete sentences and should
    not contain any bullet points or lists.
    ###
    Question: {question}
    """


def get_summary(prompt: str):
    data = {'model': settings.SUMMARIZER_MODEL, 'prompt': prompt, 'stream': False}

    response = httpx.post(settings.SUMMARIZER_URL, json=data, timeout=None)
    response.raise_for_status()

    return response.json()


def get_embeddings(prompt: str):
    data = {'model': settings.EMBEDDING_MODEL,
            'prompt': prompt,
            'stream': False}

    response = httpx.post(settings.EMBEDDING_URL, json=data, timeout=None)
    response.raise_for_status()

    return response.json()
