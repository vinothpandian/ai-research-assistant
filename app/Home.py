import contextlib
import json

import httpx
import streamlit as st

from core.schema.article import ArticlesList

st.set_page_config(page_title="Research Assistant", page_icon="🥼")

st.header("Search through your research papers")


search_option = st.radio(
    "",
    ["Semantic search", "Ask a question"],
    horizontal=True,
)
question = st.text_input(search_option)
score_threshold = st.slider("Search match threshold", 0.0, 1.0, 0.25, 0.05)


answer = ""
items = []

if not question:
    response = httpx.get("http://localhost:8000/articles/").json()
    items = response["items"]


if question and search_option == "Semantic search":
    response = httpx.get(
        "http://localhost:8000/articles/search/",
        params={
            "question": question,
            "score_threshold": score_threshold,
            "with_answer": False,
        },
    ).json()
    items = response.get("articles", [])

if question and search_option == "Ask a question":
    with httpx.stream(
        "GET",
        "http://localhost:8000/articles/search/",
        params={
            "question": question,
            "score_threshold": score_threshold,
            "with_answer": True,
        },
    ) as response:
        first_response = False

        for line in response.iter_text():
            if not first_response:
                items = json.loads(line).get("articles", [])
                first_response = True
                continue

            with contextlib.suppress(json.JSONDecodeError):
                part_answer = json.loads(line).get("answer", "")
                answer += part_answer


if answer and search_option == "Ask a question":
    with st.container(border=True):
        st.write("Answer to your question")
        st.caption(answer)

articles = ArticlesList.model_validate(items)
for article in articles:
    with st.container():
        st.header(article.title)
        st.caption(", ".join(article.authors))
        st.write(article.link)
        st.write("AI Generated Summary")
        st.caption(article.ai_summary)
        st.divider()


if not items:
    st.write("No results found")
