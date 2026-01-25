"""
FastAPI server for Cohere Multi-Tool Agent
Provides REST API and WebSocket endpoints for the agent
"""

import os
import json
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from agent import CohereAgent

load_dotenv()

# Store active agents per session
agents: dict[str, CohereAgent] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    print("🚀 Starting Cohere Agent Server...")
    yield
    print("👋 Shutting down...")
    agents.clear()


app = FastAPI(
    title="Cohere Multi-Tool Agent API",
    description="AI Agent with web search, code execution, and more",
    version="1.0.0",
    lifespan=lifespan
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    response: str
    session_id: str


class ToolInfo(BaseModel):
    name: str
    description: str


def get_or_create_agent(session_id: str) -> CohereAgent:
    """Get existing agent or create new one for session"""
    if session_id not in agents:
        agents[session_id] = CohereAgent()
    return agents[session_id]


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web UI"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cohere Multi-Tool Agent</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .chat-container { height: calc(100vh - 200px); }
        .message { animation: fadeIn 0.3s ease-in; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .typing::after { content: '...'; animation: dots 1.5s infinite; }
        @keyframes dots { 0%, 20% { content: '.'; } 40% { content: '..'; } 60%, 100% { content: '...'; } }
    </style>
</head>
<body class="bg-gray-900 text-white">
    <div class="container mx-auto max-w-4xl p-4">
        <header class="text-center py-6">
            <h1 class="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                🤖 Cohere Multi-Tool Agent
            </h1>
            <p class="text-gray-400 mt-2">Powered by Command R+ with Web Search, Code Execution & More</p>
        </header>

        <div class="bg-gray-800 rounded-lg shadow-xl">
            <div class="p-4 border-b border-gray-700">
                <div class="flex gap-2 flex-wrap">
                    <span class="px-3 py-1 bg-blue-600 rounded-full text-sm">🔍 Web Search</span>
                    <span class="px-3 py-1 bg-green-600 rounded-full text-sm">🧮 Calculator</span>
                    <span class="px-3 py-1 bg-purple-600 rounded-full text-sm">🐍 Python</span>
                    <span class="px-3 py-1 bg-orange-600 rounded-full text-sm">🌐 Scraper</span>
                </div>
            </div>

            <div id="chat" class="chat-container overflow-y-auto p-4 space-y-4">
                <div class="message text-center text-gray-500">
                    Start a conversation! Try asking me to search the web, do calculations, or run code.
                </div>
            </div>

            <div class="p-4 border-t border-gray-700">
                <form id="chatForm" class="flex gap-2">
                    <input
                        type="text"
                        id="messageInput"
                        placeholder="Ask me anything..."
                        class="flex-1 bg-gray-700 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        autocomplete="off"
                    >
                    <button
                        type="submit"
                        class="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition"
                    >
                        Send
                    </button>
                </form>
            </div>
        </div>

        <footer class="text-center py-4 text-gray-500 text-sm">
            Built for Cohere job application |
            <a href="/docs" class="text-blue-400 hover:underline">API Docs</a>
        </footer>
    </div>

    <script>
        const chat = document.getElementById('chat');
        const form = document.getElementById('chatForm');
        const input = document.getElementById('messageInput');
        const sessionId = 'session_' + Math.random().toString(36).substr(2, 9);

        function addMessage(content, isUser = false, isTyping = false) {
            const div = document.createElement('div');
            div.className = `message flex ${isUser ? 'justify-end' : 'justify-start'}`;

            const bubble = document.createElement('div');
            bubble.className = `max-w-[80%] rounded-lg px-4 py-2 ${
                isUser
                    ? 'bg-blue-600'
                    : 'bg-gray-700'
            }`;

            if (isTyping) {
                bubble.innerHTML = '<span class="typing">Thinking</span>';
                bubble.id = 'typingIndicator';
            } else {
                bubble.innerHTML = content.replace(/\\n/g, '<br>');
            }

            div.appendChild(bubble);
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;

            return div;
        }

        function removeTyping() {
            const typing = document.getElementById('typingIndicator');
            if (typing) typing.parentElement.remove();
        }

        async function sendMessage(message) {
            addMessage(message, true);
            addMessage('', false, true);

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message, session_id: sessionId })
                });

                const data = await response.json();
                removeTyping();

                if (response.ok) {
                    addMessage(data.response);
                } else {
                    addMessage('❌ Error: ' + (data.detail || 'Something went wrong'));
                }
            } catch (error) {
                removeTyping();
                addMessage('❌ Error: ' + error.message);
            }
        }

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const message = input.value.trim();
            if (message) {
                sendMessage(message);
                input.value = '';
            }
        });

        // Example prompts
        const examples = [
            "What's the latest news about AI?",
            "Calculate the compound interest on $1000 at 5% for 10 years",
            "Write Python code to generate the first 20 fibonacci numbers",
            "What time is it right now?"
        ];
    </script>
</body>
</html>
"""


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the agent"""
    try:
        agent = get_or_create_agent(request.session_id)
        response = agent.chat(request.message)
        return ChatResponse(
            response=response,
            session_id=request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clear/{session_id}")
async def clear_history(session_id: str):
    """Clear conversation history for a session"""
    if session_id in agents:
        agents[session_id].clear_history()
        return {"status": "cleared", "session_id": session_id}
    return {"status": "no_session", "session_id": session_id}


@app.get("/tools")
async def list_tools():
    """List available tools"""
    from tools import TOOL_DEFINITIONS
    tools = []
    for tool in TOOL_DEFINITIONS:
        func = tool.get("function", {})
        tools.append({
            "name": func.get("name"),
            "description": func.get("description")
        })
    return {"tools": tools}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_sessions": len(agents)
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
