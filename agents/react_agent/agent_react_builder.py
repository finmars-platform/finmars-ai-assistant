from typing import Optional
from datetime import datetime
import os

from langchain_core.messages import HumanMessage, AIMessage, RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES

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
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState

from libs.utils.key_manager import get_api_key
from libs.utils.langfuse_manager import LangfusePromptName
from tools import build_all_tools


def create_agent_prompt(sys_msg) -> ChatPromptTemplate:
    # Get timezone from environment variable, default to UTC
    tz_name = os.getenv("TZ", "UTC")

    # Get current date, time, and timezone
    try:
        if ZoneInfo:
            tz = ZoneInfo(tz_name)
            current_time = datetime.now(tz)
        else:
            # Fallback for older Python versions
            from datetime import timezone

            current_time = datetime.now(timezone.utc)
            tz_name = "UTC"  # Force UTC for fallback
    except Exception:
        # If timezone is invalid, fall back to UTC
        if ZoneInfo:
            tz = ZoneInfo("UTC")
            current_time = datetime.now(tz)
            tz_name = "UTC"
        else:
            from datetime import timezone

            current_time = datetime.now(timezone.utc)
            tz_name = "UTC"

    # Format the datetime information
    datetime_info = f"\n\n### Current date and time: {current_time.strftime('%Y-%m-%d %H:%M:%S')} {tz_name}"

    # Add datetime info to the system message content
    if hasattr(sys_msg, "content"):
        sys_msg.content = sys_msg.content + datetime_info
    elif hasattr(sys_msg, "prompt") and hasattr(sys_msg.prompt, "template"):
        sys_msg.prompt.template = sys_msg.prompt.template + datetime_info

    return ChatPromptTemplate.from_messages(
        [
            sys_msg,
            MessagesPlaceholder("messages", optional=True),
        ]
    )


async def pre_hook_agent_processor(state, config):
    hm_content = (
        "Here is my KINDLY REMINDER about `calculator_python_numexpr` tool usage. "
        "Again, PLEASE, IN CASE OF ANY MATH OPERATIONS, CALCULATIONS USE `calculator_python_numexpr` tool. "
        "THIS IS MANDATORY FOR ALL CALCULATIONS THAT WAS PRODUCED FROM YOU!!!"
    )
    ai_content = "YES!!! Of course, I will use the `calculator_python_numexpr` tool for any mathematical calculations. Thank you for the reminder."

    # Remove any existing messages that contain the reminder content
    state["messages"] = [
        msg
        for msg in state["messages"]
        if not (
            hasattr(msg, "content")
            and ((hm_content == msg.content) or (ai_content == msg.content))
        )
    ]

    # Insert reminder messages before the last human message
    rem = [HumanMessage(content=hm_content), AIMessage(content=ai_content)]

    # Find the index of the last human message
    last_human_index = -1
    for i in range(len(state["messages"]) - 1, -1, -1):
        if state["messages"][i].type == "human":
            last_human_index = i
            break

    if last_human_index != -1:
        # Insert before the last human message
        state["messages"][last_human_index:last_human_index] = rem
    else:
        # If no human messages exist, just add the reminders at the end
        state["messages"].extend(rem)

    return {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), *state["messages"]]}


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

    finmars_token = task_solver_config.get("finmars_token")
    space = task_solver_config.get("space")
    realm = task_solver_config.get("realm")

    is_google_provider = task_solver_config.get("is_google_provider", False)

    if is_google_provider:
        # Use ChatGoogleGenerativeAI for Google models
        task_solver_llm_config = {
            "model": task_solver_config.get("model_name"),
            "temperature": task_solver_config.get("temperature"),
            "thinking_budget": task_solver_config.get("thinking_budget", -1),
            "include_thoughts": task_solver_config.get("include_thoughts", True),
        }
        executor_llm = ChatGoogleGenerativeAI(**task_solver_llm_config)
    else:
        # Use ChatOpenAI for OpenAI models
        task_solver_llm_config = {
            "api_key": get_api_key(base_url=task_solver_config.get("base_url")),
            "model_name": task_solver_config.get("model_name"),
            "temperature": task_solver_config.get("temperature"),
            "base_url": task_solver_config.get("base_url"),
        }
        executor_llm = ChatOpenAI(**task_solver_llm_config)

    # Build the prompt template using ChatPromptTemplate.from_messages
    prompt_template = create_agent_prompt(sys_msg=task_solver_sys_msg)

    tools: list[BaseTool] = build_all_tools(
        finmars_token=finmars_token, space=space, realm=realm
    )

    # Create executor agent with state modifier
    executor_agent = create_react_agent(
        model=executor_llm,
        tools=tools,
        prompt=prompt_template,
        name="FinmarsReactAgent",
        state_schema=SolverState,
        pre_model_hook=pre_hook_agent_processor,
    )
    return executor_agent
