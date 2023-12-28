import streamlit as st

from app.lib.app import api_client

st.set_page_config(page_title="Research Assistant", page_icon="🥼")

st.header("Your library")

data = api_client.get_articles()
st.write(f"Total articles: {data.total_items}")
st.divider()


def remove_article(article_id: str):
    try:
        api_client.delete_article(article_id)
        st.toast("Article removed")
    except Exception as e:
        st.error(f"Error removing article: {e}")


for article in data.items:
    with st.container():
        st.subheader(article.title)
        st.caption(", ".join(article.authors))
        st.write(article.link)
        st.caption(article.ai_summary)
        columns = st.columns(4)
        columns[-1].button(
            "Remove from library",
            key=f"save_{article.id}",
            use_container_width=True,
            on_click=remove_article,
            type="primary",
            args=(article.id,),
        )
        st.divider()
