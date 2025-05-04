import streamlit as st


@st.fragment
def api_key_input():
    return st.text_input('Gemini API Key 🔑', type="password",
                         help='You can get your API key from https://aistudio.google.com/app/apikey.')


def extraction_information():
    if len(st.session_state['html_documents']) == st.session_state['slider_number_of_htmls']:
        st.success(f"All HTML documents extracted for {st.session_state['url_input']}!", icon="✅")
    elif len(st.session_state['html_documents']) < st.session_state['slider_number_of_htmls']:
        if st.session_state['token_limit_flag']:
            st.warning(
                f"Token limit exceeded. Less HTML documents used for keyword generation of {st.session_state['url_input']}.",
                icon="⚠️")
        else:
            st.warning(
                f"Less HTML documents used for keyword generation of {st.session_state['url_input']}. Could not extract more.",
                icon="⚠️")

    if 'html_token_count' in st.session_state and st.session_state['html_token_count']:
        st.info(f"HTML token count is {st.session_state['html_token_count']}.")

    with st.expander("URLs of extracted HTML documents"):
        tab_names = []
        for i in range(len(st.session_state['html_documents'])):
            tab_names.append(f"page{i+1}")
        tabs = st.tabs(tab_names)
        for idx, (label, tab) in enumerate(zip(st.session_state['html_documents'], tabs)):
            with tab:
                tab.write(label.splitlines()[0])
