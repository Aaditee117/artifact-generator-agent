"""Draw.io XML Generator for Architecture Diagrams.

Uses draw.io's built-in Azure icon library (azure2) which contains official Microsoft Azure icons.
Icons are kept in sync with Microsoft's architecture guidelines.

Reference: https://learn.microsoft.com/en-us/azure/architecture/icons/
"""

import base64
import zlib
import urllib.parse
from datetime import datetime

# Azure Icon Styles - Maps service names to draw.io's built-in Azure2 library icons
# Updated to match Microsoft's official Azure Architecture icon set (2024-2026)
# Deprecated/discontinued services are noted with comments
AZURE_ICON_STYLES = {
    # === Compute Services ===
    "app-service": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/app_services/App_Services.svg;",
    "app-services": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/app_services/App_Services.svg;",
    "function-app": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/compute/Function_Apps.svg;",
    "function-apps": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/compute/Function_Apps.svg;",
    "functions": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/compute/Function_Apps.svg;",
    "vm": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/compute/Virtual_Machine.svg;",
    "virtual-machine": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/compute/Virtual_Machine.svg;",
    "virtual-machines": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/compute/Virtual_Machine.svg;",
    "vmss": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/compute/VM_Scale_Sets.svg;",
    "vm-scale-sets": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/compute/VM_Scale_Sets.svg;",
    "batch": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/compute/Batch_Accounts.svg;",
    "web-app": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/app_services/App_Services.svg;",
    "webapp": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/app_services/App_Services.svg;",
    "static-web-app": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/app_services/Static_Apps.svg;",
    "static-app": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/app_services/Static_Apps.svg;",
    
    # === Container Services ===
    "container-apps": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/containers/Container_Apps.svg;",
    "container-instances": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/containers/Container_Instances.svg;",
    "kubernetes": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/containers/Kubernetes_Services.svg;",
    "aks": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/containers/Kubernetes_Services.svg;",
    "kubernetes-services": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/containers/Kubernetes_Services.svg;",
    "container-registry": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/containers/Container_Registries.svg;",
    "acr": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/containers/Container_Registries.svg;",
    
    # === Database Services ===
    "cosmos-db": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/databases/Azure_Cosmos_DB.svg;",
    "cosmosdb": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/databases/Azure_Cosmos_DB.svg;",
    "sql-database": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/databases/SQL_Database.svg;",
    "sql": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/databases/SQL_Database.svg;",
    "sql-server": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/databases/SQL_Server.svg;",
    "azure-sql": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/databases/Azure_SQL.svg;",
    "mysql": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/databases/Azure_Database_MySQL_Server.svg;",
    "postgresql": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/databases/Azure_Database_PostgreSQL_Server.svg;",
    "redis": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/databases/Cache_Redis.svg;",
    "cache-redis": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/databases/Cache_Redis.svg;",
    
    # === Storage Services ===
    "storage": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/storage/Storage_Accounts.svg;",
    "storage-account": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/storage/Storage_Accounts.svg;",
    "storage-accounts": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/storage/Storage_Accounts.svg;",
    "blob-storage": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/storage/Storage_Accounts.svg;",
    "blob": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/storage/Storage_Accounts.svg;",
    "file-storage": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/storage/Storage_Accounts.svg;",
    "data-lake": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/storage/Data_Lake_Storage_Gen1.svg;",
    
    # === AI & Machine Learning Services ===
    "openai": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/ai_machine_learning/Azure_OpenAI.svg;",
    "azure-openai": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/ai_machine_learning/Azure_OpenAI.svg;",
    "cognitive-services": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/ai_machine_learning/Cognitive_Services.svg;",
    "ai-services": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/ai_machine_learning/Cognitive_Services.svg;",
    "machine-learning": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/ai_machine_learning/Machine_Learning.svg;",
    "ml": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/ai_machine_learning/Machine_Learning.svg;",
    "search": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/ai_machine_learning/Search_Services.svg;",
    "ai-search": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/ai_machine_learning/Search_Services.svg;",
    "cognitive-search": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/ai_machine_learning/Search_Services.svg;",  # Renamed to AI Search
    "bot-service": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/ai_machine_learning/Bot_Services.svg;",
    "bot-services": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/ai_machine_learning/Bot_Services.svg;",
    "document-intelligence": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/ai_machine_learning/Cognitive_Services.svg;",
    "form-recognizer": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/ai_machine_learning/Cognitive_Services.svg;",  # Renamed to Document Intelligence
    "computer-vision": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/ai_machine_learning/Cognitive_Services.svg;",
    "speech": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/ai_machine_learning/Cognitive_Services.svg;",
    "language": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/ai_machine_learning/Cognitive_Services.svg;",
    
    # === AI Foundry / Models ===
    "foundry": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/ai_machine_learning/Machine_Learning.svg;",
    "ai-foundry": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/ai_machine_learning/Machine_Learning.svg;",
    "azure-ai-foundry": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/ai_machine_learning/Machine_Learning.svg;",
    
    # === Networking Services ===
    "vnet": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/networking/Virtual_Networks.svg;",
    "virtual-network": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/networking/Virtual_Networks.svg;",
    "virtual-networks": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/networking/Virtual_Networks.svg;",
    "subnet": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/networking/Subnet.svg;",
    "api-management": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/integration/API_Management_Services.svg;",
    "api": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/integration/API_Management_Services.svg;",
    "apim": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/integration/API_Management_Services.svg;",
    "application-gateway": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/networking/Application_Gateways.svg;",
    "app-gateway": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/networking/Application_Gateways.svg;",
    "load-balancer": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/networking/Load_Balancers.svg;",
    "front-door": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/networking/Front_Doors.svg;",
    "cdn": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/networking/CDN_Profiles.svg;",
    "cdn-profile": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/networking/CDN_Profiles.svg;",
    "firewall": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/networking/Firewalls.svg;",
    "vpn-gateway": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/networking/Virtual_Network_Gateways.svg;",
    "dns": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/networking/DNS_Zones.svg;",
    "bastion": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/networking/Bastions.svg;",
    "private-link": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/networking/Private_Link.svg;",
    "private-endpoint": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/networking/Private_Link.svg;",
    
    # === Integration & Messaging ===
    "service-bus": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/integration/Service_Bus.svg;",
    "event-hub": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/analytics/Event_Hubs.svg;",
    "event-hubs": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/analytics/Event_Hubs.svg;",
    "event-grid": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/integration/Event_Grid_Domains.svg;",
    "logic-apps": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/integration/Logic_Apps.svg;",
    "logic-app": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/integration/Logic_Apps.svg;",
    
    # === Security & Identity ===
    "key-vault": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/security/Key_Vaults.svg;",
    "keyvault": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/security/Key_Vaults.svg;",
    "entra-id": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/identity/Azure_Active_Directory.svg;",
    "active-directory": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/identity/Azure_Active_Directory.svg;",  # Renamed to Entra ID
    "azure-ad": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/identity/Azure_Active_Directory.svg;",  # Renamed to Entra ID
    "entra": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/identity/Azure_Active_Directory.svg;",
    "managed-identity": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/identity/Managed_Identities.svg;",
    "sentinel": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/security/Azure_Sentinel.svg;",
    "defender": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/security/Microsoft_Defender_for_Cloud.svg;",
    
    # === Monitoring & DevOps ===
    "monitor": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/management_governance/Monitor.svg;",
    "azure-monitor": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/management_governance/Monitor.svg;",
    "application-insights": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/management_governance/Application_Insights.svg;",
    "app-insights": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/management_governance/Application_Insights.svg;",
    "log-analytics": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/analytics/Log_Analytics_Workspaces.svg;",
    "devops": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/devops/Azure_DevOps.svg;",
    "azure-devops": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/devops/Azure_DevOps.svg;",
    
    # === Analytics ===
    "synapse": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/analytics/Azure_Synapse_Analytics.svg;",
    "synapse-analytics": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/analytics/Azure_Synapse_Analytics.svg;",
    "databricks": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/analytics/Azure_Databricks.svg;",
    "data-factory": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/analytics/Data_Factories.svg;",
    
    # === User/Client Icons ===
    "user": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/identity/Users.svg;",
    "users": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/identity/Groups.svg;",
    "browser": "rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;",
    "web": "rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;",
    "mobile": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/intune/Client_Apps.svg;",
    
    # === Microsoft 365 / External Services ===
    "teams": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/general/MS_Teams.svg;",
    "ms-teams": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/general/MS_Teams.svg;",
    "sharepoint": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/general/SharePoint.svg;",
    "power-bi": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/analytics/Power_BI_Embedded.svg;",
    "microsoft-fabric": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/analytics/Azure_Synapse_Analytics.svg;",
    
    # === General / Branding ===
    "azure": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/general/10001_icon_service_Azure.svg;",
    "azure-logo": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/general/10001_icon_service_Azure.svg;",
    "microsoft-azure": "sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/azure2/general/10001_icon_service_Azure.svg;",
}


def _escape_xml(text):
    if not text:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _get_icon_style(service_type):
    normalized = service_type.lower().strip() if service_type else "app-service"
    return AZURE_ICON_STYLES.get(normalized, AZURE_ICON_STYLES["app-service"])


def _auto_layout_nodes(nodes):
    """Create professional layout with container grouping similar to Azure architecture diagrams."""
    tier_nodes = {}
    tier_order = ["external", "frontend", "gateway", "api", "backend", "ai", "integration", "data", "database"]
    bottom_tiers = ["security", "monitoring", "devops"]
    
    # Group nodes by tier
    for node in nodes:
        tier = node.get("group", node.get("tier", "backend"))
        if tier:
            tier = tier.lower()
        else:
            tier = "backend"
        if tier not in tier_nodes:
            tier_nodes[tier] = []
        tier_nodes[tier].append(node)
    
    # Professional layout parameters
    start_x, start_y = 120, 140
    column_width = 240
    column_gap = 80
    node_width, node_height = 80, 100
    vertical_spacing = 130
    container_padding = 40
    
    positioned = []
    containers = []
    current_x = start_x
    max_y = start_y
    
    # Layout main tiers in columns
    for tier in tier_order:
        if tier not in tier_nodes:
            continue
        
        tier_list = tier_nodes[tier]
        column_height = len(tier_list) * vertical_spacing
        
        # Create container for this tier if multiple nodes
        if len(tier_list) > 1:
            container_x = current_x - container_padding
            container_y = start_y - container_padding
            container_w = column_width
            container_h = column_height + container_padding
            
            containers.append({
                "id": f"container_{tier}",
                "label": tier.replace("_", " ").title(),
                "x": container_x,
                "y": container_y,
                "width": container_w,
                "height": container_h,
            })
        
        # Position nodes in this tier
        for i, node in enumerate(tier_list):
            node_x = current_x + (column_width - node_width) // 2
            node_y = start_y + i * vertical_spacing
            positioned.append({
                **node,
                "x": node_x,
                "y": node_y,
                "width": node_width,
                "height": node_height
            })
            max_y = max(max_y, node_y + node_height)
        
        current_x += column_width + column_gap
    
    # Position bottom tier (security, monitoring, devops) in a row at the bottom
    bottom_y = max_y + 100
    bottom_x = start_x
    for tier in bottom_tiers:
        if tier not in tier_nodes:
            continue
        for node in tier_nodes[tier]:
            positioned.append({
                **node,
                "x": bottom_x,
                "y": bottom_y,
                "width": 60,
                "height": 60
            })
            bottom_x += 100
    
    return positioned, containers


def _encode_for_url(xml):
    try:
        compressed = zlib.compress(xml.encode("utf-8"), 9)[2:-4]
        b64 = base64.b64encode(compressed).decode("utf-8")
        return urllib.parse.quote(b64, safe="")
    except Exception:
        b64 = base64.b64encode(xml.encode("utf-8")).decode("utf-8")
        return urllib.parse.quote(b64, safe="")


def create_drawio_diagram(nodes, edges, groups=None, title="Architecture Diagram"):
    """Create a professional Azure architecture diagram with containers and branding."""
    groups = groups or []
    print(f"Creating professional draw.io diagram: {len(nodes)} nodes, {len(edges)} edges")
    
    positioned, containers = _auto_layout_nodes(nodes)
    node_id_set = set(n.get("id") for n in positioned if n.get("id"))
    
    cells = []
    cell_id_counter = 10  # Start after reserved IDs
    
    # Add Azure logo in top-right corner
    cells.append(f'    <mxCell id="azure_logo" value="" style="sketch=0;aspect=fixed;html=1;points=[];align=center;image;fontSize=12;image=img/lib/mscae/Microsoft_Azure_Logo.svg;" vertex="1" parent="1"><mxGeometry x="1420" y="20" width="150" height="50" as="geometry"/></mxCell>')
    
    # Add title
    cells.append(f'    <mxCell id="title" value="{_escape_xml(title)}" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=18;fontStyle=1;fontColor=#333333;" vertex="1" parent="1"><mxGeometry x="40" y="30" width="600" height="40" as="geometry"/></mxCell>')
    
    # Add containers (grouped components like VNet, Subnets)
    for container in containers:
        cid = container["id"]
        clabel = _escape_xml(container["label"])
        cx, cy, cw, ch = container["x"], container["y"], container["width"], container["height"]
        # Rounded rectangle with light blue fill for containers
        container_style = "rounded=1;whiteSpace=wrap;html=1;fillColor=#e1f5ff;strokeColor=#2196F3;strokeWidth=2;dashed=1;dashPattern=5 5;fontSize=14;fontStyle=1;verticalAlign=top;align=left;spacingLeft=10;spacingTop=5;"
        cells.append(f'    <mxCell id="{cid}" value="{clabel}" style="{container_style}" vertex="1" parent="1"><mxGeometry x="{cx}" y="{cy}" width="{cw}" height="{ch}" as="geometry"/></mxCell>')
    
    # Add nodes with Azure icons
    for node in positioned:
        nid = node.get("id", f"node_{cell_id_counter}")
        cell_id_counter += 1
        label = _escape_xml(node.get("label", node.get("name", "Service")))
        azure_type = node.get("azureType", node.get("icon", node.get("type", "app-service")))
        style = _get_icon_style(azure_type)
        x, y = node.get("x", 100), node.get("y", 100)
        w, h = node.get("width", 80), node.get("height", 80)
        cells.append(f'    <mxCell id="{nid}" value="{label}" style="{style}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
    
    # Add edges (connections) with professional styling
    for i, edge in enumerate(edges):
        src, tgt = edge.get("source", ""), edge.get("target", "")
        if src not in node_id_set or tgt not in node_id_set:
            continue
        lbl = edge.get("label", "")
        proto = edge.get("protocol", "")
        edge_lbl = f"{lbl} ({proto})" if lbl and proto else (lbl or proto or "")
        # Professional arrow style with rounded edges
        style = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#666666;endArrow=classic;endFill=1;fontSize=11;"
        cells.append(f'    <mxCell id="edge_{i}" value="{_escape_xml(edge_lbl)}" style="{style}" edge="1" parent="1" source="{src}" target="{tgt}"><mxGeometry relative="1" as="geometry"/></mxCell>')
    
    # Add note at bottom about architecture
    note_y = 1100
    cells.append(f'    <mxCell id="note" value="Note: The architecture and AI models are subject to change as per requirements during development phase" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=12;fontColor=#D32F2F;fontStyle=2;" vertex="1" parent="1"><mxGeometry x="40" y="{note_y}" width="800" height="30" as="geometry"/></mxCell>')
    
    cells_xml = "\n".join(cells)
    timestamp = datetime.utcnow().isoformat()
    
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="{timestamp}" agent="OptiStudio" version="22.0.0" type="device">
  <diagram id="architecture" name="{_escape_xml(title)}">
    <mxGraphModel dx="1600" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1600" pageHeight="1200" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
{cells_xml}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''
    
    encoded = _encode_for_url(xml)
    safe_title = urllib.parse.quote(title.replace(" ", "_"))
    edit_url = f"https://app.diagrams.net/?title={safe_title}.drawio#R{encoded}"
    embed_url = f"https://viewer.diagrams.net/?highlight=0000ff&edit=_blank&layers=1&nav=1&title={safe_title}.drawio#R{encoded}"
    
    print(f"Draw.io diagram created - XML: {len(xml)} bytes, URL ready")
    return {"xml": xml, "edit_url": edit_url, "embed_url": embed_url, "format": "drawio"}
