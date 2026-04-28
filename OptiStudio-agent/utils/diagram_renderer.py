"""Render diagrams using the Python `diagrams` library and Mermaid via Kroki API."""


import os
import tempfile
import httpx
import sys
import logging

logger = logging.getLogger(__name__)


async def render_mermaid_png(mermaid_code: str) -> bytes:
    """Render Mermaid diagram to PNG using Kroki.io API (no local install needed)."""
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://kroki.io/mermaid/png",
            content=mermaid_code.encode("utf-8"),
            headers={"Content-Type": "text/plain"},
        )
        response.raise_for_status()
        return response.content


async def render_architecture_with_diagrams_lib(components: list, connections: list, project_name: str) -> bytes:
    """Generate architecture diagram using the Python `diagrams` library.

    This produces precise diagrams with official Azure/AWS/GCP icons.
    Requires graphviz installed on the system.
    """
    code = _build_diagrams_code(components, connections, project_name)

    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "diagram.py")
        output_path = os.path.join(tmpdir, "architecture")

        final_code = code.replace("__OUTPUT_PATH__", output_path)
        with open(script_path, "w") as f:
            f.write(final_code)

        import subprocess
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            cwd=tmpdir,
            timeout=30,
        )

        png_path = output_path + ".png"
        if os.path.exists(png_path):
            with open(png_path, "rb") as f:
                return f.read()

        raise RuntimeError(f"Diagram generation failed: {result.stderr}")


# Azure service mapping for the `diagrams` library
_AZURE_SERVICE_MAP = {
    "app service": "from diagrams.azure.compute import AppServices",
    "azure functions": "from diagrams.azure.compute import FunctionApps",
    "azure sql": "from diagrams.azure.database import SQLDatabases",
    "cosmos db": "from diagrams.azure.database import CosmosDb",
    "blob storage": "from diagrams.azure.storage import BlobStorage",
    "azure cdn": "from diagrams.azure.network import CDNProfiles",
    "front door": "from diagrams.azure.network import FrontDoors",
    "api management": "from diagrams.azure.integration import APIManagement",
    "service bus": "from diagrams.azure.integration import ServiceBus",
    "event grid": "from diagrams.azure.integration import EventGridDomains",
    "key vault": "from diagrams.azure.security import KeyVaults",
    "active directory": "from diagrams.azure.identity import ActiveDirectory",
    "monitor": "from diagrams.azure.devops import ApplicationInsights",
    "redis": "from diagrams.azure.database import CacheForRedis",
    "container": "from diagrams.azure.compute import ContainerInstances",
    "aks": "from diagrams.azure.compute import KubernetesServices",
    "vm": "from diagrams.azure.compute import VM",
    "load balancer": "from diagrams.azure.network import LoadBalancers",
    "vnet": "from diagrams.azure.network import VirtualNetworks",
    "default": "from diagrams.azure.general import Helpcircle",
}


def _resolve_import(technology: str) -> tuple[str, str]:
    """Resolve a technology name to a diagrams library import + class name."""
    tech_lower = technology.lower()
    for key, import_stmt in _AZURE_SERVICE_MAP.items():
        if key in tech_lower:
            class_name = import_stmt.rsplit(" ", 1)[-1]
            return import_stmt, class_name

    default_import = _AZURE_SERVICE_MAP["default"]
    class_name = default_import.rsplit(" ", 1)[-1]
    return default_import, class_name


def _build_diagrams_code(components: list, connections: list, project_name: str) -> str:
    """Build Python code for the `diagrams` library."""
    imports = set()
    imports.add("from diagrams import Diagram, Cluster, Edge")

    node_lines = []
    var_names = {}

    for i, comp in enumerate(components):
        var = f"node_{i}"
        var_names[comp["name"]] = var
        imp, cls = _resolve_import(comp.get("technology", "default"))
        imports.add(imp)
        # Sanitize label to remove problematic characters
        comp_name = _sanitize_text(comp["name"])
        comp_tech = _sanitize_text(comp.get("technology", ""))
        label = f'{comp_name}\\n({comp_tech})'
        node_lines.append(f'    {var} = {cls}("{label}")')

    conn_lines = []
    for conn in connections:
        src = var_names.get(conn["from"])
        dst = var_names.get(conn["to"])
        if src and dst:
            label = _sanitize_text(conn.get("description", conn.get("protocol", "")))
            conn_lines.append(f'    {src} >> Edge(label="{label}") >> {dst}')

    # Sanitize project name to ASCII-safe characters
    safe_name = _sanitize_text(project_name)

    # Add UTF-8 encoding declaration to the generated Python file
    code = "# -*- coding: utf-8 -*-\n"
    code += "\n".join(sorted(imports)) + "\n\n"
    code += f'with Diagram("{safe_name} Architecture", filename="__OUTPUT_PATH__", show=False, direction="TB"):\n'
    code += "\n".join(node_lines) + "\n"
    code += "\n".join(conn_lines) + "\n"
    return code


def _sanitize_text(text: str) -> str:
    """Sanitize text to remove/replace problematic Unicode characters."""
    if not text:
        return ""

    # Replace common problematic characters
    replacements = {
        '–': '-',   # en-dash
        '—': '-',   # em-dash
        '\u2018': "'",  # left single smart quote
        '\u2019': "'",  # right single smart quote
        '\u201C': '"',  # left double smart quote
        '\u201D': '"',  # right double smart quote
        '…': '...',  # ellipsis
        '\u2013': '-',  # en-dash (unicode)
        '\u2014': '-',  # em-dash (unicode)
        '\ufffd': '',   # replacement character
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove any remaining non-ASCII characters that could cause issues
    # Keep only printable ASCII characters
    sanitized = ''.join(c if ord(c) < 128 else '-' for c in text)

    # Escape quotes for Python strings
    sanitized = sanitized.replace('"', '\\"')

    return sanitized


def _mermaid_safe(text: str) -> str:
    """Escape text for Mermaid diagram labels."""
    if not text:
        return ""
    # Remove characters that break Mermaid syntax
    for ch in ['[', ']', '(', ')', '{', '}', '"', '`', '#', ';', '&', '<', '>']:
        text = text.replace(ch, ' ')
    # Collapse whitespace
    return ' '.join(text.split())


def graph_to_mermaid(graph: dict, project_name: str = "Architecture") -> str:
    """Convert an architecture graph (nodes/edges/groups) to Mermaid flowchart syntax.

    Args:
        graph: dict with 'groups', 'nodes', 'edges' from generate_architecture_diagram
        project_name: used in the title comment

    Returns:
        Mermaid flowchart string
    """
    lines = ["flowchart TB"]

    groups = graph.get("groups", [])
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    # Build group-id -> group map
    group_map = {g["id"]: g for g in groups}

    # Build group-id -> [nodes] map
    grouped_nodes: dict[str, list] = {}
    ungrouped_nodes: list = []
    for n in nodes:
        gid = n.get("group", "")
        if gid and gid in group_map:
            grouped_nodes.setdefault(gid, []).append(n)
        else:
            ungrouped_nodes.append(n)

    # Render grouped nodes in subgraphs
    for gid, g in group_map.items():
        label = _mermaid_safe(g.get("label", gid))
        lines.append(f"    subgraph {gid}[\"{label}\"]")
        for n in grouped_nodes.get(gid, []):
            nid = n["id"]
            nlabel = _mermaid_safe(n.get("label", nid))
            tech = _mermaid_safe(n.get("technology", ""))
            display = f"{nlabel}\\n{tech}" if tech else nlabel
            lines.append(f"        {nid}[\"{display}\"]")
        lines.append("    end")

    # Render ungrouped nodes
    for n in ungrouped_nodes:
        nid = n["id"]
        nlabel = _mermaid_safe(n.get("label", nid))
        tech = _mermaid_safe(n.get("technology", ""))
        display = f"{nlabel}\\n{tech}" if tech else nlabel
        lines.append(f"    {nid}[\"{display}\"]")

    # Render edges
    for e in edges:
        src = e.get("source", "")
        tgt = e.get("target", "")
        label = _mermaid_safe(e.get("label", ""))
        if label:
            lines.append(f"    {src} -->|\"{label}\"| {tgt}")
        else:
            lines.append(f"    {src} --> {tgt}")

    return "\n".join(lines)


async def render_architecture_graph_to_png(graph: dict, project_name: str = "Architecture") -> bytes:
    """Convert architecture graph JSON to a PNG image via Mermaid + Kroki.

    This is used when generating a PPT that needs an architecture image
    but the user hasn't exported one from the React Flow editor.
    Filters out any DFD/process/dataflow nodes before rendering.
    """
    def is_valid_architecture_node(node):
        # Only allow nodes with a valid Azure service/component type
        # Forbid generic process/dataflow/step nodes
        forbidden_labels = ["process", "step", "data flow", "flow", "activity", "operation"]
        label = (node.get("label") or "").lower()
        azure_types = [
            "app-service", "functions", "container-apps", "aks", "virtual-machines", "batch",
            "api-management", "logic-apps", "service-bus", "event-grid", "event-hub", "data-factory",
            "openai", "ai-search", "machine-learning", "cognitive-services", "bot-service", "ai-foundry",
            "cosmos-db", "sql-database", "blob-storage", "data-lake", "synapse", "redis", "databricks",
            "virtual-network", "subnet", "application-gateway", "cdn", "private-endpoint", "load-balancer", "front-door",
            "entra-id", "key-vault", "defender", "sentinel",
            "monitor", "application-insights", "log-analytics", "devops",
            "user", "ms-teams", "sharepoint", "power-bi", "microsoft-fabric"
        ]
        if any(lbl in label for lbl in forbidden_labels):
            return False
        azure_type = node.get("azureType") or node.get("azure_type")
        if azure_type and azure_type.lower() in azure_types:
            return True
        # Allow containers/decoration/brain/future if nodeType is correct
        node_type = (node.get("nodeType") or "").lower()
        if node_type in ["container", "decoration", "brain", "future"]:
            return True
        return False

    filtered_nodes = [n for n in graph.get("nodes", []) if is_valid_architecture_node(n)]
    valid_ids = set(n["id"] for n in filtered_nodes)
    filtered_edges = [e for e in graph.get("edges", []) if e.get("source") in valid_ids and e.get("target") in valid_ids]
    filtered_graph = dict(graph)
    filtered_graph["nodes"] = filtered_nodes
    filtered_graph["edges"] = filtered_edges

    mermaid_code = graph_to_mermaid(filtered_graph, project_name)
    logger.info("Rendering architecture graph to PNG via Kroki (%d chars)...", len(mermaid_code))
    return await render_mermaid_png(mermaid_code)


async def render_drawio_xml_to_png(xml: str) -> bytes:
    """Render draw.io XML to PNG using the diagrams.net export API.

    This produces a high-quality PNG with official Azure icons rendered
    by draw.io's own server-side renderer.

    Falls back to Kroki if the draw.io export API is unavailable.
    """

    # draw.io's official export service
    export_url = "https://convert.diagrams.net/node/export"

    payload = {
        "xml": xml,
        "format": "png",
        "w": 1600,
        "h": 1200,
        "bg": "#ffffff",
        "border": 10,
        "scale": 2,
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                export_url,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            png_bytes = response.content
            if png_bytes and len(png_bytes) > 100:
                logger.info("Draw.io export API returned %d bytes PNG", len(png_bytes))
                return png_bytes
            logger.warning("Draw.io export API returned empty/small response (%d bytes)", len(png_bytes))
    except Exception as e:
        logger.warning("Draw.io export API failed: %s. Trying alternative method...", e)

    # There is currently no supported fallback for draw.io XML if the diagrams.net export API fails.
    raise RuntimeError("Could not render draw.io XML to PNG: diagrams.net export API failed and no fallback is available.")
