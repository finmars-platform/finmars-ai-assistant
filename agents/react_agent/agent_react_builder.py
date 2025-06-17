from typing import Optional

from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState

from libs.utils.key_manager import get_api_key
from libs.utils.langfuse_manager import LangfusePromptName
from tools import build_all_tools


def create_agent_prompt(sys_msg) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            sys_msg,
            MessagesPlaceholder("messages", optional=True),
        ]
    )


class SolverState(AgentState):
    """State for Solver agent"""

    # New Context ...
    pass


def create_finmars_agent_react(
    config: Optional[RunnableConfig] = None,
):
    # Get configurable prompt configs
    configurable = config.get("configurable", {}) if config else {}

    # Get task solver prompt and config
    task_solver_sys_msg, task_solver_config = configurable.get(
        LangfusePromptName.SIMPLE_REACT_SYSTEM_PROMPT,
    )

    task_solver_llm_config = {
        "api_key": get_api_key(base_url=task_solver_config.get("base_url")),
        "model_name": task_solver_config.get("model_name"),
        "temperature": task_solver_config.get("temperature"),
        "base_url": task_solver_config.get("base_url"),
    }
    executor_llm = ChatOpenAI(**task_solver_llm_config)

    # Build the prompt template using ChatPromptTemplate.from_messages
    prompt_template = create_agent_prompt(sys_msg=task_solver_sys_msg)

    tools: list[BaseTool] = build_all_tools()

    # Create executor agent with state modifier
    executor_agent = create_react_agent(
        model=executor_llm,
        tools=tools,
        prompt=prompt_template,
        name="FinmarsReactAgent",
        state_schema=SolverState,
    )
    return executor_agent
