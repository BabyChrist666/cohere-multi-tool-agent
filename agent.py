"""
Cohere Multi-Tool AI Agent
Demonstrates agentic workflows with tool use for Cohere job applications
"""

import os
import json
import cohere
from typing import Optional
from dotenv import load_dotenv
from tools import TOOL_DEFINITIONS, execute_tool

load_dotenv()


class CohereAgent:
    """
    Multi-tool AI Agent powered by Cohere's Command model.

    Features:
    - Web search for real-time information
    - Calculator for math operations
    - Python code execution
    - Web scraping
    - Multi-turn conversation with memory
    - Automatic tool selection and chaining
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "command-r-08-2024"):
        self.api_key = api_key or os.getenv("COHERE_API_KEY")
        if not self.api_key:
            raise ValueError("COHERE_API_KEY is required")

        self.client = cohere.Client(self.api_key)
        self.model = model
        self.conversation_history = []
        self.max_tool_iterations = 5

        self.preamble = """You are a helpful AI assistant with access to multiple tools.

Available tools:
1. web_search - Search the internet for current information
2. calculator - Perform mathematical calculations
3. execute_python - Run Python code for data processing
4. scrape_webpage - Extract content from URLs
5. get_current_time - Get current date/time

Guidelines:
- Use tools when you need external information or computations
- Chain multiple tools together when needed
- Always provide clear, helpful responses
- If a tool fails, explain the issue and try alternatives
- Be concise but thorough"""

    def _process_tool_calls(self, tool_calls: list) -> list[dict]:
        """Execute tool calls and return results"""
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.name
            try:
                parameters = tool_call.parameters if hasattr(tool_call, 'parameters') else {}
            except:
                parameters = {}

            print(f"  [Tool] Executing: {tool_name}({parameters})")

            result = execute_tool(tool_name, parameters)
            results.append({
                "call": tool_call,
                "outputs": [result]
            })

            status = "OK" if result.get("success") else "FAIL"
            print(f"  [{status}] Result received")

        return results

    def chat(self, message: str, stream: bool = False) -> str:
        """
        Send a message and get a response, with automatic tool use.
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "USER",
            "message": message
        })

        print(f"\n[User]: {message}")
        print("[Agent] Thinking...")

        iteration = 0
        tool_results = None

        while iteration < self.max_tool_iterations:
            iteration += 1

            # Make API call with tool use
            if tool_results:
                # When providing tool results, use force_single_step
                response = self.client.chat(
                    model=self.model,
                    message=message,
                    preamble=self.preamble,
                    chat_history=self.conversation_history[:-1],
                    tools=TOOL_DEFINITIONS,
                    tool_results=tool_results,
                    force_single_step=True
                )
            else:
                response = self.client.chat(
                    model=self.model,
                    message=message,
                    preamble=self.preamble,
                    chat_history=self.conversation_history[:-1],
                    tools=TOOL_DEFINITIONS
                )

            # Check if we need to execute tools
            if response.tool_calls:
                print(f"\n[Iteration {iteration}]: Tool calls detected")

                # Execute tools
                tool_results = []
                for tc in response.tool_calls:
                    tool_name = tc.name
                    params = tc.parameters if hasattr(tc, 'parameters') else {}

                    print(f"  [Tool] {tool_name}({params})")
                    result = execute_tool(tool_name, params)

                    tool_results.append({
                        "call": tc,
                        "outputs": [result]
                    })

                    status = "OK" if result.get("success") else "FAIL"
                    print(f"  [{status}]")

            else:
                # No more tool calls, we have the final response
                final_response = response.text

                # Add to history
                self.conversation_history.append({
                    "role": "CHATBOT",
                    "message": final_response
                })

                print(f"\n[Agent]: {final_response}")
                return final_response

        # Max iterations reached
        return "I've reached the maximum number of tool iterations. Please try rephrasing your request."

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("[System] Conversation history cleared")

    def get_history(self) -> list[dict]:
        """Get conversation history"""
        return self.conversation_history


def main():
    """Interactive CLI for the agent"""
    print("=" * 60)
    print("Cohere Multi-Tool AI Agent")
    print("=" * 60)
    print("\nCommands:")
    print("  /clear - Clear conversation history")
    print("  /history - Show conversation history")
    print("  /quit - Exit the agent")
    print("-" * 60)

    try:
        agent = CohereAgent()
        print("[System] Agent initialized successfully!")
    except ValueError as e:
        print(f"\n[Error]: {e}")
        print("Please set COHERE_API_KEY in your .env file")
        return

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            if user_input.lower() == "/quit":
                print("Goodbye!")
                break

            if user_input.lower() == "/clear":
                agent.clear_history()
                continue

            if user_input.lower() == "/history":
                history = agent.get_history()
                print(f"\n[History] ({len(history)} messages):")
                for msg in history:
                    role = msg.get("role", "unknown")
                    content = msg.get("message", "")
                    print(f"  [{role}]: {str(content)[:100]}...")
                continue

            agent.chat(user_input)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\n[Error]: {e}")


if __name__ == "__main__":
    main()
