import streamlit as st

from app.streamlit_components.keyword_results import search_trigger
from app.streamlit_components.app_utils import api_key_input, extraction_information
from app.streamlit_components.extraction_form import form_html_extraction
from app.streamlit_components.keyword_generation_form import form_keywords_generation
from app.streamlit_components.sidebar import sidebar_guide, sidebar_details


def streamlit_app():
    st.session_state.setdefault('state', 'extraction')

    sidebar_guide()

    sidebar_details()

    st.logo(image='resources/transparent_logo.png', size="large")
    st.title('AI SEO keyword generator')

    gemini_api_key = api_key_input()

    form_html_extraction(gemini_api_key)

    if all(key in st.session_state for key in ("html_documents", "url_input", "slider_number_of_htmls")):
        extraction_information()

    if ( st.session_state['state'] == "keyword_generation" or
            (st.session_state['state'] == "searching" and "keywords" in st.session_state) ):
        form_keywords_generation(gemini_api_key)

    if st.session_state['state'] == "searching" and "keywords" in st.session_state:
        search_trigger()
        st.subheader("Copy keywords from below", divider="gray")
        st.write(st.session_state['keywords'])
