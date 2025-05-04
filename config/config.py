# LLM model used
MODEL_NAME = "gemini-2.0-flash-001"

# LLM supported languages
LANGUAGES = [
    "Same language as website", "Arabic", "Bengali", "Bulgarian", "Chinese", "Croatian", "Czech",
    "Danish", "Dutch", "English", "Estonian", "Finnish", "French", "German", "Greek", "Hebrew",
    "Hindi", "Hungarian", "Indonesian", "Italian", "Japanese", "Korean", "Latvian", "Lithuanian",
    "Norwegian", "Polish", "Portuguese", "Romanian", "Russian", "Serbian", "Slovak", "Slovenian",
    "Spanish", "Swahili", "Swedish", "Thai", "Turkish", "Ukrainian", "Vietnamese"
]

# LLM context length
MAX_CONTEXT_LENGTH = 1000000

# Keyword generation limit, for prevention
MAX_OUTPUT_TOKENS = 2000

# System prompt token size
SYSTEM_PROMPT_LENGTH = 400

# Max links to extract and scrape
MAX_LINKS_TO_SCRAPE = 400
