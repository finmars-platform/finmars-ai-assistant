from typing import Sequence

from google.ai.generativelanguage_v1beta.types import Tool as GenAITool
from langchain_core.messages import (
    SystemMessage,
    BaseMessage,
)
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt.chat_agent_executor import AgentState

from agents.env import LLM_MODEL
from agents.multiagent_system_prompt import (
    FINANCIAL_MATHEMATICIAN_SYSTEM_PROMPT,
    FINANCIAL_MATHEMATICIAN_LOG_FILE_SYSTEM_PROMPT,
)


async def create_prompt(
    messages: Sequence[BaseMessage], is_gemini: bool
) -> list[BaseMessage]:
    """Create the prompt template"""
    sys_msg = (
        SystemMessage(FINANCIAL_MATHEMATICIAN_SYSTEM_PROMPT)
        if is_gemini
        else SystemMessage(
            FINANCIAL_MATHEMATICIAN_SYSTEM_PROMPT
            + FINANCIAL_MATHEMATICIAN_LOG_FILE_SYSTEM_PROMPT
        )
    )
    return [
        sys_msg,
        *messages,
    ]


async def financial_mathematician(state: AgentState, config: RunnableConfig):
    messages = state.get("messages", [])

    config_default = {
        "temperature": 0.0,
        "base_url": None,
    }

    is_gemini = LLM_MODEL.startswith("gemini")

    msgs = await create_prompt(messages=messages, is_gemini=is_gemini)

    if is_gemini:
        config_default.update(
            {
                "model": LLM_MODEL,
                "thinking_budget": -1,
                "include_thoughts": True,
            }
        )
        llm = ChatGoogleGenerativeAI(
            **config_default,
            tags=["additional_thinking"],
            # timeout=200.0,
        )
        response = await llm.ainvoke(
            msgs,
            tools=[GenAITool(code_execution={})],
        )
        # ).with_retry(
        #     retry_if_exception_type=(
        #         httpx.ReadTimeout,
        #         httpx.RemoteProtocolError,
        #         ServiceUnavailable,
        #         InternalServerError,
        #     ),  # Retry only on ValueError
        #     wait_exponential_jitter=True,  # Add jitter to the exponential backoff
        #     stop_after_attempt=6,
        # )
    else:
        config_default.update(
            {
                "model_name": LLM_MODEL,
                "temperature": (
                    1.0
                    if config_default.get("temperature", 0.0) < 1.0
                    else config_default.get("temperature", 0.0)
                ),
                "use_responses_api": True,
                "model_kwargs": {
                    "reasoning": {
                        "effort": "low",  # 'low', 'medium', or 'high'
                        "summary": "auto",  # 'detailed', 'auto', or None
                    }
                },
            }
        )
        llm = ChatOpenAI(
            **config_default,
            tags=["additional_thinking"],
            # timeout=200.0,
        )
        llm = llm.bind_tools(
            [
                {
                    "type": "code_interpreter",
                    # Create a new container
                    "container": {"type": "auto"},
                }
            ]
        )
        response = await llm.ainvoke(
            msgs,
        )

    response.name = "financial_mathematician"

    return {
        "messages": [response],
    }


def build_graph_financial_mathematician():
    workflow = StateGraph(AgentState)
    workflow.add_node("financial_mathematician", financial_mathematician)

    # Add edges
    workflow.add_edge(START, "financial_mathematician")
    workflow.add_edge("financial_mathematician", END)

    # Compile the graph
    app = workflow.compile(name="financial_mathematician")

    return app


financial_mathematician_app = build_graph_financial_mathematician()
