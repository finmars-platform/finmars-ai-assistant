import os
from typing import List, Union, Generator, Iterator, Optional
from pprint import pprint
import time

from langchain_core.messages import BaseMessage

from agents.react_agent.runner import arun_agent_stream
from utils.agent_utils.async_loop_to_sync import sync_generator_from_async
from utils.agent_utils.lc_converter import convert_to_lc_messages
from libs.utils.langfuse_manager import PromptSource
from utils.pipelines.env_manager import get_bool_env
from utils.pipelines.state import get_bundle, make_key


# Uncomment to disable SSL verification warnings if needed.
# warnings.filterwarnings('ignore', message='Unverified HTTPS request')


class Pipeline:
    def __init__(self):
        self.name = os.getenv("PIPELINE_NAME", "Finmars AI Assistant Local")
        self.description = "This is a finmars ai assistant pipeline"
        self.debug = False
        self.version = "0.0.1"
        self.author = "Dmitrii Koriakov"

        # Configure prompt source from environment variable
        # Options: "code" or "langfuse" (default: "langfuse")
        # prompt_source_env = os.getenv("PROMPT_SOURCE", PromptSource.LANGFUSE.value)
        prompt_source_env = os.getenv("PROMPT_SOURCE", PromptSource.CODE.value)
        self.prompt_source = PromptSource(prompt_source_env)

    async def on_startup(self):
        # This function is called when the server is started.
        print(f"on_startup: {__name__}")
        pass

    async def on_shutdown(self):
        # This function is called when the server is shutdown.
        print(f"on_shutdown: {__name__}")
        pass

    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        # This function is called before the OpenAI API request is made. You can modify the form data before it is sent to the OpenAI API.
        print(f"inlet: {__name__}")
        if self.debug:
            print(f"inlet: {__name__} - body:")
            pprint(body)
            print(f"inlet: {__name__} - user:")
            pprint(user)

        body["chat_id"] = body["metadata"]["chat_id"]

        return body

    async def outlet(self, body: dict, user: Optional[dict] = None) -> dict:
        # This function is called after the OpenAI API response is completed. You can modify the messages after they are received from the OpenAI API.
        print(f"outlet: {__name__}")
        if self.debug:
            print(f"outlet: {__name__} - body:")
            pprint(body)
            print(f"outlet: {__name__} - user:")
            pprint(user)
        return body

    def pipe(
        self,
        user_message: str,
        model_id: str,
        messages: List[dict],
        body: dict,
    ) -> Union[str, Generator, Iterator]:
        print(f"pipe: {__name__}")

        chat_id = body.get("chat_id", "")

        dynamic_token = get_bool_env(
            name="ACTIVATE_DYNAMIC_FINMARS_EXPERT_TOKEN_HANDLING", default=False
        )

        user = (body or {}).get("user") or {}
        user_email = (user.get("email") or "").strip()
        user_name = (user.get("name") or "").strip()

        token = None
        realm = None
        space = None

        print(f"dynamic_token: {dynamic_token}")
        if dynamic_token:
            # Require user context and valid session bundle
            if not user_email:
                return "User email is not defined. Please log in again via SSO."

            key = make_key(user_email, user_name)
            bundle = get_bundle(key)
            if not bundle:
                return "FinAI authorization is required: please press the FinAI button again."

            if int(time.time()) >= int(bundle.get("exp", 0)):
                return "FinAI session has expired. Please refresh the page and click FinAI."

            token = bundle.get("FINMARS_EXPERT_TOKEN")
            token = f"Token {token}"
            realm = bundle.get("FINMARS_REALM")
            space = bundle.get("FINMARS_SPACE")
            key = make_key(user_email, user_name)
        else:
            # Use static env configuration
            token = (os.getenv("FINMARS_EXPERT_TOKEN") or "").strip()
            token = f"Bearer {token}"
            realm = (os.getenv("FINMARS_REALM") or "").strip()
            space = (os.getenv("FINMARS_SPACE") or "").strip()
            if not token or not realm or not space:
                return "Missing FINMARS credentials. Please set FINMARS_EXPERT_TOKEN, FINMARS_REALM, and FINMARS_SPACE env vars."
            # build a fallback key for tracing
            key = make_key(user_email or "static_env", user_name or "static_env")

        print(f"token: {repr(token)}; realm: {repr(realm)}; space: {repr(space)}")

        user_id: str | None = body.get("user", {}).get("id")
        user_role: str | None = body.get("user", {}).get("role")
        print(
            f"user_id: {repr(user_id)}; user_role: {repr(user_role)}; user_name: {repr(user_name)}; user_email: {repr(user_email)}"
        )

        if self.debug:
            print(f"pipe: {__name__} - received message from user: {user_message}")

        yield {
            "event": {
                "type": "status",
                "data": {
                    "description": "Agent starts thinking...",
                    "done": False,
                },
            }
        }

        messages_lc: list[BaseMessage] = convert_to_lc_messages(messages=messages)

        for chunk in sync_generator_from_async(
            arun_agent_stream,
            messages=messages_lc,
            prompt_source=self.prompt_source,
            user_key=key,
            chat_id=chat_id,
            realm=realm,
            space=space,
            finmars_token=token,
        ):
            yield chunk

        yield {
            "event": {
                "type": "status",
                "data": {
                    "description": "Agent Answered!",
                    "done": True,
                },
            }
        }
