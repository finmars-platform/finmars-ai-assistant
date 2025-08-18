import hashlib
import os

ACTIVATE_PUBLIC_NAME = os.getenv("ACTIVATE_PUBLIC_NAME", "false").lower() == "true"

def hash_string(input_string):
    """Hashes a string using SHA256."""
    if input_string is None:
        return None
    return hashlib.sha256(input_string.encode("utf-8")).hexdigest()