import os
import uuid
from datetime import datetime
from typing import Callable, Dict

from dotenv import load_dotenv
from openai import OpenAI
from src.chatbot.tools.tooling import TOOL_MAPPING


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


def new_react_agent(user_input: str):
    pass


def react_agent(user_input: str, tools: Dict[str, Callable[[str], str]]) -> str:
    session_id = str(uuid.uuid4())
    thoughts = []

    system_prompt = """
    You are a helpful assistant. You have access to the following tools:

    - cancel_order(tracking_number: int): Cancels an order given a tracking number.
    - track_order(tracking_number: int): Retrieves the status of an order using its tracking number.


    Use this format:
    Thought: describe what to do
    Action: tool_name("argument")
    Observation: result of the action
    Answer: final answer to the user
    """

    full_prompt = f"{system_prompt}\nUser: {user_input}\n"

    while True:
        messages = [{"role": "user", "content": full_prompt}]
        response = client.chat.completions.create(
            model="meta-llama/llama-3.3-8b-instruct:free",
            #model="qwen/qwen3-0.6b-04-28:free",
            messages=messages
        )

        content = response.choices[0].message.content.strip()
        print("🧠 LLM:", content)
        full_prompt += f"\n{content}"

        if content.startswith("Answer:"):
            return content.replace("Answer:", "").strip()

        if content.startswith("Action:"):
            try:
                tool_call = content.replace("Action:", "").strip()
                name, arg = tool_call.split("(", 1)
                name = name.strip()
                arg = arg.rstrip(")").strip("\"' ")

                tool_fn = tools.get(name)
                if not tool_fn:
                    full_prompt += f"\nObservation: ERROR: Unknown tool '{name}'"
                    continue

                result = tool_fn(arg)
                full_prompt += f"\nObservation: {result}"
            except Exception as e:
                full_prompt += f"\nObservation: ERROR: {str(e)}"
        else:
            full_prompt += f"\nObservation: INVALID FORMAT"


def react_agent_old(user_input: str, llm_fn: Callable[[str], str]) -> str:
    thoughts = []
    session_id = str(uuid.uuid4())
    prompt = f"""
You are a helpful customer support assistant. Use the following tools to act:
- cancel_order(tracking_number: int): Cancels an order given a tracking number.
- track_order(tracking_number: int): Retrieves the status of an order using its tracking number.

You must reason step-by-step and decide when to use a tool. Follow this format:
Thought: what you should do
Action: the tool you want to use and its input
Observation: the result of the action
... (repeat Thought/Action/Observation as needed, for a maximum of 8 iterations)
Answer: your final response to the user

Begin!
User: {user_input}
"""

    while True:
        full_prompt = prompt + "\n" + "\n".join(thoughts) + "\nThought:"
        output = llm_fn(full_prompt).strip()
        log_run(session_id, "LLM Output", output)
        thoughts.append(f"Thought: {output}")

        if output.startswith("Answer:"):
            final = output.replace("Answer:", "").strip()
            log_run(session_id, "Final Answer", final)
            return final

        if output.startswith("Action:"):
            print("[ACTION!!]")
            try:
                action_line = output.replace("Action:", "").strip()
                func_name, arg_str = action_line.split("(", 1)
                arg = arg_str.rstrip(")").strip("\"'")

                tool_func = TOOL_MAPPING[func_name.strip()]
                if not tool_func:
                    thoughts.append(f"TOOL NOT RECOGNIZED. Tool name: {func_name.strip()}")
                    log_run(session_id, "TOOL NOT RECOGNIZED:", func_name.strip())
                else:
                    observation = tool_func(arg)
                    thoughts.append(f"Observation: {observation}")
                    log_run(session_id, "Observation", observation)
            except Exception as e:
                error_msg = f"ERROR: {str(e)}"
                thoughts.append(f"Observation: {error_msg}")
                log_run(session_id, "Observation", error_msg)
        else:
            thoughts.append("Observation: INVALID FORMAT")
            log_run(session_id, "Observation", "INVALID FORMAT")

