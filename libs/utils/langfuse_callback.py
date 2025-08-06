import os
from typing import List, Optional
from langfuse.langchain import CallbackHandler


def get_langfuse_callbacks() -> List:
    """
    Get Langfuse callbacks if all required environment variables are set.
    
    Returns:
        List containing CallbackHandler if environment variables exist, 
        empty list otherwise.
    """
    LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")
    LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "")
    
    # Only create and use langfuse_handler if all required env vars exist
    if LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY and LANGFUSE_HOST:
        return [CallbackHandler()]
    
    return []