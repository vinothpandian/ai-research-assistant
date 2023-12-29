import streamlit as st

from app.lib.app import api_client
from core.schema.article import CreateArticle
from core.schema.semantic_scholar import SemanticScholarArticle

st.set_page_config(page_title="Search", page_icon="🔍", layout="wide")

st.title("Search Semantic Scholar")

if "start" not in st.session_state:
    st.session_state.start = 0
limit = 10


def go_to_next_page():
    st.session_state.start += limit


def go_to_previous_page():
    st.session_state.start -= limit


def save_article(ss_article: SemanticScholarArticle):
    try:
        article_to_create = CreateArticle(
            arxiv_id=ss_article.paperId,
            title=ss_article.title,
            abstract=ss_article.abstract,
            link=ss_article.url,
            published=ss_article.publicationDate,
            authors=[author.name for author in ss_article.authors],
        )
        api_client.create_article(article_to_create)
        st.toast("Article added to library")
    except Exception as e:
        st.error(f"Error adding article: {e}")


query = st.text_input("Search for research articles by title, author, DOI, etc.")

if query:
    st.divider()
    data = api_client.search_articles(query=query, start=st.session_state.start, limit=limit)

    columns = st.columns(6)
    with columns[0]:
        st.button("Prev", on_click=go_to_previous_page, disabled=st.session_state.start != 0, use_container_width=True)
    with columns[-1]:
        st.button(
            "Next",
            on_click=go_to_next_page,
            disabled=st.session_state.start + limit >= data.total_items,
            use_container_width=True,
        )

    st.write(f"Found {data.total_items} results")

    for i, article in enumerate(data.items):
        with st.container():
            st.header(article.title)
            st.caption(", ".join(author.name for author in article.authors))
            st.write(article.url)
            st.caption(article.abstract)
            columns = st.columns(6)
            columns[-1].button(
                "Add to library", key=f"save_{i}", use_container_width=True, on_click=save_article, args=(article,)
            )
            st.divider()
