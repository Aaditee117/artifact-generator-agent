"""Architecture Diagram generation tool — returns graph data for React Flow rendering.

Supports phase-aware architecture generation:
- POC: Minimal architecture with basic tiers
- MVP: Production-ready architecture with HA
"""

import json
import traceback
from openai import AzureOpenAI
from config import settings
from utils.prompts import ARCHITECTURE_ANALYSIS_PROMPT, get_architecture_prompt, PHASE_TYPE_POC, PHASE_TYPE_MVP
from utils.blob_storage import upload_bytes


def _get_chat_client() -> AzureOpenAI:
    return AzureOpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    )


async def generate_architecture_diagram(
    context: str,
    instructions: str,
    answers: str = "",
    phase_type: str | None = None,
    session_folder: str | None = None,
) -> dict:
    """Analyze context and generate architecture graph data for React Flow rendering.

    Args:
        context: Project artifacts content
        instructions: User instructions
        answers: Clarification answers
        phase_type: 'poc' or 'mvp' for phase-specific architecture

    Returns dict with:
    - graph: The graph structure (nodes, edges, groups) for frontend rendering
    - project_name: Name of the project
    - architecture_style: Style of architecture (microservices, monolithic, etc.)
    - phase_type: The phase type used for generation

    The frontend will:
    1. Render the graph using React Flow
    2. Allow user to drag/edit nodes
    3. Export to SVG/PNG
    4. Send PNG back for PPT embedding
    """
    client = _get_chat_client()

    # Get phase-appropriate prompt
    if phase_type:
        base_prompt = get_architecture_prompt(phase_type)
        phase_label = "POC" if phase_type == PHASE_TYPE_POC else "MVP"
    else:
        base_prompt = ARCHITECTURE_ANALYSIS_PROMPT
        phase_label = None

    # LLM analyzes and produces architecture graph specification
    prompt = base_prompt.format(
        context=context, instructions=instructions, answers=answers,
    )

    print(f"🏗️ Generating architecture graph for project... (Phase: {phase_label or 'Default'})")

    response = client.chat.completions.create(
        model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    spec = json.loads(response.choices[0].message.content)

    # Validate and normalize the graph structure
    graph = _normalize_graph(spec)

    print(f"✅ Architecture graph generated:")
    print(f"   - Groups: {len(graph['groups'])}")
    print(f"   - Nodes: {len(graph['nodes'])}")
    print(f"   - Edges: {len(graph['edges'])}")
    if phase_label:
        print(f"   - Phase: {phase_label}")

    return {
        "project_name": spec.get("project_name", "Architecture"),
        "architecture_style": spec.get("architecture_style", "hybrid"),
        "graph": graph,
        "phase_type": phase_type,
        "phase_label": phase_label,
    }


def _normalize_graph(spec: dict) -> dict:
    """Normalize and validate the graph structure from LLM output."""

    groups = spec.get("groups", [])
    nodes = spec.get("nodes", [])
    edges = spec.get("edges", [])

    # Ensure all groups have required fields (kept for backward compat)
    normalized_groups = []
    for g in groups:
        normalized_groups.append({
            "id": g.get("id", f"group-{len(normalized_groups)}"),
            "label": g.get("label", "Group"),
            "color": g.get("color", "#F3F6FC"),
        })

    # Ensure all nodes have required fields
    node_ids = set()
    normalized_nodes = []
    # For horizontal alignment of footer nodes
    footer_types = ["devops", "key-vault", "monitor", "application-insights"]
    footer_x_start = 50
    footer_y = 900
    footer_spacing = 120
    footer_count = 0

    for n in nodes:
        node_id = n.get("id", f"node-{len(normalized_nodes)}")
        if isinstance(node_id, str):
            node_ids.add(node_id)
        node_type = n.get("nodeType", "service")

        label = n.get("label", n.get("technology", "Node"))
        if node_type == "decoration" and label.strip().lower() == "azure":
            icon = "azure"
            azure_type = "azure"
        else:
            icon = n.get("icon", n.get("azureType", "app-service"))
            azure_type = n.get("azureType", n.get("icon", "app-service"))

        pos = n.get("position")
        is_footer = False
        position = None
        if pos and isinstance(pos, dict):
            is_footer = (azure_type.lower() in footer_types or icon.lower() in footer_types) and pos.get("y") == 800
            position = dict(pos)
            if is_footer:
                position["x"] = footer_x_start + footer_count * footer_spacing
                position["y"] = footer_y
                footer_count += 1

        base = {
            "id": node_id,
            "label": label,
            "technology": n.get("technology", ""),
            "tooltip": n.get("tooltip", n.get("description", "")),
            "group": n.get("group", ""),
            "icon": icon,
            "position": position if is_footer else pos,
            "azureType": azure_type,
            "nodeType": node_type,
            "parentNode": n.get("parentNode"),
            "isFuture": n.get("isFuture", False),
        }

        if node_type == "container":
            base["width"] = n.get("width")
            base["height"] = n.get("height")
            base["containerStyle"] = n.get("containerStyle")

        normalized_nodes.append(base)

    # Ensure all edges reference valid nodes
    normalized_edges = []
    for e in edges:
        source = e.get("source", "")
        target = e.get("target", "")
        if source in node_ids and target in node_ids:
            normalized_edges.append({
                "source": source,
                "target": target,
                "label": e.get("label", ""),
                "protocol": e.get("protocol", "HTTPS"),
                "isFuture": e.get("isFuture", False),
            })
        else:
            print(f"⚠️ Skipping invalid edge: {source} → {target}")

    return {
        "groups": normalized_groups,
        "nodes": normalized_nodes,
        "edges": normalized_edges,
    }


async def save_architecture_image(
    image_bytes: bytes,
    project_name: str = "architecture",
    session_folder: str | None = None,
) -> dict:
    """Save the rendered architecture image (PNG from frontend) to blob storage.

    This is called after the frontend renders and exports the React Flow diagram.
    Returns the URL for embedding in PPT.
    """
    try:
        filename = f"{project_name.replace(' ', '_')}_architecture.png"
        url, storage_path = await upload_bytes(
            image_bytes, filename, "image/png",
            session_folder=session_folder, subfolder="generated",
        )

        print(f"✅ Architecture image saved: {url}")

        return {
            "url": url,
            "storage_path": storage_path,
        }
    except Exception as e:
        print(f"❌ Failed to save architecture image: {e}")
        traceback.print_exc()
        return {
            "error": str(e),
        }

