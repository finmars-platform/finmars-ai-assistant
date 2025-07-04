#!/usr/bin/env python3
"""
Simple script to interact with the agent via LangChain ChatOpenAI interface.
"""

import time
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


def main():
    # Initialize the ChatOpenAI client with custom base URL
    chat = ChatOpenAI(
        base_url="http://localhost:9199/v1",
        api_key="test",
        model="finmars-ai-assistant",
        temperature=0.0,
        streaming=True  # Enable streaming for real-time responses
    )

    print("Agent Chat Interface")
    print("=" * 50)
    print("Type 'exit' to quit the conversation")
    print("=" * 50)

    # Conversation history
    messages = []

    # Optional system message
    system_prompt = "You are a helpful AI assistant."
    messages.append(SystemMessage(content=system_prompt))

    while True:
        # Get user input
        user_input = input("\nYou: ").strip()

        if user_input.lower() == 'exit':
            print("Goodbye!")
            break

        if not user_input:
            continue

        # Add user message to history
        messages.append(HumanMessage(content=user_input))

        # Retry logic with 3 attempts
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                # Get response from agent
                print("\nAgent: ", end="", flush=True)

                # Stream the response
                full_response = ""
                for chunk in chat.stream(messages):
                    content = chunk.content
                    print(content, end="", flush=True)
                    full_response += content

                print()  # New line after response

                # TODO: FIX in `pipelines` this error
                if full_response.startswith("ERR::"):
                    raise Exception(full_response)

                # Add assistant response to history
                messages.append({"role": "assistant", "content": full_response})
                break  # Success, exit retry loop

            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"\nError occurred: {e}")
                    print(f"Retrying... (Attempt {retry_count + 1}/{max_retries})")
                    time.sleep(1)  # Wait 1 second before retry
                else:
                    print(f"\nError after {max_retries} attempts: {e}")
                    # Remove the last user message if there was an error
                    messages.pop()
                    break


def simple_example():
    """Simple example of making a single request to the agent with retry logic."""
    chat = ChatOpenAI(
        base_url="http://localhost:9199/v1",
        api_key="test",
        model="finmars-ai-assistant",
        temperature=0.0
    )

    # Single request example
    messages = [
        HumanMessage(content="What can you help me with?")
    ]

    # Retry logic with 3 attempts
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = chat.invoke(messages)
            print("Response:", response.content)
            break  # Success, exit retry loop
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Error occurred: {e}")
                print(f"Retrying... (Attempt {attempt + 2}/{max_retries})")
                time.sleep(1)
            else:
                print(f"Error after {max_retries} attempts: {e}")


if __name__ == "__main__":
    # Run the interactive chat
    main()

    # Or uncomment below to run the simple example
    # simple_example()
