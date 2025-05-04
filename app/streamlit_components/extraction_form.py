import streamlit as st
from model.url_crawler.crawler import Crawler
from model.llm_inference.token_utils import llm_token_limit_check
from utils.utilities_responses import check_webpage_response
from utils.utilities_url import check_url_string, reformat_url


def form_html_extraction(gemini_api_key):
    with st.form(key='extraction_form'):
        st.header("HTML documents scraper", divider="gray")
        url_input = st.text_input("Enter a website URL :material/border_color:",
                                  help='Enter URL in format https://www.example.com.')
        slider_number_of_htmls = st.slider(
            label='Number of HTML documents to extract :material/library_books:',
            min_value=1,
            max_value=10,
            step=1,
            value=5,
            help="⚠️ **Reminder:** More HTML documents means more token usage when generating keywords."
        )

        if st.form_submit_button("Extract HTML documents"):
            st.session_state['state'] = "extraction"
            st.session_state['token_limit_flag'] = False
            if not gemini_api_key:
                st.error(
                    'Missing Gemini API key! Enter your API key before extracting.',
                    icon='🚨')
                call_get_html.clear(url_input, slider_number_of_htmls, gemini_api_key)
                for key in ["html_documents", "html_token_count"]:
                    st.session_state.pop(key, None)
            else:
                gemini_api_key = gemini_api_key.strip()
                if url_input:
                    html_documents = []
                    stripped_url = url_input.strip()
                    if not check_url_string(stripped_url):
                        st.warning("Not a valid URL format. Enter in a correct format: https://www.example.com/.")
                    else:
                        st.session_state['url_input'] = reformat_url(stripped_url)
                        html_documents = call_get_html(st.session_state['url_input'], slider_number_of_htmls)

                    if html_documents:
                        mod_html_documents = check_token_limit(gemini_api_key, html_documents)
                        st.session_state['html_documents'] = mod_html_documents
                        st.session_state['slider_number_of_htmls'] = slider_number_of_htmls
                        st.session_state['state'] = "keyword_generation"
                    else:
                        call_get_html.clear(url_input, slider_number_of_htmls, gemini_api_key)
                        for key in ["html_documents", "html_token_count"]:
                            st.session_state.pop(key, None)
                else:
                    st.warning('Enter a website URL.')
        else:
            if not url_input and st.session_state['state'] == "idle":
                st.info('Enter a website URL.')

            if not gemini_api_key:
                st.warning(
                    'Please enter your Gemini API key before extracting. You can get your FREE API key from https://aistudio.google.com/app/apikey.',
                    icon='⚠')


@st.cache_data(show_spinner=False, max_entries=10)
def call_get_html(url, slider_number_of_htmls):
    with st.spinner("Processing...", show_time=True):
        process = st.empty()
        process.write("Checking input...")

        try:
            check_webpage_response(url)
        except Exception as e:
            st.error(e)
            process.write("Extraction end: Input error")
            return False
        else:
            process.write("Crawling links...")
            try:
                obj = Crawler(url, slider_number_of_htmls)
                if slider_number_of_htmls != 1:
                    obj.crawl_links()
            except Exception as e:
                st.error(e)
                process.write("Extraction end: Link extraction error")
                return False

            process.write("Scraping HTMLs...")
            try:
                html_documents = obj.scrape_htmls()
                process.empty()
            except Exception as e:
                st.error(e)
                process.write("Extraction end: HTML extraction error.")
                return False

    return html_documents


def check_token_limit(gemini_api_key, html_documents):
    try:
        number_of_htmls = len(html_documents)
        while html_documents:
            st.session_state['html_token_count'] = llm_token_limit_check(gemini_api_key, html_documents)
            if st.session_state['html_token_count']:
                if len(html_documents) < number_of_htmls:
                    st.session_state['token_limit_flag'] = True
                break
            else:
                html_documents.pop()

        if not html_documents:
            st.warning(
                f"Can't generate keywords for {st.session_state['url_input']}. HTML of given URL exceeds Gemini 2.0 Flash token limit. Enter a different URL.")
    except Exception as e:
        st.session_state['html_token_count'] = False
        st.info(e)

    return html_documents
