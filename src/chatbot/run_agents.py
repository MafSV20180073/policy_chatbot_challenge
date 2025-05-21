import json
import os

from agents.agents import react_agent
from dotenv import load_dotenv
from openai import OpenAI
from tools.tooling import TOOL_MAPPING, tools

load_dotenv()

OPEN_ROUTER_API_URL = os.getenv("OPEN_ROUTER_API_URL")
OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")


def openrouter_llm_fn(prompt: str, verbose: bool = True) -> str:
    client = OpenAI(
        base_url=OPEN_ROUTER_API_URL,
        api_key=OPEN_ROUTER_API_KEY,
    )

    print(prompt)

    completion = client.chat.completions.create(
        extra_body={},
        model="meta-llama/llama-3.3-8b-instruct:free",
        messages=[{"role": "user", "content": prompt}],
    )
    if verbose:
        print(completion.choices[0].message.content)

    return completion.choices[0].message.content


# Example usage
if __name__ == "__main__":
    """
    Use this format:
    Thought: describe what to do
    Action: tool_name("argument")
    Observation: result of the action
    Answer: final answer to the user
    """

    # response = react_agent("I want to cancel order 111975", openrouter_llm_fn)
    MODEL = "openai/gpt-4-turbo"  # "meta-llama/llama-3.3-8b-instruct:free"
    SYSTEM_PROMPT = """
    You are a helpful assistant. You have access to tools for managing orders.
    
    When a user asks to cancel or track an order, use the appropriate tool. 
    For cancelling orders, use the cancel_order tool.
    For tracking orders, use the track_order tool.
    
    ALWAYS use the tools when appropriate rather than making up responses.
    
    """

    # full_prompt = f"{system_prompt}\nUser: {user_input}\n"

    openai_client = OpenAI(
        base_url=OPEN_ROUTER_API_URL,
        api_key=OPEN_ROUTER_API_KEY,
    )

    task = "I want to cancel order 111975 please."

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": task,
        }
    ]

    request = {
        "model": MODEL,
        "tools": tools,
        "tool_choice": "auto",  # Ensure the model considers using tools
        "messages": messages,
    }

    print("Sending initial request...")
    response = openai_client.chat.completions.create(**request)

    response_message = response.choices[0].message
    print(f"Initial response received. Content: {response_message.content}")
    print(f"Tool calls: {response_message.tool_calls}")

    messages.append({"role": "assistant", "content": response_message.content})

    if response_message.tool_calls and len(response_message.tool_calls) > 0:
        print(f"Processing {len(response_message.tool_calls)} tool call(s)")

        messages.pop()  # Remove the previously added assistant message
        messages.append({
            "role": "assistant",
            "content": response_message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,  # tc.function_name
                        "arguments": tc.function.arguments,
                    }
                } for tc in response_message.tool_calls]
        })

        # Process each tool call:
        for tool_call in response_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            print(f"Calling {tool_name} with args: {tool_args}")

            # Call the tool function
            tool_function = TOOL_MAPPING[tool_name]
            raw_response = tool_function(**tool_args)

            # Convert tool response to string if it's a requests.Response:
            if hasattr(raw_response, 'json'):
                try:
                    tool_content = json.dumps(raw_response.json())
                except json.JSONDecodeError:
                    tool_content = raw_response.text
            else:
                tool_content = json.dumps(raw_response)

            print(f"Tool response: {tool_content}")

            # Add tool response to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                # "name": tool_name,
                "content": tool_content,
            })

        # Second request to get our final result:
        second_request = {
            "model": MODEL,
            "messages": messages,
            "tools": tools,
        }

        print("Sending follow-up request...")
        second_response = openai_client.chat.completions.create(**second_request)
        second_response_message = second_response.choices[0].message.content

        # response = react_agent("I want to cancel order 111975 please.", TOOL_MAPPING)
        print("Final response:", second_response_message)
    else:
        print("No tool calls were made by the model.")
        print("Final response:", response_message.content)
