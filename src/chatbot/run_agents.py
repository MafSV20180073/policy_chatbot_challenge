import os

from dotenv import load_dotenv
from src.chatbot.chats.cli_chat import OrderManagementChat
from src.chatbot.tools.promtps import SYSTEM_PROMPT, SYSTEM_PROMPT_2, SYSTEM_PROMPT_3

load_dotenv()

MODEL = os.getenv("MODEL", "mistralai/mistral-7b-instruct:free")

# Alternative models:
# - "openai/gpt-4.1-nano"
# - "mistralai/mistral-small-3.1-24b-instruct:free"
# - "google/gemini-2.0-flash-001"


# Example usage:
if __name__ == "__main__":
    # task = "I want to cancel order 111975 please."
    task = "What is the status of my order? The tracking number is 285374!"

    chat = OrderManagementChat(
        model=MODEL,
        system_prompt=SYSTEM_PROMPT,
    )

    chat.run_interactive()
