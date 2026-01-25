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

    def __init__(self, api_key: Optional[str] = None, model: str = "command-r-plus"):
        self.api_key = api_key or os.getenv("COHERE_API_KEY")
        if not self.api_key:
            raise ValueError("COHERE_API_KEY is required")

        self.client = cohere.Client(self.api_key)
        self.model = model
        self.conversation_history = []
        self.max_tool_iterations = 5

        self.system_prompt = """You are a helpful AI assistant with access to multiple tools.

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
            tool_name = tool_call.function.name
            try:
                parameters = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                parameters = {}

            print(f"  🔧 Executing: {tool_name}({parameters})")

            result = execute_tool(tool_name, parameters)
            results.append({
                "call": tool_call,
                "outputs": [result]
            })

            status = "✓" if result.get("success") else "✗"
            print(f"  {status} Result received")

        return results

    def chat(self, message: str, stream: bool = False) -> str:
        """
        Send a message and get a response, with automatic tool use.

        Args:
            message: User's input message
            stream: Whether to stream the response (not implemented yet)

        Returns:
            Agent's response string
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })

        print(f"\n💬 User: {message}")
        print("🤖 Agent thinking...")

        iteration = 0
        tool_results = None

        while iteration < self.max_tool_iterations:
            iteration += 1

            # Build messages for API call
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(self.conversation_history)

            # Make API call
            response = self.client.chat(
                model=self.model,
                messages=messages,
                tools=TOOL_DEFINITIONS,
                tool_results=tool_results
            )

            # Check if we need to execute tools
            if response.message.tool_calls:
                print(f"\n📍 Iteration {iteration}: Tool calls detected")
                tool_results = self._process_tool_calls(response.message.tool_calls)

                # Add assistant's tool call to history
                self.conversation_history.append({
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in response.message.tool_calls
                    ]
                })

                # Add tool results to history
                for tr in tool_results:
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tr["call"].id,
                        "content": json.dumps(tr["outputs"])
                    })
            else:
                # No more tool calls, we have the final response
                final_response = response.message.content[0].text

                # Add to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_response
                })

                print(f"\n🤖 Agent: {final_response}")
                return final_response

        # Max iterations reached
        return "I've reached the maximum number of tool iterations. Please try rephrasing your request."

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("🗑️ Conversation history cleared")

    def get_history(self) -> list[dict]:
        """Get conversation history"""
        return self.conversation_history


def main():
    """Interactive CLI for the agent"""
    print("=" * 60)
    print("🤖 Cohere Multi-Tool AI Agent")
    print("=" * 60)
    print("\nCommands:")
    print("  /clear - Clear conversation history")
    print("  /history - Show conversation history")
    print("  /quit - Exit the agent")
    print("-" * 60)

    try:
        agent = CohereAgent()
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("Please set COHERE_API_KEY in your .env file")
        return

    while True:
        try:
            user_input = input("\n📝 You: ").strip()

            if not user_input:
                continue

            if user_input.lower() == "/quit":
                print("👋 Goodbye!")
                break

            if user_input.lower() == "/clear":
                agent.clear_history()
                continue

            if user_input.lower() == "/history":
                history = agent.get_history()
                print(f"\n📜 History ({len(history)} messages):")
                for msg in history:
                    role = msg.get("role", "unknown")
                    content = msg.get("content", msg.get("tool_calls", ""))
                    print(f"  [{role}]: {str(content)[:100]}...")
                continue

            agent.chat(user_input)

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
