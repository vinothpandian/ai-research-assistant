import contextlib

import streamlit as st

from app.utils.app import api_client
from core.schema.article import ArticlesWithScoreList

st.set_page_config(page_title="Research Assistant", page_icon="🥼")

st.header("Search through your library")

if "question" not in st.session_state:
    st.session_state.question = ""

search_option = st.radio(
    "Search option",
    ["Semantic search", "Ask a question"],
    horizontal=True,
)
st.text_input(label=search_option, key="question")
score_threshold = 0.1

with st.expander("Advanced options"):
    score_threshold = st.slider("Search match threshold", 0.0, 1.0, 0.1, 0.05)

title = ""


def render_articles(articles: ArticlesWithScoreList):
    st.divider()

    if len(articles) > 0:
        st.markdown(f"**Found {len(articles)} results**")

    if len(articles) == 0 and st.session_state.question:
        st.write("No results found")

    if len(articles) == 0 and not st.session_state.question:
        st.write("Your library is empty")

    for article in articles:
        with st.container():
            st.subheader(article.title)
            st.caption(", ".join(article.authors))
            with contextlib.suppress(AttributeError):
                st.write("Similarity score: ", article.score)
            st.write(article.link)
            st.caption(article.ai_summary)
            st.divider()


if st.session_state.question and search_option == "Semantic search":
    result = api_client.semantic_search(st.session_state.question, score_threshold, with_answer=False)
    data = next(iter(result), [])
    render_articles(data)

placeholder = st.empty()
if st.session_state.question and search_option == "Ask a question":
    search_results = []
    answer = ""
    result = api_client.semantic_search(st.session_state.question, score_threshold, with_answer=True)
    container = placeholder.container(border=True)
    container.subheader("Answer")
    answer_placeholder = container.empty()
    answer_placeholder.write("Loading...")
    for i, item in enumerate(result):
        if i == 0:
            search_results = item
            render_articles(search_results)
            continue

        if not item:
            continue

        answer += str(item)
        answer_placeholder.write(answer)

if title:
    st.header(title)
