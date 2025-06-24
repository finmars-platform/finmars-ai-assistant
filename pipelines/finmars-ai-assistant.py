from typing import List, Union, Generator, Iterator, Optional
from pprint import pprint
import time

from agents.react_agent.runner import arun_agent_stream
from utils.agent_utils.async_loop_to_sync import sync_generator_from_async


# Uncomment to disable SSL verification warnings if needed.
# warnings.filterwarnings('ignore', message='Unverified HTTPS request')


class Pipeline:
    def __init__(self):
        self.name = "Finmars AI Assistant"
        self.description = "This is a finmars ai assistant pipeline"
        self.debug = False
        self.version = "0.0.1"
        self.author = "Dmitrii Koriakov"

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

        for chunk in sync_generator_from_async(
            arun_agent_stream, message_input=user_message
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
