import os
from typing import Tuple, Optional, Dict, Any, List

from langchain_core.messages import ToolMessage, BaseMessage
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
)
from langfuse import Langfuse
from langfuse.api import ChatMessage, CreatePromptRequest_Chat
from langfuse.api.resources.commons.errors.not_found_error import NotFoundError
from langfuse.model import (
    ChatPromptClient,
)

from agents.react_agent.system_prompt import SIMPLE_REACT_SYSTEM_PROMPT
from libs.basic.base_enum import BaseEnum
from libs.logger.logger import logger


class TypeMessage(str, BaseEnum):
    SYSTEM = "system"
    AI = "ai"
    HUMAN = "human"
    TOOL = "tool"


class PromptSource(str, BaseEnum):
    CODE = "code"
    LANGFUSE = "langfuse"


class LangfusePromptName(str, BaseEnum):
    SIMPLE_REACT_SYSTEM_PROMPT = "simple_react_system_prompt"


MAP_PROMPTS = {
    LangfusePromptName.SIMPLE_REACT_SYSTEM_PROMPT: (
        TypeMessage.SYSTEM.value,
        SIMPLE_REACT_SYSTEM_PROMPT,
    )
}


MAP_LC_BUILDER = {
    TypeMessage.SYSTEM: SystemMessagePromptTemplate.from_template,
    TypeMessage.HUMAN: HumanMessagePromptTemplate.from_template,
    TypeMessage.AI: AIMessagePromptTemplate.from_template,
    TypeMessage.TOOL: ToolMessage,
}


async def from_tuple_to_lc_msg(msg_tuple: Tuple[str, str]) -> BaseMessage:
    value_to_check = msg_tuple[0]
    content = msg_tuple[1]
    if any(item.value == value_to_check for item in TypeMessage):
        type_msg = TypeMessage(value_to_check)
        if type_msg.value == TypeMessage.TOOL:
            return MAP_LC_BUILDER[type_msg](content=content)
        else:
            return MAP_LC_BUILDER[type_msg](content)
    else:
        raise ValueError(
            f"{value_to_check} is not a valid value in {TypeMessage.__name__}"
        )


class LangFusePromptManager:
    langfuse = Langfuse()

    @classmethod
    async def build_msg(
        cls,
        name: LangfusePromptName,
        version: Optional[int] = None,
        label: Optional[str] = "production",
        config: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        return_config: Optional[bool] = None,
        prompt_source: Optional[PromptSource] = None,
    ) -> (
        BaseMessage
        | SystemMessagePromptTemplate
        | Tuple[BaseMessage | SystemMessagePromptTemplate, Dict[str, Any]]
    ):
        # Determine prompt source from parameter or environment variable
        if prompt_source is None:
            prompt_source = PromptSource(
                os.getenv("PROMPT_SOURCE", PromptSource.CODE.value)
            )

        # If prompt source is CODE, load from local code
        if prompt_source == PromptSource.CODE:
            prompt_msg: BaseMessage | Tuple[str, str] = MAP_PROMPTS[name]

            # If the prompt_msg is a tuple, convert it to langchain msg
            if isinstance(prompt_msg, tuple):
                prompt_msg = await from_tuple_to_lc_msg(prompt_msg)

            logger.info(
                f"[LOADED PROMPT FROM CODE FOR {name.value}] CONTENT: {repr(prompt_msg)}"
            )

            if return_config:
                return prompt_msg, config
            return prompt_msg

        # Otherwise, try to load from Langfuse
        prompt_from_langfuse_config = None
        try:
            prompt_from_langfuse: ChatPromptClient = (
                await cls.langfuse.async_api.prompts.get(
                    prompt_name=name.value,
                    version=version,
                    label=label,
                )
            )
            prompt_from_langfuse_config = prompt_from_langfuse.config
            prompt = prompt_from_langfuse.prompt
            logger.warning(
                f"[GOT PROMPT FROM LANGFUSE FOR {name.value}] CONTENT: {repr(prompt)}"
            )
        except NotFoundError as e:
            logger.warning(f"!!Prompt not found will be created from scratch: {e}")
            prompt_msg: BaseMessage | Tuple[str, str] = MAP_PROMPTS[name]

            # Convert your prompt to a list[ChatMessage] as required by CreatePromptRequest_Chat
            if isinstance(prompt_msg, tuple):
                # If it's a tuple (role, content)
                chat_messages = [ChatMessage(role=prompt_msg[0], content=prompt_msg[1])]
            elif isinstance(prompt_msg, list):
                # If it's a list of tuples (role, content)
                chat_messages = [
                    ChatMessage(role=role, content=content)
                    for role, content in prompt_msg
                ]
            else:
                # If it's a langchain message or similar, convert accordingly
                chat_messages = [await cls._from_langchain_to_langfuse(prompt_msg)]

            await cls.langfuse.async_api.prompts.create(
                request=CreatePromptRequest_Chat(
                    name=name.value,
                    prompt=chat_messages,  # list[ChatMessage]
                    labels=["production"],
                    tags=tags,
                    type="chat",
                    config=config,
                    commit_message="[autogenerated] init prompt from codebase",
                ),
            )
            logger.warning(
                f"[CREATED PROMPT IN LANGFUSE FOR {name.value}] CONTENT: {repr(prompt_msg)}"
            )

            # If the original prompt_msg is a tuple, convert it to langchain msg
            if isinstance(prompt_msg, tuple):
                prompt_msg = await from_tuple_to_lc_msg(prompt_msg)
            if return_config:
                return prompt_msg, prompt_from_langfuse_config or config
            return prompt_msg

        # Prompt exists in Langfuse, reconstruct messages
        msgs: List[Tuple[str, str]] = [
            (item.role, item.content) for item in prompt_from_langfuse.prompt
        ]
        msg_lc: BaseMessage = await from_tuple_to_lc_msg(msgs[-1])
        if return_config:
            return msg_lc, prompt_from_langfuse_config or config
        return msg_lc

    @staticmethod
    async def _from_langchain_to_langfuse(
        msg: "BaseMessage" | Tuple[str, str],
    ) -> ChatMessage:
        if isinstance(msg, tuple):
            return ChatMessage(role=msg[0], content=msg[1])
        elif hasattr(msg, "content"):
            return ChatMessage(role=getattr(msg, "type", "system"), content=msg.content)
        elif hasattr(msg, "prompt"):
            msg_type = None
            if isinstance(msg, SystemMessagePromptTemplate):
                msg_type = "system"
            elif isinstance(msg, HumanMessagePromptTemplate):
                msg_type = "human"
            elif isinstance(msg, AIMessagePromptTemplate):
                msg_type = "ai"
            return ChatMessage(role=msg_type, content=msg.prompt.template)
        else:
            raise ValueError(f"Unknown message type: {msg}")
