import os
from typing import List, Union, Generator, Iterator, Optional
from pprint import pprint

from langchain_core.messages import BaseMessage
from agents.deep_agent.runner import arun_agent_stream
from utils.agent_utils.async_loop_to_sync import sync_generator_from_async
from utils.agent_utils.lc_converter import convert_to_lc_messages
from libs.utils.langfuse_manager import PromptSource
from utils.pipelines.pipeline_processor import process_pipeline_auth, log_user_info


# Uncomment to disable SSL verification warnings if needed.
# warnings.filterwarnings('ignore', message='Unverified HTTPS request')


class Pipeline:
    def __init__(self):
        self.name = os.getenv("PIPELINE_NAME", "Finmars AI Assistant Local")
        self.name = f"{self.name} Deep Agent"
        self.description = "This is a finmars ai assistant pipeline with deep agent"
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

        # Process authentication and authorization
        token, realm, space, key, error_message = process_pipeline_auth(body)
        if error_message:
            print(f"ERR: {error_message}")
            yield error_message
            raise ValueError(f"ERR: {error_message}")

        print(f"realm: {repr(realm)}; space: {repr(space)}")

        # Log user information
        log_user_info(body)

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
