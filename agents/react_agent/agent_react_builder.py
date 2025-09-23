import json
import os
from datetime import datetime
from typing import Optional

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    RemoveMessage,
    SystemMessage,
    AnyMessage,
)
from langgraph.graph.message import REMOVE_ALL_MESSAGES

from agents.react_agent.system_prompt import (
    SIMPLE_LLM_TOOL_USAGE_DETECTOR_SYSTEM_PROMPT,
)
from agents.react_agent.utils import init_llm

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
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState

from libs.utils.langfuse_manager import LangfusePromptName
from tools import build_all_tools

msg_type = {
    "ai": "AI Finance Agent",
}


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


def format_msg_content(m: AnyMessage):
    content_out = ""
    if m.type == "ai":
        if isinstance(m.content, list):
            content_out += json.dumps(m.content, indent=2, ensure_ascii=False)
        else:
            content_out += str(m.content)

        if m.tool_calls:
            content_out += f"\nTOOL CALLS BY `AI Finance Agent`: {json.dumps(m.tool_calls, indent=2, ensure_ascii=False)}\n"
    else:
        if m.type == "tool":
            content_out += f"\n TOOL RESPONSE OF TOOL CALL WITH ID: {m.id}\n"
        content_out += str(m.content)
    content_out += "\n"
    content_out += "=" * 150
    content_out += "\n"
    return content_out


async def post_hook_agent_processor(state, config):

    # prompt = ChatPromptTemplate.from_messages(
    #     [
    #         SystemMessage(content=SIMPLE_LLM_TOOL_USAGE_DETECTOR_SYSTEM_PROMPT),
    #         HumanMessagePromptTemplate.from_template(
    #             "Here is the dialog between `AI Finance Agent` and Human:\n\n\n{dialog}"
    #         ),
    #         HumanMessagePromptTemplate.from_template(
    #             "Here is the thinking AND list of current tool calling of `AI Finance Agent` that "
    #             "was created by `AI Finance Agent` based on dialog between `AI Finance Agent` and Human:\n\n\n{agent_tool_calls}"
    #         ),
    #     ]
    # )
    # configurable = config.get("configurable", {}) if config else {}
    # task_solver_sys_msg, task_solver_config = configurable.get(
    #     LangfusePromptName.SIMPLE_REACT_SYSTEM_PROMPT,
    # )
    #
    # task_solver_config["is_google_provider"] = False
    # task_solver_config["model_name"] = "gpt-4.1-2025-04-14"  # could be lower model
    # task_solver_config["temperature"] = 0.0
    #
    # llm = init_llm(task_solver_config, kwargs={"tags": ["additional_thinking"]})
    # chain_calculator_usage_detector = prompt | llm
    #
    # dialog = "\n".join(
    #     (
    #         f"<{msg_type.get(m.type, m.type.capitalize())}>\n{format_msg_content(m)}"
    #         for m in state["messages"][:-1]
    #     )
    # )
    #
    # agent_tool_calls = (
    #     f"<{msg_type.get(state['messages'][-1].type, state['messages'][-1].type.capitalize())}>\n"
    #     f"{format_msg_content(state['messages'][-1])}"
    # )
    #
    # result: AIMessage = await chain_calculator_usage_detector.ainvoke(
    #     {"dialog": dialog, "agent_tool_calls": agent_tool_calls}
    # )
    # result_content = result.content

    result_content = """
YOU FORGOT TO USE `calculator_python_numexpr`! USE IT RIGHT NOW FOR YOUR MATH CALCULATIONS!! 
ALL mathematical operations that MUST be performed using the calculator_python_numexpr tool. 
No calculator tool calls have been made yet for these calculations. 
For financial accuracy and auditability, every step involving arithmetic (summing, aggregating, percentage calculation end etc) must use the calculator tool `calculator_python_numexpr`. 
Execute these calculations with `calculator_python_numexpr` immediately!
"""
    msgs2rm = [
        RemoveMessage(id=m.id) for m in state["messages"] if m.content == result_content
    ]
    return {
        "messages": [
            *msgs2rm,
            *state["messages"],
            HumanMessage(
                content=result_content,
                name="StrictSupervisorAuditorCalculatorUsage",
            ),
        ]
    }


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

    # Check if the last message is a tool message
    if len(state["messages"]) > 0 and state["messages"][-1].type == "tool":
        # Find the last AI message with tool_calls that corresponds to the tool message
        ai_with_tool_calls_index = -1
        for i in range(len(state["messages"]) - 1, -1, -1):
            if (
                state["messages"][i].type == "ai"
                and hasattr(state["messages"][i], "tool_calls")
                and state["messages"][i].tool_calls
            ):
                ai_with_tool_calls_index = i
                break

        if ai_with_tool_calls_index != -1:
            # # Check if there's a human message before the AI message with tool_calls
            # if (ai_with_tool_calls_index > 0 and
            #     state["messages"][ai_with_tool_calls_index - 1].type == "human"):
            #     # Insert before the human message
            #     insert_index = ai_with_tool_calls_index - 1
            # else:
            #     # Insert before the AI message with tool_calls
            #     insert_index = ai_with_tool_calls_index
            insert_index = ai_with_tool_calls_index
            state["messages"][insert_index:insert_index] = rem
        else:
            # If no AI message with tool_calls found, just extend at the end
            state["messages"].extend(rem)
    else:
        # Find the last human message
        last_human_index = -1
        for i in range(len(state["messages"]) - 1, -1, -1):
            if state["messages"][i].type == "human":
                last_human_index = i
                break

        if last_human_index != -1:
            # Check if there's an AI message right before the human message
            if (
                last_human_index > 0
                and state["messages"][last_human_index - 1].type == "ai"
            ):
                # Insert before the AI+human pair
                insert_index = last_human_index - 1
            else:
                # Insert before just the human message
                insert_index = last_human_index

            state["messages"][insert_index:insert_index] = rem
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

    executor_llm = init_llm(task_solver_config)

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
        post_model_hook=post_hook_agent_processor,
    )
    return executor_agent
