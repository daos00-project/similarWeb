import streamlit as st
from urllib.parse import quote_plus


@st.fragment
def search_trigger():
    with st.container(border=True):
        st.header("SEO keywords", divider="gray")
        chosen_keywords = st.pills(
            label="Generated Keywords :material/key:",
            default=st.session_state['keywords'][:10],
            options=st.session_state['keywords'],
            selection_mode="multi",
            key="keyword_pills"
        )
        st.markdown(f"Your selected options: {chosen_keywords}.")

        if chosen_keywords:
            keywords_str = ", ".join(chosen_keywords)
            encoded_query = quote_plus(keywords_str) + ' -filetype:pdf'
            st.link_button("Search in browser", f"https://www.google.com/search?q={encoded_query}")
