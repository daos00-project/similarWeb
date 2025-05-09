import re
import openai
from keybert import KeyLLM
from openai import OpenAI
from keybert.llm import OpenAI as keyLLM_OpenAI
from config.config import MODEL_NAME, MAX_OUTPUT_TOKENS
from utils.prompts import (
    get_user_prompt_default,
    get_system_prompt_default,
    get_user_prompt_language,
    get_system_prompt_language
)


def llm_init(gemini_api_key, language, number_of_keywords, temperature, presence_penalty):
    client = OpenAI(
        api_key=gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    if language == "Same language as website":
        keyllm_prompt = get_user_prompt_default(number_of_keywords)
        prompt = get_system_prompt_default(number_of_keywords)
    else:
        keyllm_prompt = get_user_prompt_language(number_of_keywords, language)
        prompt = get_system_prompt_language(number_of_keywords, language)

    llm = keyLLM_OpenAI(client, model=MODEL_NAME, system_prompt=prompt, prompt=keyllm_prompt,
                        generator_kwargs={"max_tokens": MAX_OUTPUT_TOKENS, "temperature": temperature,
                                          "presence_penalty": presence_penalty}, chat=True)
    return llm


def keyword_generation(llm, joined_html_documents):
    try:
        kw_model = KeyLLM(llm)
        keywords = kw_model.extract_keywords(joined_html_documents)
    except openai.AuthenticationError as e:
        msg = re.search(r"'message': '(.*?\.)'", e.message).group(1)
        raise Exception(f"AuthenticationError code: {e.status_code}, message: {msg}")
    except openai.RateLimitError as e:
        raise Exception(f"Rate limit exceeded, error code: {e.status_code}. Try again later.")
    except openai.APIConnectionError:
        raise Exception(f"Network error. Please try again.")
    except openai.BadRequestError as e:
        msg = re.search(r"'message': '(.*?\.)'", e.message).group(1)
        raise Exception(f"Invalid request code: {e.status_code}, message: {msg}")
    except (openai.OpenAIError, openai.APIError) as e:
        raise Exception(f"OpenAI API error: {e.status_code}. Please slow down and try again in a minute.")
    except Exception as e:
        raise Exception(f"Unexpected error. Please try a different API key: {str(e)}")

    return keywords
