import streamlit as st

from app.lib.app import api_client
from core.schema.article import CreateArticle
from core.schema.arxiv import ArxivArticle

st.set_page_config(page_title="Search", page_icon="🔍", layout="wide")

st.title("Search Arxiv")

query = st.text_input("Search for research articles")

if query:
    data = api_client.search_articles(query=query)

    st.write(f"Found {data.total_items} results")

    def save_article(arxiv_article: ArxivArticle):
        try:
            article_to_create = CreateArticle(
                arxiv_id=arxiv_article.id,
                title=arxiv_article.title,
                abstract=arxiv_article.summary,
                link=arxiv_article.link,
                published=arxiv_article.published,
                authors=[author.name for author in arxiv_article.authors],
            )
            api_client.create_article(article_to_create)
            st.toast("Article added to library")
        except Exception as e:
            st.error(f"Error adding article: {e}")

    for i, article in enumerate(data.items):
        with st.container():
            st.header(article.title)
            st.caption(", ".join(author.name for author in article.authors))
            st.write(article.link)
            st.caption(article.summary)
            columns = st.columns(6)
            columns[-1].button(
                "Add to library", key=f"save_{i}", use_container_width=True, on_click=save_article, args=(article,)
            )
            st.divider()
