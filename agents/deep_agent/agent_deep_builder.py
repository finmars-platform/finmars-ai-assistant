from typing import Optional
from datetime import datetime
import os

from agents.utils.build_system_message import build_system_msg

try:
    from zoneinfo import ZoneInfo
except ImportError:
    # Fallback for Python < 3.9
    from datetime import timezone

    ZoneInfo = None

from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from deepagents import async_create_deep_agent
from langgraph.prebuilt.chat_agent_executor import AgentState

from libs.utils.key_manager import get_api_key
from libs.utils.langfuse_manager import LangfusePromptName
from tools import build_all_tools


class SolverState(AgentState):
    """State for Solver agent"""

    # New Context ...
    pass


def create_finmars_deep_agent(
    config: Optional[RunnableConfig] = None,
):
    # Get configurable prompt configs
    configurable = config.get("configurable", {}) if config else {}

    # Get task solver prompt and config
    task_solver_sys_msg, task_solver_config = configurable.get(
        LangfusePromptName.SIMPLE_REACT_SYSTEM_PROMPT,
    )

    finmars_token = task_solver_config.get("finmars_token")
    space = task_solver_config.get("space")
    realm = task_solver_config.get("realm")

    task_solver_llm_config = {
        "api_key": get_api_key(base_url=task_solver_config.get("base_url")),
        "model_name": task_solver_config.get("model_name"),
        "temperature": task_solver_config.get("temperature"),
        "base_url": task_solver_config.get("base_url"),
    }
    executor_llm = ChatOpenAI(**task_solver_llm_config)

    # Build the prompt template using ChatPromptTemplate.from_messages
    prompt_template: str = build_system_msg(
        sys_msg=task_solver_sys_msg, get_string=True
    )

    tools: list[BaseTool] = build_all_tools(
        finmars_token=finmars_token, space=space, realm=realm
    )

    # Create executor agent with state modifier
    executor_agent = async_create_deep_agent(
        model=executor_llm,
        tools=tools,
        instructions=prompt_template,
    )
    return executor_agent
