import os
from typing import List, Union, Generator, Iterator, Optional
from pprint import pprint
import time

from langchain_core.messages import BaseMessage
from pydantic import BaseModel

from agents.react_agent.runner import arun_agent_stream
from utils.agent_utils.async_loop_to_sync import sync_generator_from_async
from utils.agent_utils.lc_converter import convert_to_lc_messages
from libs.utils.langfuse_manager import PromptSource


# Uncomment to disable SSL verification warnings if needed.
# warnings.filterwarnings('ignore', message='Unverified HTTPS request')


class Pipeline:

    class Valves(BaseModel):
        OLLAMA_MODEL_NAME: str

    def __init__(self):
        self.name = os.getenv("PIPELINE_NAME", "Finmars AI Assistant Local")
        self.name = f"{self.name} Ollama"
        self.description = "This is a finmars ai assistant pipeline"
        self.debug = False
        self.version = "0.0.1"
        self.author = "Dmitrii Koriakov"

        # Configure prompt source from environment variable
        # Options: "code" or "langfuse" (default: "langfuse")
        # prompt_source_env = os.getenv("PROMPT_SOURCE", PromptSource.LANGFUSE.value)
        prompt_source_env = os.getenv("PROMPT_SOURCE", PromptSource.CODE.value)
        self.prompt_source = PromptSource(prompt_source_env)

        self.valves = self.Valves(
            **{
                "OLLAMA_MODEL_NAME": os.getenv("OLLAMA_MODEL_NAME", "qwen3:1.7b"),
            }
        )

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
            arun_agent_stream, messages=messages_lc, prompt_source=self.prompt_source, model_name=self.valves.OLLAMA_MODEL_NAME
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
