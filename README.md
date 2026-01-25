# 🤖 Cohere Multi-Tool AI Agent

A powerful AI agent built with Cohere's Command R+ model, featuring multiple tools for real-world tasks.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Cohere](https://img.shields.io/badge/Cohere-Command%20R+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-red)

## ✨ Features

- **🔍 Web Search** - Search the internet for real-time information using DuckDuckGo
- **🧮 Calculator** - Perform mathematical calculations safely
- **🐍 Python Executor** - Run Python code in a sandboxed environment
- **🌐 Web Scraper** - Extract content from any webpage
- **⏰ Time/Date** - Get current time in any timezone
- **🔄 Multi-turn Conversations** - Maintains context across messages
- **🔗 Tool Chaining** - Automatically combines tools for complex tasks

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Cohere API key ([Get one free](https://dashboard.cohere.com/api-keys))

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/cohere-agent.git
cd cohere-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your COHERE_API_KEY
```

### Run CLI Agent

```bash
python agent.py
```

### Run Web Server

```bash
python server.py
# Open http://localhost:8000
```

## 📖 Usage Examples

### CLI Mode

```
📝 You: What's the latest news about quantum computing?
🤖 Agent thinking...
  🔧 Executing: web_search({"query": "quantum computing news 2024"})
  ✓ Result received
🤖 Agent: Based on my search, here are the latest developments...

📝 You: Calculate compound interest on $10000 at 7% for 5 years
🤖 Agent thinking...
  🔧 Executing: calculator({"expression": "10000 * (1 + 0.07) ** 5"})
  ✓ Result received
🤖 Agent: The compound interest calculation shows $14,025.52...

📝 You: Write Python code to find prime numbers up to 100
🤖 Agent thinking...
  🔧 Executing: execute_python({"code": "..."})
  ✓ Result received
🤖 Agent: Here are the prime numbers up to 100: [2, 3, 5, 7, 11, ...]
```

### API Mode

```bash
# Chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Search for Cohere AI news", "session_id": "user123"}'

# List tools
curl http://localhost:8000/tools

# Health check
curl http://localhost:8000/health
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│              (CLI / Web UI / API Client)                 │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                   FastAPI Server                         │
│                   (server.py)                            │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                  CohereAgent                             │
│                   (agent.py)                             │
│  ┌─────────────────────────────────────────────────┐    │
│  │  • Conversation Management                       │    │
│  │  • Tool Selection & Orchestration               │    │
│  │  • Response Generation                          │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              Cohere API (Command R+)                     │
│                  Tool Use & Chat                         │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                    Tools                                 │
│                  (tools.py)                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │Web Search│ │Calculator│ │  Python  │ │ Scraper  │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 🛠️ Adding Custom Tools

1. Define the tool in `tools.py`:

```python
# Add to TOOL_DEFINITIONS
{
    "type": "function",
    "function": {
        "name": "my_tool",
        "description": "What my tool does",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "..."}
            },
            "required": ["param1"]
        }
    }
}

# Implement the function
def my_tool(param1: str) -> dict:
    # Your logic here
    return {"success": True, "result": "..."}

# Add to TOOL_EXECUTORS
TOOL_EXECUTORS["my_tool"] = my_tool
```

## 🚢 Deployment

### Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

### Deploy to Render

1. Connect your GitHub repo
2. Set environment variable: `COHERE_API_KEY`
3. Build command: `pip install -r requirements.txt`
4. Start command: `python server.py`

### Deploy with Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "server.py"]
```

## 📝 API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🎯 Why This Project?

This project demonstrates:
- **Agentic AI workflows** with multi-step tool use
- **Production-ready architecture** with FastAPI
- **Safe code execution** with sandboxing
- **Conversational memory** for context retention
- **Extensible tool system** for custom capabilities

Perfect for roles like:
- Applied AI Engineer – Agentic Workflows
- Member of Technical Staff, Agent Code
- Forward Deployed Engineer

## 📄 License

MIT License - feel free to use this for your own projects!

## 🙏 Acknowledgments

- [Cohere](https://cohere.com) for the amazing Command R+ model
- [FastAPI](https://fastapi.tiangolo.com) for the web framework
- [DuckDuckGo](https://duckduckgo.com) for search API

---

Built with ❤️ for the Cohere team
