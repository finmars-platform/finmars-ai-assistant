import time
import asyncio
import aiohttp
import jwt
import os
from typing import Dict, Tuple, Optional
from urllib.parse import urlencode

# In-memory store for user-specific data
# key -> (bundle, exp_unix, refresh_token, refresh_exp)
_store: Dict[str, Tuple[dict, int, Optional[str], Optional[int]]] = {}

# Track running refresh tasks to avoid duplicates
_refresh_tasks: Dict[str, asyncio.Task] = {}


def save_bundle(
    key: str,
    bundle: dict,
    exp_unix: int,
    refresh_token: Optional[str] = None,
    refresh_exp: Optional[int] = None,
) -> None:
    """Saves a user's data bundle to the in-memory store and starts refresh task if needed."""
    _store[key] = (bundle, exp_unix, refresh_token, refresh_exp)

    # Start refresh task if we have a refresh token
    if refresh_token and refresh_exp:
        # Cancel existing task if any
        if key in _refresh_tasks:
            _refresh_tasks[key].cancel()

        # Start new refresh task
        _refresh_tasks[key] = asyncio.create_task(
            _schedule_token_refresh(key, exp_unix, refresh_token, refresh_exp)
        )


def get_bundle(key: str) -> Optional[dict]:
    """Retrieves a user's data bundle if it exists and has not expired."""
    item = _store.get(key)
    if not item:
        return None

    bundle, exp, refresh_token, refresh_exp = item
    current_time = int(time.time())

    # Check if access token has expired
    if current_time >= int(exp):
        # Remove expired entry
        _store.pop(key, None)
        # Cancel refresh task if exists
        if key in _refresh_tasks:
            _refresh_tasks[key].cancel()
            del _refresh_tasks[key]
        return None

    return bundle


async def _schedule_token_refresh(
    key: str, access_exp: int, refresh_token: str, refresh_exp: int
) -> None:
    """Schedule token refresh 2 minutes before access token expires."""
    try:
        current_time = int(time.time())
        refresh_time = access_exp - 120  # 2 minutes before expiry

        # If refresh time is in the past, refresh immediately
        wait_seconds = max(0, refresh_time - current_time)

        print(f"Scheduling token refresh for key {key} in {wait_seconds} seconds")

        if wait_seconds > 0:
            await asyncio.sleep(wait_seconds)

        # Check if refresh token is still valid
        if int(time.time()) >= refresh_exp:
            print(f"Refresh token expired for key {key}")
            _store.pop(key, None)
            return

        # Perform token refresh
        success = await _refresh_access_token(key, refresh_token)
        if not success:
            print(f"Failed to refresh token for key {key}")
            _store.pop(key, None)

    except asyncio.CancelledError:
        print(f"Token refresh task cancelled for key {key}")
    except Exception as e:
        print(f"Error in token refresh scheduler for key {key}: {e}")
    finally:
        # Clean up task reference
        if key in _refresh_tasks:
            del _refresh_tasks[key]


async def _refresh_access_token(key: str, refresh_token: str) -> bool:
    """
    Refresh the access token using the refresh token.
    Returns True if successful, False otherwise.
    """
    try:
        auth_domain = os.getenv("AUTH_DOMAIN_NAME")
        token_url = (
            f"https://{auth_domain}/realms/finmars/protocol/openid-connect/token"
        )

        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": "finmars",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                token_url,
                data=urlencode(payload),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            ) as response:
                if response.status != 200:
                    print(f"Token refresh failed with status {response.status}")
                    return False

                token_data = await response.json()

                # Parse new tokens
                new_access_token = token_data.get("access_token")
                new_refresh_token = token_data.get("refresh_token", refresh_token)

                if not new_access_token:
                    print("No access token in refresh response")
                    return False

                # Parse JWT to get expiration times
                access_claims = jwt.decode(
                    new_access_token,
                    options={"verify_signature": False, "verify_aud": False},
                )
                new_access_exp = int(access_claims.get("exp", 0))

                refresh_claims = jwt.decode(
                    new_refresh_token,
                    options={"verify_signature": False, "verify_aud": False},
                )
                new_refresh_exp = int(refresh_claims.get("exp", 0))

                # Get existing bundle data
                existing_item = _store.get(key)
                if not existing_item:
                    return False

                existing_bundle = existing_item[0]

                # Update bundle with new token
                new_bundle = {
                    **existing_bundle,
                    "FINMARS_EXPERT_TOKEN": new_access_token,
                    "exp": new_access_exp,
                }

                # Save updated bundle (this will start a new refresh task)
                save_bundle(
                    key, new_bundle, new_access_exp, new_refresh_token, new_refresh_exp
                )

                print(f"Successfully refreshed token for key: {key}")
                return True

    except Exception as e:
        print(f"Error refreshing token for key {key}: {e}")
        return False


def make_key(email: str, name: str) -> str:
    """Creates a consistent key from user's email and name."""
    # Just it case security_suffix
    security_suffix = os.getenv("BOOTSTRAP_SECURITY_SUFFIX_KEY", "")
    return f"email:{email.lower().strip()}::name:{(name or '').strip().lower()}____{security_suffix}"
