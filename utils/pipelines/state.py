import time
from typing import Dict, Tuple, Optional

# In-memory store for user-specific data
# key -> (bundle, exp_unix)
_store: Dict[str, Tuple[dict, int]] = {}


def save_bundle(key: str, bundle: dict, exp_unix: int) -> None:
    """Saves a user's data bundle to the in-memory store."""
    _store[key] = (bundle, exp_unix)


def get_bundle(key: str) -> Optional[dict]:
    """Retrieves a user's data bundle if it exists and has not expired."""
    item = _store.get(key)
    if not item:
        return None
    bundle, exp = item
    if int(time.time()) >= int(exp):
        _store.pop(key, None)
        return None
    return bundle


def make_key(email: str, name: str) -> str:
    """Creates a consistent key from user's email and name."""
    return f"email:{email.lower().strip()}::name:{(name or '').strip().lower()}"
