from typing import Sequence

import httpx
from google.ai.generativelanguage_v1beta.types import Tool as GenAITool
from google.api_core.exceptions import ServiceUnavailable
from langchain_core.messages import (
    SystemMessage,
    BaseMessage,
)
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt.chat_agent_executor import AgentState

from agents.react_agent.system_prompt import FINANCIAL_MATHEMATICIAN_SYSTEM_PROMPT


async def create_prompt(
    messages: Sequence[BaseMessage],
) -> list[BaseMessage]:
    """Create the prompt template"""
    return [
        SystemMessage(FINANCIAL_MATHEMATICIAN_SYSTEM_PROMPT),
        *messages,
    ]


async def financial_mathematician(state: AgentState, config: RunnableConfig):
    messages = state.get("messages", [])
    config_default = {
        # "model_name": "gemini-2.5-flash",
        "model": "gemini-2.5-pro",
        "temperature": 0.0,
        "thinking_budget": -1,
        "include_thoughts": True,
    }

    llm = ChatGoogleGenerativeAI(
        **config_default,
        tags=["additional_thinking"],
        timeout=20.0,
    ).with_retry(
        retry_if_exception_type=(
            httpx.ReadTimeout,
            httpx.RemoteProtocolError,
            ServiceUnavailable,
        ),  # Retry only on ValueError
        wait_exponential_jitter=True,  # Add jitter to the exponential backoff
        stop_after_attempt=6,
    )
    msgs = await create_prompt(
        messages=messages,
    )

    response = await llm.ainvoke(
        msgs,
        tools=[GenAITool(code_execution={})],
    )
    response.name = "FinancialMathematician"

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
    app = workflow.compile(name="FinancialMathematician")

    return app


financial_mathematician_app = build_graph_financial_mathematician()
