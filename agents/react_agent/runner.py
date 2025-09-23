import json
from typing import Optional
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_core.runnables import RunnableConfig

from agents.react_agent import simple_react_tag
from agents.react_agent.agent_react_builder import create_finmars_agent_react
from libs.utils.prompt_map_builder import build_map_prompts_cfg
from libs.utils.langfuse_manager import PromptSource
from libs.utils.langfuse_callback import get_langfuse_callbacks


async def arun_agent_stream(
    messages: list[BaseMessage],
    chat_id: str,
    user_key: str,
    prompt_source: Optional[PromptSource] = None,
    model_name: Optional[str] = None,
    finmars_token: Optional[str] = None,
    realm: Optional[str] = None,
    space: Optional[str] = None,
):
    # Get Langfuse callbacks based on environment variables
    callbacks = get_langfuse_callbacks()

    config_default = {
        "model_name": "gpt-4.1-2025-04-14",
        "temperature": 0.0,
        "base_url": None,
        "is_google_provider": False,
    }

    map_prompts_cfg = await build_map_prompts_cfg(
        config_default=config_default,
        tags=simple_react_tag,
        prompt_source=prompt_source,
        model_name=model_name,
        finmars_token=finmars_token,
        realm=realm,
        space=space,
    )
    config = RunnableConfig(
        **{
            "callbacks": callbacks,
            "metadata": {
                "langfuse_user_id": user_key,
                "langfuse_session_id": chat_id,
                "langfuse_tags": [
                    f"model_name::{model_name}",
                    f"prompt_source::{prompt_source}",
                ],
            },
            "configurable": map_prompts_cfg,
        }
    )

    agent = create_finmars_agent_react(config)

    # Set trace attributes dynamically via metadata
    answer = ""
    prev_event_is_agent_thinking = True
    async for event_graph in agent.astream_events(
        {
            "messages": messages,
        },
        version="v2",
        config=config,
    ):
        if "skip" in event_graph.get("tags", []):
            continue

        if event_graph.get("event") == "on_tool_end":
            tool_output = event_graph.get("data", {}).get("output")
            tool_output_status = ""
            tool_output_name = ""

            if hasattr(tool_output, "status"):
                tool_output_status = tool_output.status

            if hasattr(tool_output, "name"):
                tool_output_name = tool_output.name

            # Create appropriate status description for tool completion
            if tool_output_name and tool_output_name.startswith("transfer_to_"):
                agent_name = tool_output_name.replace("transfer_to_", "")
                status_description = f"✅ Delegation to {agent_name} completed with status: {tool_output_status}..."
            else:
                status_description = f"🔧 Agent got response from {tool_output_name} tool with status: {tool_output_status}..."

            yield {
                "event": {
                    "type": "status",
                    "data": {
                        "description": status_description,
                        "done": False,
                    },
                }
            }
            prev_event_is_agent_thinking = False

        elif event_graph.get("event") == "on_tool_start":
            tool_name: str = event_graph.get("name")
            tool_input_data: dict = event_graph.get("data", {}).get("input", {})

            # Create appropriate status description for supervisor transfers
            if tool_name.startswith("transfer_to_"):
                agent_name = tool_name.replace("transfer_to_", "")
                task_description = tool_input_data.get(
                    "description", "No task description provided"
                )
                status_description = (
                    f"🔄 Supervisor delegating to {agent_name}: {task_description}..."
                )
            else:
                status_description = f"🔧 Agent call {tool_name} tool with input: {json.dumps(tool_input_data)}..."

            yield {
                "event": {
                    "type": "status",
                    "data": {
                        "description": status_description,
                        "done": False,
                    },
                }
            }
            prev_event_is_agent_thinking = False

        elif event_graph.get("event") == "on_chat_model_stream":
            msg_chunk = event_graph.get("data", {}).get("chunk")
            if msg_chunk.type != "AIMessageChunk":
                continue

            if msg_chunk.content:

                if not prev_event_is_agent_thinking:
                    yield {
                        "event": {
                            "type": "status",
                            "data": {
                                "description": "Agent is analysing tool responses...",
                                "done": False,
                            },
                        }
                    }
                    prev_event_is_agent_thinking = True

                answer += msg_chunk.content
                yield msg_chunk.content


async def arun_agent_stream_thinking(
    messages: list[BaseMessage],
    chat_id: str,
    user_key: str,
    prompt_source: Optional[PromptSource] = None,
    model_name: Optional[str] = None,
    finmars_token: Optional[str] = None,
    realm: Optional[str] = None,
    space: Optional[str] = None,
):
    # Get Langfuse callbacks based on environment variables
    callbacks = get_langfuse_callbacks()
    config_default = {
        # "model_name": "gemini-2.5-flash",
        "model_name": "gemini-2.5-pro",
        "temperature": 0.0,
        "base_url": None,
        "is_google_provider": True,
        "thinking_budget": -1,
        "include_thoughts": True,
    }

    map_prompts_cfg = await build_map_prompts_cfg(
        config_default=config_default,
        tags=simple_react_tag,
        prompt_source=prompt_source,
        model_name=model_name,
        finmars_token=finmars_token,
        realm=realm,
        space=space,
    )
    config = RunnableConfig(
        **{
            "callbacks": callbacks,
            "metadata": {
                "langfuse_user_id": user_key,
                "langfuse_session_id": chat_id,
                "langfuse_tags": [
                    f"model_name::{model_name}",
                    f"prompt_source::{prompt_source}",
                ],
            },
            "configurable": map_prompts_cfg,
        }
    )

    agent = create_finmars_agent_react(config)

    # Set trace attributes dynamically via metadata
    answer = ""
    prev_event_is_agent_thinking = True
    is_thinking_active = False

    async for event_graph in agent.astream_events(
        {
            "messages": messages,
        },
        version="v2",
        config=config,
    ):
        if "skip" in event_graph.get("tags", []):
            continue

        if event_graph.get("event") == "on_tool_end":
            tool_output = event_graph.get("data", {}).get("output")
            tool_output_status = ""
            tool_output_name = ""

            if hasattr(tool_output, "status"):
                tool_output_status = tool_output.status

            if hasattr(tool_output, "name"):
                tool_output_name = tool_output.name

            # Always yield status event for UI
            # Create appropriate status description for tool completion
            if tool_output_name and tool_output_name.startswith("transfer_to_"):
                agent_name = tool_output_name.replace("transfer_to_", "")
                status_description = f"✅ Delegation to {agent_name} completed with status: {tool_output_status}..."
            else:
                status_description = f"🔧 Agent got response from {tool_output_name} tool with status: {tool_output_status}..."

            yield {
                "event": {
                    "type": "status",
                    "data": {
                        "description": status_description,
                        "done": False,
                    },
                }
            }

            # Tool responses should always be in thinking blocks
            # If thinking is not active, something went wrong, but let's handle it gracefully
            if is_thinking_active:
                # Create appropriate thinking output for tool completion
                if tool_output_name and tool_output_name.startswith("transfer_to_"):
                    agent_name = tool_output_name.replace("transfer_to_", "")
                    yield f"✅ Delegation to {agent_name} completed (status: {tool_output_status})\n"
                else:
                    yield f"🔧 Tool call completed: {tool_output_name} (status: {tool_output_status})\n"
            prev_event_is_agent_thinking = False

        elif event_graph.get("event") == "on_tool_start":
            tool_name: str = event_graph.get("name")
            tool_input_data: dict = event_graph.get("data", {}).get("input", {})

            # Always yield status event for UI
            # Create appropriate status description for supervisor transfers
            if tool_name.startswith("transfer_to_"):
                agent_name = tool_name.replace("transfer_to_", "")
                task_description = tool_input_data.get(
                    "description", "No task description provided"
                )
                status_description = (
                    f"🔄 Supervisor delegating to {agent_name}: {task_description}..."
                )
            else:
                status_description = f"🔧 Agent call {tool_name} tool with input: {json.dumps(tool_input_data)}..."

            yield {
                "event": {
                    "type": "status",
                    "data": {
                        "description": status_description,
                        "done": False,
                    },
                }
            }

            # Always start thinking block for tool calls if not active
            if not is_thinking_active:
                yield "<think>"
                is_thinking_active = True

            # Always yield tool call notification in thinking block
            if tool_name.startswith("transfer_to_"):
                # Handle supervisor delegation transfers
                agent_name = tool_name.replace("transfer_to_", "")
                task_description = tool_input_data.get(
                    "description", "No task description provided"
                )
                yield f"🔄 Supervisor delegating to {agent_name}: {task_description}\n"
            else:
                yield f"🔧 Tool call: {tool_name} with input: {json.dumps(tool_input_data)}\n"

            prev_event_is_agent_thinking = False

        elif event_graph.get("event") == "on_chat_model_stream":
            msg_chunk = event_graph.get("data", {}).get("chunk")
            if msg_chunk.type != "AIMessageChunk":
                continue

            # Check if this is from chain_calculator_usage_detector with additional_thinking tag
            is_additional_thinking = "additional_thinking" in event_graph.get(
                "tags", []
            )

            # Handle thinking content
            if hasattr(msg_chunk, "content") and isinstance(msg_chunk.content, list):
                for content_item in msg_chunk.content:
                    if (
                        isinstance(content_item, dict)
                        and content_item.get("type") == "thinking"
                    ):
                        thinking_content = content_item.get("thinking", "")
                        if thinking_content:
                            if not is_thinking_active:
                                yield "<think>"
                                is_thinking_active = True
                            yield thinking_content
                        continue

            # Handle regular content
            if msg_chunk.content and isinstance(msg_chunk.content, str):
                # Check if this chunk has tool calls
                has_tool_calls = (
                    hasattr(msg_chunk, "tool_calls") and msg_chunk.tool_calls
                )

                # If this is additional_thinking content, stream it in thinking mode
                if is_additional_thinking:
                    if not is_thinking_active:
                        yield "<think>"
                        is_thinking_active = True
                    yield msg_chunk.content
                    continue

                # If we were in thinking mode and get regular content without tool calls, close thinking
                if is_thinking_active and not has_tool_calls:
                    yield "\n </think> \n\n"
                    is_thinking_active = False

                if not prev_event_is_agent_thinking and not is_thinking_active:
                    yield {
                        "event": {
                            "type": "status",
                            "data": {
                                "description": "Agent is analysing tool responses...",
                                "done": False,
                            },
                        }
                    }
                    prev_event_is_agent_thinking = True

                answer += msg_chunk.content
                yield msg_chunk.content

    # Close thinking if still active at the end
    if is_thinking_active:
        yield "\n </think> \n\n"


async def run_agent(
    messages: list[BaseMessage], prompt_source: Optional[PromptSource] = None
) -> str:
    answer = ""
    async for chunk in arun_agent_stream(
        messages=messages, prompt_source=prompt_source
    ):
        answer += chunk
    return answer


if __name__ == "__main__":
    import asyncio

    # Example 1: Use default prompt source (from environment variable or Langfuse)
    # response = asyncio.run(run_agent(messages=[HumanMessage(content="What is the inception date of the portfolio?")]))

    # Example 2: Explicitly use prompts from code
    # response = asyncio.run(
    #     run_agent(
    #         messages=[HumanMessage(content="Show for me portfolio list top 5 on 1 page")],
    #         prompt_source=PromptSource.CODE
    #     )
    # )

    # Example 3: Explicitly use prompts from Langfuse
    response = asyncio.run(
        run_agent(
            messages=[
                HumanMessage(content="Show for me portfolio list top 5 on 1 page")
            ],
            prompt_source=PromptSource.LANGFUSE,
        )
    )
    print(f"ANSWER: {response}")
