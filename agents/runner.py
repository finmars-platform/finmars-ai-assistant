import json
import time
from typing import Optional
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_core.runnables import RunnableConfig

from agents import simple_react_tag
from agents.agent_multi_agent_builder import create_finmars_multi_agent
from agents.agent_react_builder import create_finmars_agent_react
from agents.env import LLM_MODEL
from libs.utils.prompt_map_builder import build_map_prompts_cfg
from libs.utils.langfuse_manager import PromptSource
from libs.utils.langfuse_callback import get_langfuse_callbacks
from openai import AsyncClient, OpenAI

openai_client_async = AsyncClient()
openai_client_sync = OpenAI()


def should_close_thinking_for_supervisor(event_graph):
    """Check if thinking should be closed based on supervisor final answer condition."""
    is_supervisor = "finmars_supervisor_agent" in event_graph.get("tags", [])
    if is_supervisor:
        if (
            isinstance(event_graph["data"]["chunk"].content, str)
            and event_graph["data"]["chunk"].content
            and not (
                hasattr(event_graph["data"]["chunk"], "tool_calls")
                and event_graph["data"]["chunk"].tool_calls
            )
        ):
            return True
        elif (
            isinstance(event_graph["data"]["chunk"].content, list)
            and isinstance(event_graph["data"]["chunk"].content[-1], str)
            and not (
                hasattr(event_graph["data"]["chunk"], "tool_calls")
                and event_graph["data"]["chunk"].tool_calls
            )
        ):
            return True
    return False


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
        #"model_name": "gpt-4.1-2025-04-14",
        "model_name": "gpt-4.1",
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

            if (
                hasattr(tool_output, "update")
                and isinstance(tool_output.update["messages"], list)
                and hasattr(tool_output.update["messages"][-1], "type")
                and tool_output.update["messages"][-1].type == "tool"
            ):
                tool_output_name = tool_output.update["messages"][-1].name
                tool_output_status = tool_output.update["messages"][-1].status

            elif hasattr(tool_output, "type") and tool_output.type == "tool":
                tool_output_name = tool_output.name
                tool_output_status = tool_output.status

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
        "temperature": 0.0,
        "base_url": None,
    }

    is_gemini = LLM_MODEL.startswith("gemini")

    if is_gemini:
        config_default.update(
            {
                "model": LLM_MODEL,
                "is_google_provider": True,
                "thinking_budget": -1,
                "include_thoughts": True,
            }
        )
    else:
        config_default.update(
            {
                "model_name": LLM_MODEL,
                "temperature": (
                    1.0
                    if config_default.get("temperature", 0.0) < 1.0
                    else config_default.get("temperature", 0.0)
                ),
                "is_google_provider": False,
                "use_responses_api": True,
                "model_kwargs": {
                    "reasoning": {
                        "effort": "low",  # 'low', 'medium', or 'high'
                        "summary": "auto",  # 'detailed', 'auto', or None
                    }
                },
            }
        )

    map_prompts_cfg = await build_map_prompts_cfg(
        config_default=config_default,
        tags=simple_react_tag,
        prompt_source=prompt_source,
        model_name=model_name,
        finmars_token=finmars_token,
        realm=realm,
        space=space,
    )
    map_prompts_cfg["is_gemini"] = is_gemini
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

    agent = create_finmars_multi_agent(config)

    # Set trace attributes dynamically via metadata
    answer = ""
    prev_event_is_agent_thinking = True
    is_thinking_active = False
    prev_answering_supervisor = ""
    prev_index = None  # Track index for GPT-5 format to detect paragraph breaks
    start_run = time.time()

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

            if (
                hasattr(tool_output, "update")
                and isinstance(tool_output.update["messages"], list)
                and hasattr(tool_output.update["messages"][-1], "type")
                and tool_output.update["messages"][-1].type == "tool"
            ):
                tool_output_name = tool_output.update["messages"][-1].name
                tool_output_status = tool_output.update["messages"][-1].status

            elif hasattr(tool_output, "type") and tool_output.type == "tool":
                tool_output_name = tool_output.name
                tool_output_status = tool_output.status

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
                    yield f"\n✅ Delegation to {agent_name} completed (status: {tool_output_status})\n"
                else:
                    yield f"\n🔧 Tool call completed: {tool_output_name} (status: {tool_output_status})\n"
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
                yield f"\n🔄 Supervisor delegating to {agent_name}: {task_description}\n"
            else:
                yield f"\n🔧 Tool call: {tool_name} with input: {json.dumps(tool_input_data)}\n"

            prev_event_is_agent_thinking = False

        elif event_graph.get("event") == "on_chat_model_stream":
            msg_chunk = event_graph.get("data", {}).get("chunk")
            if msg_chunk.type != "AIMessageChunk":
                continue

            # Check if this is from chain_calculator_usage_detector with additional_thinking tag
            is_additional_thinking = "additional_thinking" in event_graph.get(
                "tags", []
            )
            # Check if this chunk has tool calls
            has_tool_calls = hasattr(msg_chunk, "tool_calls") and msg_chunk.tool_calls
            if (not is_thinking_active) and has_tool_calls:
                yield "<think>"
                is_thinking_active = True

            # Handle GPT-5 reasoning content from additional_kwargs
            if hasattr(msg_chunk, "additional_kwargs") and msg_chunk.additional_kwargs:
                reasoning_data = msg_chunk.additional_kwargs.get("reasoning", {})
                if reasoning_data and "summary" in reasoning_data:
                    if not is_thinking_active:
                        yield "<think>"
                        is_thinking_active = True

                    for summary_item in reasoning_data["summary"]:
                        if isinstance(summary_item, dict):
                            summary_type = summary_item.get("type")
                            current_index = summary_item.get("index", 0)

                            # Yield \n\n when index changes (paragraph break)
                            if prev_index is not None and current_index != prev_index:
                                yield "\n\n"

                            prev_index = current_index

                            if summary_type == "summary_text":
                                text = summary_item.get("text", "")
                                if text:
                                    yield text

                # Handle GPT-5 code_interpreter tool outputs from additional_kwargs
                tool_outputs = msg_chunk.additional_kwargs.get("tool_outputs", [])
                if tool_outputs:
                    if not is_thinking_active:
                        yield "<think>"
                        is_thinking_active = True

                    for tool_output in tool_outputs:
                        if isinstance(tool_output, dict):
                            tool_type = tool_output.get("type")
                            if tool_type == "code_interpreter_call":
                                status = tool_output.get("status", "unknown")
                                code = tool_output.get("code", "")

                                if code:
                                    yield f"\n**Code interpreter executing (status: {status}):**\n```python\n{code}\n```\n"

                                container_id = tool_output.get("container_id", "")
                                if container_id:
                                    files = openai_client_sync.containers.files.list(
                                        container_id=container_id,
                                    )
                                    is_files_showed = False
                                    for file in files:
                                        if file.created_at > start_run:
                                            file_content = await openai_client_async.containers.files.content.retrieve(
                                                container_id=container_id,
                                                file_id=file.id,
                                            )
                                            yield f"\n**Code interpreter file ({file.id}) output:**\n{file_content}\n"
                                            is_files_showed = True

                                    if is_files_showed:
                                        start_run = time.time()

            # Handle thinking content and code execution content
            if hasattr(msg_chunk, "content") and isinstance(msg_chunk.content, list):
                for content_item in msg_chunk.content:
                    if isinstance(content_item, dict):
                        content_type = content_item.get("type")

                        # Handle GPT-5 text content with index tracking
                        if content_type == "text":
                            text_content = content_item.get("text", "")
                            current_index = content_item.get("index", 0)

                            # Yield \n\n when index changes (paragraph break)
                            if prev_index is not None and current_index != prev_index:
                                yield "\n\n"

                            prev_index = current_index

                            if text_content:
                                yield text_content
                            continue

                        # Handle Gemini thinking content (backward compatibility)
                        elif content_type == "thinking":
                            thinking_content = content_item.get("thinking", "")
                            if thinking_content:
                                if not is_thinking_active:
                                    yield "<think>"
                                    is_thinking_active = True
                                yield thinking_content
                            continue

                        # Handle Gemini code execution content (backward compatibility)
                        elif content_type in [
                            "executable_code",
                            "code_execution_result",
                        ]:
                            if not is_thinking_active:
                                yield "<think>"
                                is_thinking_active = True

                            if content_type == "executable_code":
                                code = content_item.get("executable_code", "")
                                if code:
                                    yield f"\n**Prepared code to execute:**\n```python\n{code}\n```\n"
                            elif content_type == "code_execution_result":
                                result = content_item.get("code_execution_result", "")
                                if result:
                                    yield f"\n**Code execution Output:**\n```\n{result}\n```\n"
                            continue

            # Handle regular content
            if msg_chunk.content and isinstance(msg_chunk.content, str):
                # If this is additional_thinking content, stream it in thinking mode
                if is_additional_thinking:
                    if not is_thinking_active:
                        yield "<think>"
                        is_thinking_active = True
                    yield msg_chunk.content
                    continue

                # Check if we should close thinking for supervisor final answer
                should_close_thinking = should_close_thinking_for_supervisor(
                    event_graph
                )

                prev_answering_supervisor += msg_chunk.content

                # Close thinking ONLY for supervisor final answer condition
                if (
                    is_thinking_active
                    and should_close_thinking
                    and not (
                        prev_answering_supervisor.startswith(
                            "delegating_to_financial_mathematician"
                        )
                        or prev_answering_supervisor.startswith(
                            "delegating_to_finmars_api_finance_ai_agent"
                        )
                    )
                ):
                    yield "\n</think>\n\n"
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

            is_supervisor = bool(
                "finmars_supervisor_agent" in event_graph.get("tags", [])
            )
            if not is_supervisor:
                prev_answering_supervisor = ""

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
