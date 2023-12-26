import streamlit as st

from app.db import db
from app.vector_db import vector_db

st.set_page_config(page_title="Library", page_icon="📚")

st.title("Your library")

articles = db.get_articles()

def remove_article(article):
    try:
        db.remove_article(article)
        vector_db.remove_article(article)
        st.toast("Article removed")
    except Exception as e:
        st.error(f"Error removing article: {e}")

for i, article in enumerate(articles):
    with st.container():
        st.header(article.title)
        st.caption(", ".join(author['name'] for author in article.authors))
        st.write(article.link)
        st.caption(article.summary)
        columns = st.columns(4)
        columns[-1].button("Remove from library", key=f"save_{i}", use_container_width=True, on_click=remove_article,
                           args=(article,))
        st.divider()
