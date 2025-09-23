from typing import Optional

from langgraph_supervisor import create_supervisor

from agents.financial_mathematician import financial_mathematician_app
from agents.multiagent_system_prompt import (
    SUPERVISOR_SYSTEM_PROMPT,
    FINMARS_API_SYSTEM_PROMPT,
)
from agents.utils.utils import prebuild_agent, post_hook_agent_processor, init_llm

from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt.chat_agent_executor import AgentState, create_react_agent


class SolverState(AgentState):
    """State for Solver agent"""

    # New Context ...
    pass


def create_finmars_multi_agent(
    config: Optional[RunnableConfig] = None,
):

    task_solver_config, prompt_template, tools = prebuild_agent(
        config=config,
        system_prompt=FINMARS_API_SYSTEM_PROMPT,
        skip_build_calculator_tools=True,
    )
    finmars_api_finance_ai_agent_executor_llm = init_llm(
        task_solver_config,
        {"tags": ["finmars_api_finance_ai_agent", "additional_thinking"]},
    )
    finmars_supervisor_agent_executor_llm = init_llm(
        task_solver_config, {"tags": ["finmars_supervisor_agent"]}
    )

    # Create executor agent with state modifier
    finmars_api_agent = create_react_agent(
        model=finmars_api_finance_ai_agent_executor_llm,
        tools=tools,
        prompt=prompt_template,
        name="finmars_api_finance_ai_agent",
        state_schema=SolverState,
        # pre_model_hook=pre_hook_agent_processor,
        # post_model_hook=post_hook_agent_processor,
    )

    executor_agent = create_supervisor(
        model=finmars_supervisor_agent_executor_llm,
        agents=[finmars_api_agent, financial_mathematician_app],
        prompt=SUPERVISOR_SYSTEM_PROMPT,
        add_handoff_back_messages=True,
        output_mode="full_history",
        supervisor_name="finmars_supervisor_agent",
        state_schema=SolverState,
        # pre_model_hook=pre_hook_agent_processor,
        post_model_hook=post_hook_agent_processor,
    ).compile()
    # executor_agent = executor_agent.with_retry(
    #     retry_if_exception_type=(
    #         httpx.ReadTimeout,
    #         httpx.RemoteProtocolError,
    #         ServiceUnavailable,
    #         InternalServerError,
    #     ),  # Retry only on ValueError
    #     wait_exponential_jitter=True,  # Add jitter to the exponential backoff
    #     stop_after_attempt=6,
    # )

    # executor_agent = async_create_deep_agent(
    #     model=executor_llm,
    #     tools=tools,
    #     subagents=[
    #         CustomSubAgent(
    #             name="financial_mathematician",
    #             description="financial_mathematician - a specialized mathematical computation subagent responsible for performing ALL arithmetic operations and mathematical calculations in the financial domain",
    #             graph=financial_mathematician_app,
    #         )
    #     ],
    #     instructions=prompt_template.messages[0].prompt.template,
    # )
    return executor_agent
