import streamlit as st

from model.llm_inference.keyword_generation import llm_init, keyword_generation
from config.config import LANGUAGES


def form_keywords_generation(gemini_api_key):
    keywords = None
    joined_html_documents = ""
    for idx, html in enumerate(st.session_state['html_documents']):
        joined_html_documents += f"\n{idx + 1}. HTML document\n" + html

    if not joined_html_documents:
        st.error('No HTML documents. Please try extracting HTML again.', icon="🚨")
        return

    with st.form(key='key_generation_form'):
        st.header("AI keyword generator", divider="gray")
        st.session_state['temperature'] = st.slider(
            label='Temperature :material/thermometer:',
            min_value=0.0,
            max_value=2.0,
            step=0.1,
            value=1.0,
            help="Controls creativity in responses. 0.0 = deterministic, 1.0 = default, 2.0 = creative and varied"
        )
        st.session_state['presence_penalty'] = st.slider(
            label='Presence penalty :material/recycling:',
            min_value=-2.0,
            max_value=2.0,
            step=0.1,
            value=0.0,
            help="Controls variety in responses. -2.0 = low variety, 0 = default, 2.0 = high variety"
        )

        # Gemini presence_penalty parameter range is from -2.0 to 2.0(excluded).
        # For UX and aesthetic reasons, the slider max will be kept at 2.0
        # Source: https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/inference
        if st.session_state['presence_penalty'] == 2.0:
            st.session_state['presence_penalty'] = 1.99
        st.session_state['number_of_keywords'] = st.slider(
            label='Number of keywords to generate :material/format_list_bulleted:',
            min_value=5,
            max_value=30,
            step=1,
            value=10
        )

        col1, col2 = st.columns(spec=2, vertical_alignment="bottom")
        with col2:
            st.session_state['language'] = st.selectbox(
                label="Keyword language :material/translate:",
                options=LANGUAGES,
                help="In what language should the keywords be generated in?"
            )

        if col1.form_submit_button("Generate keywords"):
            if not gemini_api_key:
                st.error('Can\'t generate keywords without a Gemini API key!', icon="🚨")
            else:
                with st.status("Generating keywords...", expanded=True) as status:
                    try:
                        llm = llm_init(
                            gemini_api_key, st.session_state['language'], st.session_state['number_of_keywords'],
                            st.session_state['temperature'], st.session_state['presence_penalty']
                        )
                        keywords = keyword_generation(llm, joined_html_documents)
                    except Exception as e:
                        st.error(e)
                        return

                    if not keywords:
                        status.update(
                            label="Generate keywords error", state="error", expanded=False
                        )
                        st.warning('No keywords found. Enter a different URL or try again')
                        return
                    else:
                        status.update(
                            label="Keywords generated!", state="complete", expanded=False
                        )

    if keywords:
        st.session_state['state'] = "searching"
        st.session_state['keywords'] = keywords[0][:st.session_state['number_of_keywords']]
