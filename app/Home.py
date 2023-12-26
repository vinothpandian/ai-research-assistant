import streamlit as st
from transformers import pipeline

from app.vector_db import vector_db

st.set_page_config(page_title="Research Assistant", page_icon="🥼")

st.header("Search through your research papers")

q = st.text_input("Search in natural language")

summarizer = pipeline("summarization", model="Falconsai/text_summarization")

if q:
    articles = vector_db.semantic_search(q)
    for article in articles:
        with st.container():
            st.header(article.payload['title'])
            st.write(article.score)
            st.caption(", ".join(author['name'] for author in article.payload['authors']))
            st.write(article.payload['link'])
            st.caption(article.payload['summary'])
            summarize = st.button("Summarize", key=article.id)
            if summarize:
                with st.container(border=True):
                    st.write(summarizer(article.payload['summary'], max_length=200, min_length=30, do_sample=False)[0][
                                 'summary_text'])

            st.divider()
