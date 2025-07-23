#!/usr/bin/env python3
"""
Simple script to test a single query with the agent.
"""

import time
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


def test_query(query: str):
    # Initialize the ChatOpenAI client with custom base URL
    chat = ChatOpenAI(
        base_url="http://localhost:9199/v1",
        api_key="test",
        model="finmars-ai-assistant",
        temperature=0.0,
        streaming=True,
    )

    messages = [
        SystemMessage(content="You are a helpful AI assistant."),
        HumanMessage(content=query),
    ]

    # Retry logic with 3 attempts
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            # Get response from agent
            print("Agent: ", end="", flush=True)

            # Stream the response
            full_response = ""
            for chunk in chat.stream(messages):
                content = chunk.content
                print(content, end="", flush=True)
                full_response += content

            print()  # New line after response

            if full_response.startswith("ERR::"):
                raise Exception(full_response)

            return full_response

        except Exception as e:
            retry_count += 1
            if retry_count < max_retries:
                print(f"\nError occurred: {e}")
                print(f"Retrying... (Attempt {retry_count + 1}/{max_retries})")
                time.sleep(1)
            else:
                print(f"\nError after {max_retries} attempts: {e}")
                return None


if __name__ == "__main__":
    import sys

    # Test Query 7.1
    query = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "Show me the P/L report for portfolio CH-EQ-75648329 since 2024-01-01"
    )
    print(f"Testing query: {query}")
    print("=" * 50)
    result = test_query(query)
