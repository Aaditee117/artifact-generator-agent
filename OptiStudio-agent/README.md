# OptiStudio Agent — Presales Generation Service

Python MCP Client/Server architecture for generating presales deliverables.

## Architecture

```
React (5173) → FastAPI Agent API (8000) → MCP Server (8001)
                     ↓                         ↓
              Azure OpenAI (GPT-4o)     3 Tools:
              Azure OpenAI (DALL-E 3)    ├── Architecture Diagram (diagrams lib + DALL-E)
              Azure Blob Storage         ├── DFD Level 0+1 (Mermaid + DALL-E)
                                         └── Presales PPT (python-pptx)
```

## Prerequisites

1. **Python 3.10+**
2. **Graphviz** (for `diagrams` library):
   ```
   winget install graphviz
   ```
   Or download from https://graphviz.org/download/ and add to PATH.

3. **Azure OpenAI** with deployed models:
   - `gpt-4o` (chat completions)
   - `dall-e-3` (image generation)

4. **Azure Blob Storage** account (`optistudioaa`)

## Setup

```powershell
cd optistudio-agent

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy .env.example to .env and fill in your keys
cp .env.example .env
```

## Running

**Terminal 1 — MCP Server (port 8001):**
```powershell
cd optistudio-agent
.venv\Scripts\activate
python mcp_server.py
```

**Terminal 2 — Agent API (port 8000):**
```powershell
cd optistudio-agent
.venv\Scripts\activate
python main.py
```

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| `POST` | `/api/agent/clarify` | Get clarification questions before generation |
| `POST` | `/api/agent/generate` | Generate architecture diagram / DFD / PPT |
| `POST` | `/api/agent/feedback` | Handle "This is good" / "Need changes" |
| `GET`  | `/health` | Health check |

## Development Startup Order

```
1. Start SQL Server (for .NET API)
2. python mcp_server.py        → MCP Server on :8001
3. python main.py              → Agent API on :8000
4. F5 in Visual Studio         → .NET API on :7126
5. npm run dev                 → React on :5173
```
