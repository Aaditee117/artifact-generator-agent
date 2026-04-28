"""Draw.io architecture diagram tool.

Uses LLM to analyze project context and generate a draw.io XML diagram
with Azure service icons. The resulting XML can be loaded into draw.io
for editing, and then saved back to blob storage.
"""

import json
import logging

from openai import AzureOpenAI
from config import settings
from tools.drawio_client import create_drawio_diagram, AZURE_ICON_STYLES
from utils.blob_storage import upload_bytes
from utils.diagram_renderer import render_drawio_xml_to_png

logger = logging.getLogger(__name__)

DRAWIO_ARCHITECTURE_PROMPT = """You are an expert Azure cloud solution architect.
Analyze the project context below and produce a JSON object describing a PROFESSIONAL Azure architecture
diagram with draw.io nodes and edges. Create a diagram similar to official Microsoft Azure architecture examples.

**Available Azure icon types** (use these exact strings for the "azureType" field):
{icon_types}

**Output JSON schema** — respond with ONLY valid JSON, no markdown:
{{
  "project_name": "string — short project name",
  "title": "string — diagram title (e.g., 'AI-Powered Presales Platform Architecture')",
  "nodes": [
    {{
      "id": "unique-string-id",
      "label": "Display Name\\n(with line breaks for multiline)",
      "azureType": "one of the icon types above (use exact match)",
      "group": "tier name: external | frontend | gateway | api | backend | ai | integration | data | database | security | monitoring | devops"
    }}
  ],
  "edges": [
    {{
      "source": "node-id",
      "target": "node-id",
      "label": "short description (optional)",
      "protocol": "HTTPS | REST | gRPC | AMQP | TCP | WebSocket | etc."
    }}
  ]
}}

**Critical Architecture Rules:**
1. **Professional Grouping**: Group related services by tier for container layout
   - External: users, browsers, mobile apps
   - Frontend: web apps, CDN, front door
   - Gateway: API Management, Application Gateway
   - API: API services, container apps
   - Backend: app services, function apps
   - AI: OpenAI, AI Search, Cognitive Services, Foundry
   - Integration: Service Bus, Event Hub, Logic Apps
   - Data/Database: Cosmos DB, SQL, Storage, Blob
   - Security/Monitoring/DevOps: bottom tier (KeyVault, App Insights, DevOps, Monitor)

2. **Node Count**:
   - POC: 8-12 nodes (minimal, basic tiers)
   - MVP: 15-25 nodes (production-ready with HA, security, monitoring)

3. **Use Correct Icons**: Match Azure service names exactly:
   - "openai" for Azure OpenAI
   - "cosmos-db" or "cosmosdb" for Cosmos DB
   - "container-apps" for Azure Container Apps
   - "api" or "api-management" for API Management
   - "function-app" for Azure Functions
   - "storage" or "blob-storage" for Storage
   - "ai-search" or "search" for AI Search
   - "teams" for MS Teams, "sharepoint" for SharePoint
   - "foundry" for MS Foundry, "document-intelligence" for Document Intelligence

4. **Data Flow**: Create logical edges showing:
   - User → Frontend → Gateway → API → Backend → AI → Data
   - Include authentication, storage, and monitoring connections

5. **Professional Details**:
   - Use descriptive labels with line breaks (\\n) for multiline text
   - Show all major integrations
   - Include external dependencies (Teams, SharePoint, etc.)
   - Add monitoring and security layer at bottom

**Project context:**
{context}

**User instructions:**
{instructions}

**Clarification answers:**
{answers}
"""


def _get_chat_client() -> AzureOpenAI:
    return AzureOpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    )


async def generate_drawio_architecture(
    context: str,
    instructions: str,
    answers: str = "",
    phase_type: str | None = None,
    session_folder: str | None = None,
) -> dict:
    """Generate a draw.io XML architecture diagram via LLM.

    1. LLM analyzes context and produces nodes/edges JSON
    2. drawio_client converts to draw.io XML with Azure icons
    3. Returns XML, edit_url, embed_url, and optionally uploads to blob

    Args:
        context: Extracted text from project artifacts
        instructions: User instructions
        answers: Clarification answers
        phase_type: 'poc' or 'mvp'
        session_folder: Blob storage session folder

    Returns:
        dict with xml, edit_url, embed_url, project_name, and optionally blob_url
    """
    client = _get_chat_client()

    icon_types = ", ".join(sorted(AZURE_ICON_STYLES.keys()))
    phase_hint = ""
    if phase_type == "poc":
        phase_hint = "\n\nGenerate a POC-level architecture (6-10 nodes, minimal components)."
    elif phase_type == "mvp":
        phase_hint = "\n\nGenerate an MVP production-ready architecture (12-20 nodes, include HA, monitoring, security)."

    prompt = DRAWIO_ARCHITECTURE_PROMPT.format(
        icon_types=icon_types,
        context=context,
        instructions=instructions + phase_hint,
        answers=answers,
    )

    print(f"🎨 Generating draw.io architecture diagram (phase: {phase_type or 'default'})...")

    response = client.chat.completions.create(
        model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    spec = json.loads(response.choices[0].message.content)
    nodes = spec.get("nodes", [])
    edges = spec.get("edges", [])
    project_name = spec.get("project_name", "Architecture")
    title = spec.get("title", f"{project_name} - Architecture Diagram")

    print(f"   LLM returned {len(nodes)} nodes, {len(edges)} edges")

    # Use drawio_client to build the XML diagram
    diagram = create_drawio_diagram(
        nodes=nodes,
        edges=edges,
        title=title,
    )

    result = {
        "project_name": project_name,
        "title": title,
        "xml": diagram["xml"],
        "edit_url": diagram["edit_url"],
        "embed_url": diagram["embed_url"],
        "node_count": len(nodes),
        "edge_count": len(edges),
        "phase_type": phase_type,
    }

    # Upload both XML and PNG to blob storage
    if session_folder:
        safe_name = project_name.replace(' ', '_')
        
        # 1. Upload the XML
        xml_bytes = diagram["xml"].encode("utf-8")
        xml_file_name = f"{safe_name}_architecture.drawio"
        xml_url, xml_storage_path = await upload_bytes(
            xml_bytes,
            xml_file_name,
            "application/xml",
            session_folder=session_folder,
            subfolder="generated",
        )
        result["blob_url"] = xml_url
        result["storage_path"] = xml_storage_path
        print(f"   ✅ Draw.io XML uploaded to blob: {xml_storage_path}")

        # 2. Render XML to PNG and upload
        try:
            print(f"   🖼️  Rendering draw.io XML to PNG...")
            png_bytes = await render_drawio_xml_to_png(diagram["xml"])
            png_file_name = f"{safe_name}_architecture.png"
            png_url, png_storage_path = await upload_bytes(
                png_bytes,
                png_file_name,
                "image/png",
                session_folder=session_folder,
                subfolder="generated",
            )
            result["image_url"] = png_url
            result["image_storage_path"] = png_storage_path
            print(f"   ✅ Architecture diagram PNG uploaded to blob: {png_storage_path}")
        except Exception as e:
            logger.warning(f"Failed to render/upload PNG: {e}. XML is still available.")
            # Continue without PNG if rendering fails

    print(f"✅ Draw.io diagram ready: {title}")
    return result


async def save_drawio_diagram(
    xml: str,
    project_name: str = "architecture",
    session_folder: str | None = None,
    export_format: str = "xml",
    image_data: bytes | None = None,
) -> dict:
    """Save a draw.io diagram (XML and optionally an exported image) to blob storage.

    Called when user saves from the draw.io editor iframe.

    Args:
        xml: The draw.io XML content
        project_name: Project name for file naming
        session_folder: Blob storage session folder
        export_format: 'xml', 'png', or 'svg'
        image_data: Exported image bytes (PNG or SVG) if available

    Returns:
        dict with xml_url and optionally image_url
    """
    result = {}
    safe_name = project_name.replace(" ", "_")

    # Always save the XML
    xml_bytes = xml.encode("utf-8")
    xml_filename = f"{safe_name}_architecture.drawio"
    xml_url, xml_path = await upload_bytes(
        xml_bytes,
        xml_filename,
        "application/xml",
        session_folder=session_folder,
        subfolder="generated",
    )
    result["xml_url"] = xml_url
    result["xml_storage_path"] = xml_path
    print(f"✅ Draw.io XML saved: {xml_path}")

    # Save exported image if provided
    if image_data:
        if export_format == "svg":
            img_filename = f"{safe_name}_architecture.svg"
            content_type = "image/svg+xml"
        else:
            img_filename = f"{safe_name}_architecture.png"
            content_type = "image/png"

        img_url, img_path = await upload_bytes(
            image_data,
            img_filename,
            content_type,
            session_folder=session_folder,
            subfolder="generated",
        )
        result["image_url"] = img_url
        result["image_storage_path"] = img_path
        print(f"✅ Draw.io export saved: {img_path}")

    return result
