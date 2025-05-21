import json
import os
import uuid
from datetime import datetime
from typing import Callable, Dict, List

from dotenv import load_dotenv
from openai import OpenAI
from src.chatbot.tools.promtps import SYSTEM_PROMPT, SYSTEM_PROMPT_2, SYSTEM_PROMPT_3
from src.chatbot.tools.tooling import TOOL_MAPPING, tools


load_dotenv()

OPEN_ROUTER_API_URL = os.getenv("OPEN_ROUTER_API_URL")
OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")

client = OpenAI(
    base_url=OPEN_ROUTER_API_URL,
    api_key=OPEN_ROUTER_API_KEY,
)


# Logging utility:
def log_run(session_id: str, step: str, content: str):
    os.makedirs("react_logs", exist_ok=True)
    with open(f"react_logs/{session_id}.log", "a") as f:
        f.write(f"{datetime.now().isoformat()} | {step}: {content}\n")


def policy_agent(model: str,
    user_query: str,
    conversation_history: List[Dict],
    system_prompt: str = SYSTEM_PROMPT,
    react_agent: bool = False,
):
    openai_client = OpenAI(
        base_url=OPEN_ROUTER_API_URL,
        api_key=OPEN_ROUTER_API_KEY,
    )

    if react_agent:
        pass
    else:
        pass

    messages = [{"role": "system", "content": system_prompt}] + conversation_history + [{"role": "user", "content": user_query}]

    request = {
        "model": model,
        "tools": tools,
        "tool_choice": "auto",  # Ensure the model considers using tools
        "messages": messages,
    }

    print("Sending initial request to openai...")
    try:
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
                "model": model,
                "messages": messages,
                "tools": tools,
                "tool_choice": "auto",
            }

            try:
                print("Sending second request...")
                second_response = openai_client.chat.completions.create(**second_request)
                second_response_message = second_response.choices[0].message.content

                print("Final response:", second_response_message)
                return second_response_message

            except Exception as e:
                error_msg = f"Error: {str(e)}"
                print(error_msg)
                return f"I'm sorry, I encountered an error while processing a follow-up request. {str(e)}"
        else:
            print("No tool calls were made by the model.")
            print("Final response:", response_message.content)
            return response_message.content

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(error_msg)
        return f"I'm sorry, I encountered an error while processing your request. {str(e)}"
