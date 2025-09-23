from typing import Optional

from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt.chat_agent_executor import AgentState, create_react_agent

from agents.utils.utils import prebuild_agent


class SolverState(AgentState):
    """State for Solver agent"""

    # New Context ...
    pass


def create_finmars_agent_react(
    config: Optional[RunnableConfig] = None,
):
    executor_llm, prompt_template, tools = prebuild_agent(
        config=config, skip_build_calculator_tools=False, system_prompt=None
    )
    # Create executor agent with state modifier
    executor_agent = create_react_agent(
        model=executor_llm,
        tools=tools,
        prompt=prompt_template,
        name="finmars_api_finance_ai_agent",
        state_schema=SolverState,
    )
    return executor_agent
