"""
MCP Server exposing 4 generation tools: architecture, DFD, presales PPT, and draw.io.
Run with: python mcp_server.py
Listens on the configured MCP server port via SSE transport.
"""

import asyncio
import json
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.middleware.cors import CORSMiddleware
import uvicorn

from config import settings
from tools.architecture_tool import generate_architecture_diagram
from tools.dfd_tool import generate_dfd
from tools.ppt_tool import generate_presales_ppt
from tools.drawio_tool import generate_drawio_architecture

server = Server("optistudio-mcp-server")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="generate_architecture_diagram",
            description="Generate architecture diagrams (precise technical + DALL-E artistic) from project context.",
            inputSchema={
                "type": "object",
                "properties": {
                    "context": {"type": "string", "description": "Extracted text from all uploaded project artifacts."},
                    "instructions": {"type": "string", "description": "User's specific instructions for the architecture diagram."},
                    "answers": {"type": "string", "description": "Answers to clarification questions, if any."},
                },
                "required": ["context", "instructions"],
            },
        ),
        Tool(
            name="generate_dfd",
            description="Generate Data Flow Diagrams (Level 0 + Level 1) using Mermaid and DALL-E from project context.",
            inputSchema={
                "type": "object",
                "properties": {
                    "context": {"type": "string", "description": "Extracted text from all uploaded project artifacts."},
                    "instructions": {"type": "string", "description": "User's specific instructions for the DFD."},
                    "answers": {"type": "string", "description": "Answers to clarification questions, if any."},
                },
                "required": ["context", "instructions"],
            },
        ),
        Tool(
            name="generate_presales_ppt",
            description="Generate a 10-slide presales proposal PPT with Optimus Info branding.",
            inputSchema={
                "type": "object",
                "properties": {
                    "context": {"type": "string", "description": "Extracted text from all uploaded project artifacts."},
                    "instructions": {"type": "string", "description": "User's specific instructions for the PPT."},
                    "answers": {"type": "string", "description": "Answers to clarification questions, if any."},
                },
                "required": ["context", "instructions"],
            },
        ),
        Tool(
            name="generate_drawio_diagram",
            description="Generate a draw.io XML architecture diagram with Azure service icons. Returns XML that can be edited in draw.io.",
            inputSchema={
                "type": "object",
                "properties": {
                    "context": {"type": "string", "description": "Extracted text from all uploaded project artifacts."},
                    "instructions": {"type": "string", "description": "User's specific instructions for the architecture diagram."},
                    "answers": {"type": "string", "description": "Answers to clarification questions, if any."},
                },
                "required": ["context", "instructions"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    ctx = arguments.get("context", "")
    inst = arguments.get("instructions", "")
    ans = arguments.get("answers", "")

    if name == "generate_architecture_diagram":
        result = await generate_architecture_diagram(ctx, inst, ans)
    elif name == "generate_dfd":
        result = await generate_dfd(ctx, inst, ans)
    elif name == "generate_presales_ppt":
        result = await generate_presales_ppt(ctx, inst, ans)
    elif name == "generate_drawio_diagram":
        result = await generate_drawio_architecture(ctx, inst, ans)
    else:
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

    return [TextContent(type="text", text=json.dumps(result, default=str))]


sse = SseServerTransport("/messages/")


async def handle_sse(request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await server.run(streams[0], streams[1], server.create_initialization_options())


app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ],
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


if __name__ == "__main__":
    print(f"MCP Server starting on port {settings.MCP_SERVER_PORT}...")
    uvicorn.run(app, host="0.0.0.0", port=settings.MCP_SERVER_PORT)
