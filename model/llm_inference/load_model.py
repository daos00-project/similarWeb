import openai
from keybert.llm import OpenAI
import streamlit as st

example_prompt = """
    <s>[INST]
    I have the following description:
    - This webpage is a comprehensive entertainment hub offering extensive information on movies, TV shows, and celebrities. Visitors can explore trailers, interviews, and exclusive videos, enhancing their viewing experience. The site provides recommendations for what to watch, featuring popular streaming content and upcoming releases. It also highlights the most popular celebrities and their latest projects. Users can delve into editor's picks, discover new releases, and stay updated with the latest news in the entertainment industry. The platform is designed to cater to fans seeking detailed insights and engaging content about their favorite films, series, and stars.

    With the following candidate keywords:
    - movie trailers, TV shows, video player, streaming

    1. You are given a document with scraped HTMLs of a website and it's webpages.
    2. Your role is to provide the most relevant keywords that are present in this document in the same language as the document is.
    3. If there are candidate keywords, improve the candidate keywords to best describe the topic of the document.
    4. Separate keywords with commas.
    5. Make sure to only return exactly 10 keywords and say nothing else.
    6. For example, don't say: "Here are the keywords present in the description."
    [/INST] movies, TV shows, user reviews, trailers, streaming, new releases, series, popular celebrities, streaming, films</s>"""

keyword_prompt = """
    [INST]

    I have the following description:
    - [DOCUMENT]

    With the following candidate keywords:
    - [CANDIDATES]

    1. You are given a document with scraped HTMLs of a website and it's webpages.
    2. Your role is to provide the most relevant keywords that are present in this document in the same language as the document is.
    3. If there are candidate keywords, improve the candidate keywords to best describe the topic of the document.
    4. Separate keywords with commas.
    5. Make sure to return exactly 10 keywords and say nothing else.
    6. For example, don't say: "Here are the keywords present in the description."
    [/INST]
    """

prompt = example_prompt + keyword_prompt


# API_KEY = os.getenv("GEMINI_API_KEY")
# st.secrets["GEMINI_API_KEY"]
# MODEL_NAME = os.getenv("MODEL_GEMINI_PRO")
client = openai.OpenAI(
    api_key=st.secrets["API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
LLM = OpenAI(client, model="gemini-2.0-flash-001", prompt=prompt, chat=True)
