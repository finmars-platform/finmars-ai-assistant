import os


def get_api_key(base_url: str | None):
    if (base_url is None) or ("https://api.openai.com/v1" == base_url):
        return os.getenv("OPENAI_API_KEY")

    elif "https://openrouter.ai/api/v1" == base_url:
        return os.getenv("OPENROUTER_API_KEY")

    elif "https://api.cerebras.ai/v1" == base_url:
        return os.getenv("CEREBRAS_API_KEY")

    return ""
