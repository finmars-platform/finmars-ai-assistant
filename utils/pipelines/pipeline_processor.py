import os
import time
from typing import Optional, Dict, Tuple

from utils.pipelines.env_manager import get_bool_env
from utils.pipelines.state import get_bundle, make_key


def process_pipeline_auth(
    body: dict,
) -> Tuple[Optional[str], Optional[str], Optional[str], str, str]:
    """
    Process authentication and authorization for pipeline requests.

    Args:
        body: Request body containing user information

    Returns:
        Tuple of (token, realm, space, key, error_message)
        If error_message is not empty, the other values should be ignored.
    """
    dynamic_token = get_bool_env(
        name="ACTIVATE_DYNAMIC_FINMARS_EXPERT_TOKEN_HANDLING", default=False
    )

    user = (body or {}).get("user") or {}
    user_email = (user.get("email") or "").strip()
    user_name = (user.get("name") or "").strip()

    token = None
    realm = None
    space = None
    key = ""

    print(f"dynamic_token: {dynamic_token}")

    if dynamic_token:
        # Require user context and valid session bundle
        if not user_email:
            return (
                None,
                None,
                None,
                "",
                "User email is not defined. Please log in again via SSO.",
            )

        key = make_key(user_email, user_name)
        bundle = get_bundle(key)
        if not bundle:
            return (
                None,
                None,
                None,
                "",
                "FinAI authorization is required: please press the FinAI button again.",
            )

        if int(time.time()) >= int(bundle.get("exp", 0)):
            return (
                None,
                None,
                None,
                "",
                "FinAI session has expired. Please refresh the page and click FinAI.",
            )

        token = bundle.get("FINMARS_EXPERT_TOKEN")
        token = f"Token {token}"
        realm = bundle.get("FINMARS_REALM")
        space = bundle.get("FINMARS_SPACE")
    else:
        # Use static env configuration
        token = (os.getenv("FINMARS_EXPERT_TOKEN") or "").strip()
        token = f"Bearer {token}"
        realm = (os.getenv("FINMARS_REALM") or "").strip()
        space = (os.getenv("FINMARS_SPACE") or "").strip()
        if not token or not realm or not space:
            return (
                None,
                None,
                None,
                "",
                "Missing FINMARS credentials. Please set FINMARS_EXPERT_TOKEN, FINMARS_REALM, and FINMARS_SPACE env vars.",
            )
        # build a fallback key for tracing
        key = make_key(user_email or "static_env", user_name or "static_env")

    return token, realm, space, key, ""


def log_user_info(body: dict) -> None:
    """
    Log user information for debugging purposes.

    Args:
        body: Request body containing user information
    """
    user = (body or {}).get("user") or {}
    user_id: str | None = user.get("id")
    user_role: str | None = user.get("role")
    user_name: str | None = user.get("name", "").strip()
    user_email: str | None = user.get("email", "").strip()

    print(
        f"user_id: {repr(user_id)}; user_role: {repr(user_role)}; user_name: {repr(user_name)}; user_email: {repr(user_email)}"
    )
