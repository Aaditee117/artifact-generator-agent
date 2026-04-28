"""DFD generation tool — uses Mermaid (Kroki API) + DALL-E 3."""

import json
from openai import AzureOpenAI
from config import settings
from utils.prompts import DFD_ANALYSIS_PROMPT
 # NOTE: The following imports are currently unused in this file.
 # Remove them to avoid confusion and keep dependencies clear.
 # from utils.prompts import DALLE_DFD_PROMPT, MERMAID_DFD_L0_TEMPLATE, MERMAID_DFD_L1_TEMPLATE
 # from utils.dalle_client import generate_image
 # from utils.diagram_renderer import render_mermaid_png
 # from utils.blob_storage import upload_bytes


def _get_chat_client() -> AzureOpenAI:
    return AzureOpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    )


from tools.architecture_tool import _normalize_graph

async def generate_dfd(
    context: str,
    instructions: str,
    answers: str = "",
    session_folder: str | None = None,
) -> dict:
    """Analyze context and generate a unified DFD diagram.

    Returns dict with the normalized React Flow graph.
    """
    client = _get_chat_client()

    prompt = DFD_ANALYSIS_PROMPT.format(
        context=context, instructions=instructions, answers=answers,
    )
    
    print("🔄 Generating unified DFD graph...")
    response = client.chat.completions.create(
        model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    spec = json.loads(response.choices[0].message.content)

    # Enforce vertical layout and simplicity in the normalized graph
    graph = _normalize_graph(spec)

    # Post-process: enforce top-to-bottom layout and limit complexity
    nodes = graph.get('nodes', [])
    edges = graph.get('edges', [])

    # Sort nodes by group: external, processes, stores (for vertical stacking)
    group_order = {"external": 0, "processes": 1, "stores": 2}
    nodes.sort(key=lambda n: group_order.get(n.get("group", ""), 99))

    # Assign vertical positions (x fixed, y increases)
    x_pos = 300
    y_start = 100
    y_gap = 150
    for idx, node in enumerate(nodes):
        node["position"] = {"x": x_pos, "y": y_start + idx * y_gap}

    # Limit to max 6 nodes and 5 edges for simplicity
    nodes = nodes[:6]
    edges = edges[:5]
    graph['nodes'] = nodes
    graph['edges'] = edges

    print(f"✅ DFD graph generated:")
    print(f"   - Groups: {len(graph['groups'])}")
    print(f"   - Nodes: {len(graph['nodes'])}")
    print(f"   - Edges: {len(graph['edges'])}")

    return {
        "success": True,
        "project_name": spec.get("project_name", "DFD"),
        "graph": graph
    }
