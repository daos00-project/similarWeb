import re
from google import genai
from config.config import MAX_CONTEXT_LENGTH, MODEL_NAME, SYSTEM_PROMPT_LENGTH


def llm_token_limit_check(gemini_api_key, html_documents):
    joined_html_documents = ""
    for idx, html in enumerate(html_documents):
        joined_html_documents += f"\n{idx + 1}. HTML document\n" + html

    try:
        total_tokens = get_llm_token_count(gemini_api_key, joined_html_documents)
        if total_tokens and (total_tokens > (MAX_CONTEXT_LENGTH - SYSTEM_PROMPT_LENGTH)):
            return False
    except Exception as e:
        raise Exception(e)

    return total_tokens


def get_llm_token_count(gemini_api_key, text: str):
    try:
        client = genai.Client(api_key=gemini_api_key)
        response = client.models.count_tokens(
            model=MODEL_NAME,
            contents=text,
        )
        return response.total_tokens
    except Exception as e:
        code = re.search(r"'code': ([\d]+),", str(e)).group(1)
        msg = re.search(r"'message': '(.*?\.)'", str(e)).group(1)
        if msg and code:
            raise Exception(
                f"Could not calculate total HTML tokens with gemini API. Error code: {code}. Message: {msg}")
        else:
            raise Exception("Unknown exception calculating tokens.")
