import streamlit as st

from app.utils.app import api_client

st.set_page_config(page_title="Research Assistant", page_icon="🥼")

if "start" not in st.session_state:
    st.session_state.start = 0
limit = 10

page_num = (st.session_state.start // limit) + 1

st.header("Your library")
data = api_client.get_articles(start=st.session_state.start, limit=limit)
st.write(f"Total articles: {data.total_items}")


def go_to_next_page():
    st.session_state.start += limit


def go_to_previous_page():
    st.session_state.start -= limit


columns = st.columns(6)
with columns[0]:
    st.button("Prev", on_click=go_to_previous_page, disabled=page_num == 1, use_container_width=True)
with columns[-1]:
    st.button(
        "Next",
        on_click=go_to_next_page,
        disabled=st.session_state.start + limit >= data.total_items,
        use_container_width=True,
    )

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
        if not article.embeddings_generated:
            st.write("Article not ready for semantic search yet")

        hide_ai_summary = st.toggle("Show abstract", key=f"show_ai_{article.id}")
        if hide_ai_summary:
            st.write("Abstract:")
            st.caption(article.abstract)
        elif article.ai_summary:
            st.write("AI generated summary:")
            st.caption(article.ai_summary)
        else:
            st.caption("AI summary is being generated...")

        columns = st.columns(3)
        columns[0].button(
            "Regenerate summary",
            key=f"summary_{article.id}",
            use_container_width=True,
            on_click=api_client.regenerate_summary,
            args=(article.id,),
        )

        columns[1].button(
            "Regenerate search index",
            key=f"embeddings_{article.id}",
            use_container_width=True,
            on_click=api_client.regenerate_embeddings,
            args=(article.id,),
        )

        columns[-1].button(
            "Remove from library",
            key=f"save_{article.id}",
            use_container_width=True,
            on_click=remove_article,
            type="primary",
            args=(article.id,),
        )
        st.divider()
