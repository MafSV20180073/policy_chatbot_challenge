from src.chatbot.agents.agents import policy_agent


class OrderManagementChat:
    def __init__(self, model: str, system_prompt: str):
        self.model = model
        self.conversation_history = []
        self.system_prompt = system_prompt

        print(f"Order Management Chat initialized with model: {model}")
        print("Type 'exit' or 'quit' to end the conversation.")
        print()

    def process_message(self, user_input: str):
        if user_input.lower() in ["exit", "quit"]:
            return "Goodbye! Chat session ended."

        # Add user message to history:
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })

        try:
            response = policy_agent(
                model=self.model,
                user_query=user_input,
                conversation_history=self.conversation_history[:-1],  # Exclude the just-added user message
                system_prompt=self.system_prompt
            )

            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })

            return response

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            return f"I'm sorry, I encountered an error while processing your request. {str(e)}"

    def run_interactive(self):
        """Run an interactive chat session"""
        print("Welcome to the Order Management Assistant!")
        print("How can I help you today?")
        print()

        while True:
            user_input = input("You: ")
            response = self.process_message(user_input)
            print(f"Assistant: {response}")
            print()

            if user_input.lower() in ['exit', 'quit']:
                break
