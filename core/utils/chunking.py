import contextlib
import re

import fitz
import httpx
from langchain.text_splitter import RecursiveCharacterTextSplitter
from loguru import logger

from core.schema.article import Article


def get_text_from_research_article(pdf_url: str):
    response = httpx.get(pdf_url, follow_redirects=True, timeout=None)
    response.raise_for_status()
    stream = response.content
    pdf_file = fitz.open(stream=stream, filetype="pdf")

    research_text = "\n\n".join([page.get_text() for page in pdf_file])
    ref_index = -1
    if matches := re.search(r"\nreferences\s*\n", research_text, re.IGNORECASE):
        ref_index = matches.start()

    return research_text[:ref_index]


def get_chunks_from_article(article: Article, chunk_size: int = 1_000):
    authors = ", ".join(article.authors)
    text = f"Title: {article.title}\n\nAuthors: {authors}\n\nAbstract: {article.abstract}"

    logger.debug(f"Text has pdf_url: {article.pdf_url is not None}")

    with contextlib.suppress(Exception):
        if article.pdf_url:
            logger.debug(f"Getting text from PDF for article {article.id} - {article.pdf_url}")
            text = get_text_from_research_article(article.pdf_url)
            logger.debug(f"Got text with {len(text)} characters from PDF for article {article.id}")

    character_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", " ", ""],
        chunk_size=chunk_size,
        chunk_overlap=0,
    )
    chunks = character_splitter.split_text(text)

    logger.debug(f"Split text into {len(chunks)} chunks")

    return chunks
