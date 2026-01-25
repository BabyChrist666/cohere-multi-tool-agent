"""
Multi-Tool definitions for Cohere Agent
Tools: Web Search, Calculator, Code Executor, Web Scraper, File Reader
"""

import json
import httpx
from typing import Any
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup


# Tool definitions for Cohere API
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information. Use this for questions about recent events, facts, or anything that requires up-to-date information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return (default 5, max 10)"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Perform mathematical calculations. Supports basic arithmetic, exponents, and common math functions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate (e.g., '2 + 2', 'sqrt(16)', '10 ** 2')"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_python",
            "description": "Execute Python code and return the result. Use for data processing, calculations, or generating outputs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute. The last expression or print output will be returned."
                    }
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "scrape_webpage",
            "description": "Fetch and extract text content from a webpage URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the webpage to scrape"
                    },
                    "max_length": {
                        "type": "integer",
                        "description": "Maximum characters to return (default 5000)"
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current date and time in various formats.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "Timezone (e.g., 'UTC', 'US/Eastern', 'Asia/Tokyo'). Default is UTC."
                    }
                },
                "required": []
            }
        }
    }
]


def web_search(query: str, num_results: int = 5) -> dict[str, Any]:
    """Search the web using DuckDuckGo"""
    try:
        num_results = min(num_results, 10)
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=num_results))

        formatted_results = []
        for r in results:
            formatted_results.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", "")
            })

        return {
            "success": True,
            "query": query,
            "num_results": len(formatted_results),
            "results": formatted_results
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def calculator(expression: str) -> dict[str, Any]:
    """Safely evaluate mathematical expressions"""
    import math

    # Allowed functions
    safe_dict = {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sum": sum,
        "pow": pow,
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "pi": math.pi,
        "e": math.e,
    }

    try:
        # Basic safety check
        forbidden = ["import", "exec", "eval", "open", "__", "os", "sys"]
        if any(f in expression.lower() for f in forbidden):
            return {"success": False, "error": "Expression contains forbidden keywords"}

        result = eval(expression, {"__builtins__": {}}, safe_dict)
        return {
            "success": True,
            "expression": expression,
            "result": result
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def execute_python(code: str) -> dict[str, Any]:
    """Execute Python code in a restricted environment"""
    import io
    import sys
    from contextlib import redirect_stdout, redirect_stderr

    # Safety check
    forbidden = ["import os", "import sys", "subprocess", "open(", "__import__",
                 "exec(", "eval(", "compile(", "globals(", "locals("]

    for f in forbidden:
        if f in code:
            return {"success": False, "error": f"Forbidden operation: {f}"}

    # Capture output
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    try:
        # Create restricted globals
        restricted_globals = {
            "__builtins__": {
                "print": print,
                "len": len,
                "range": range,
                "str": str,
                "int": int,
                "float": float,
                "list": list,
                "dict": dict,
                "set": set,
                "tuple": tuple,
                "bool": bool,
                "sum": sum,
                "min": min,
                "max": max,
                "abs": abs,
                "round": round,
                "sorted": sorted,
                "enumerate": enumerate,
                "zip": zip,
                "map": map,
                "filter": filter,
            }
        }

        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            exec(code, restricted_globals)

        output = stdout_capture.getvalue()
        errors = stderr_capture.getvalue()

        return {
            "success": True,
            "output": output if output else "Code executed successfully (no output)",
            "errors": errors if errors else None
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def scrape_webpage(url: str, max_length: int = 5000) -> dict[str, Any]:
    """Fetch and extract text from a webpage"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        with httpx.Client(follow_redirects=True, timeout=10) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script and style elements
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()

        # Get text
        text = soup.get_text(separator="\n", strip=True)

        # Clean up whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        text = "\n".join(lines)

        # Truncate if needed
        if len(text) > max_length:
            text = text[:max_length] + "...[truncated]"

        return {
            "success": True,
            "url": url,
            "title": soup.title.string if soup.title else "No title",
            "content": text
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_current_time(timezone: str = "UTC") -> dict[str, Any]:
    """Get current date and time"""
    from datetime import datetime
    try:
        # Simple UTC implementation
        now = datetime.utcnow()
        return {
            "success": True,
            "timezone": timezone,
            "datetime": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "day_of_week": now.strftime("%A")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# Tool executor mapping
TOOL_EXECUTORS = {
    "web_search": web_search,
    "calculator": calculator,
    "execute_python": execute_python,
    "scrape_webpage": scrape_webpage,
    "get_current_time": get_current_time,
}


def execute_tool(tool_name: str, parameters: dict) -> dict[str, Any]:
    """Execute a tool by name with given parameters"""
    if tool_name not in TOOL_EXECUTORS:
        return {"success": False, "error": f"Unknown tool: {tool_name}"}

    try:
        return TOOL_EXECUTORS[tool_name](**parameters)
    except Exception as e:
        return {"success": False, "error": str(e)}
