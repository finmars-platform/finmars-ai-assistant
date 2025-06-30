from langchain_core.messages import HumanMessage, BaseMessage
from langchain_core.runnables import RunnableConfig
from langfuse.langchain import CallbackHandler

from agents.react_agent import simple_react_tag
from agents.react_agent.agent_react_builder import create_finmars_agent_react
from libs.utils.prompt_map_builder import build_map_prompts_cfg


async def arun_agent_stream(messages: list[BaseMessage]):
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
    answer = ""
    async for event_graph in agent.astream_events(
        {
            "messages": messages,
        },
        version="v2",
        config=config,
    ):
        if "skip" in event_graph.get("tags", []):
            continue

        if event_graph.get("event") == "on_chat_model_stream":
            msg_chunk = event_graph.get("data", {}).get("chunk")
            if msg_chunk.type != "AIMessageChunk":
                continue

            if msg_chunk.content:
                answer += msg_chunk.content
                yield msg_chunk.content


async def run_agent(messages: list[BaseMessage]) -> str:
    answer = ""
    async for chunk in arun_agent_stream(messages=messages):
        answer += chunk
    return answer


if __name__ == "__main__":
    import asyncio

    # response = asyncio.run(run_agent(messages=[HumanMessage(content="What is the inception date of the portfolio?")]))
    response = asyncio.run(
        run_agent(
            messages=[
                HumanMessage(content="Show for me portfolio list top 5 on 1 page")
            ]
        )
    )
    print(f"ANSWER: {response}")
