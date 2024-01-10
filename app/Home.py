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


def render_articles(articles: ArticlesWithScoreList, header: str | None = None):
    container = st.container()

    if header:
        container.subheader(header)

    if not header:
        st.divider()

        if len(articles) > 0:
            container.markdown(f"**Found {len(articles)} results**")

    if len(articles) == 0 and st.session_state.question:
        container.write("No results found")

    if len(articles) == 0 and not st.session_state.question:
        container.write("Your library is empty")

    for article in articles:
        with container.container():
            st.subheader(article.title)
            st.caption(", ".join(article.authors))
            with contextlib.suppress(AttributeError):
                if not header:
                    st.write("Similarity score: ", round(article.score, 3))
            st.write(article.link)
            st.caption(article.abstract if header else article.ai_summary)
            if expand := st.expander("Contexts"):
                for context in article.chunks:
                    expand.caption(context)
                    expand.divider()

            st.divider()


if st.session_state.question and search_option == "Semantic search":
    articles_result = api_client.semantic_search(st.session_state.question, score_threshold)
    render_articles(articles_result)

placeholder = st.empty()
if st.session_state.question and search_option == "Ask a question":
    answer = ""
    qa_result = api_client.question_answering(st.session_state.question, score_threshold)
    articles = api_client.semantic_search(st.session_state.question, score_threshold)
    container = placeholder.container(border=True)
    container.subheader("Answer")
    answer_placeholder = container.empty()
    answer_placeholder.write("Loading...")
    render_articles(articles, header="Context")
    item: str
    for item in qa_result:
        answer += str(item)
        answer_placeholder.write(answer)

if title:
    st.header(title)
