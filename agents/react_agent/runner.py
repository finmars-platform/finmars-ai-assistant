from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langfuse.langchain import CallbackHandler

from agents.react_agent import simple_react_tag
from agents.react_agent.agent_react_builder import create_finmars_agent_react
from libs.utils.prompt_map_builder import build_map_prompts_cfg


async def run_agent(message_input: str) -> str:

    langfuse_handler = CallbackHandler()

    map_prompts_cfg = await build_map_prompts_cfg(tags=simple_react_tag)
    config = RunnableConfig(
        **{
            "callbacks": [langfuse_handler],
            "metadata": {
                "langfuse_user_id": "random-user",
                "langfuse_session_id": "random-session",
                "langfuse_tags": ["random-tag-1", "random-tag-2"],
            },
            "configurable": map_prompts_cfg,
        }
    )

    agent = create_finmars_agent_react(config)

    # Set trace attributes dynamically via metadata
    response = await agent.ainvoke(
        {
            "messages": [
                HumanMessage(content=message_input),
            ]
        },
        config=config,
    )
    answer: str = response["messages"][-1].content
    return answer


if __name__ == "__main__":
    import asyncio

    # response = asyncio.run(run_agent("What is the inception date of the portfolio?"))
    response = asyncio.run(run_agent("Show for me portfolio list top 5 on 1 page"))
    print(f"ANSWER: {response}")
