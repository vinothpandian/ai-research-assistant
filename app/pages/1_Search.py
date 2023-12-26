import feedparser
import streamlit as st

from app.db import db
from app.schema import ArticlesList
from app.vector_db import vector_db

st.set_page_config(page_title="Search", page_icon="🔍", layout="wide")

st.title("Search for research papers")

query = st.text_input("Enter your query")

if query:
    clean_query = "+".join(query.split())
    feed = feedparser.parse(
        f"https://export.arxiv.org/api/query?search_query=all:{clean_query}&start=0&max_results=10")

    total_result = feed.get("feed", {}).get("opensearch_totalresults", 0)

    articles = ArticlesList.model_validate(feed.get('entries', []))

    st.write(f"Found {total_result} results")


    def save_article(article):
        try:
            db.save_article(article)
            vector_db.save_article(article)
            st.toast("Article saved")
        except Exception as e:
            st.error(f"Error saving article: {e}")


    for i, article in enumerate(articles):
        with st.container():
            st.header(article.title)
            st.caption(", ".join(author.name for author in article.authors))
            st.write(article.link)
            st.caption(article.summary)
            columns = st.columns(6)
            columns[-1].button("Save to library", key=f"save_{i}", use_container_width=True, on_click=save_article,
                               args=(article,))
            st.divider()
