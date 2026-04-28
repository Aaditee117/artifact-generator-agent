/**
 * Sample Enterprise Architecture Diagrams
 * 
 * Pre-built architecture templates for common Azure patterns
 */

import type { EnterpriseArchitectureSchema } from './enterpriseArchitectureSchema';

/**
 * OptiStudio Enterprise Architecture
 * Compact grid layout with all Azure services
 */
export const optiStudioArchitecture: EnterpriseArchitectureSchema = {
  title: "OptiStudio Enterprise Architecture",
  legend: [
    { symbol: "outlined-box", color: "#0078D4", label: "System Boundary" },
    { symbol: "filled-box", color: "#E8F4FDAA", label: "Functional Layer" },
    { symbol: "solid-line", color: "#333333", label: "Data Flow" }
  ],
  groups: [
    {
      id: "grp-boundary",
      label: "Azure Cloud Environment",
      parentId: null,
      style: {
        backgroundColor: "#FAFBFCAA",
        borderStyle: "solid",
        borderColor: "#0078D4",
        borderWidth: 2,
        borderRadius: 12,
        labelColor: "#0078D4"
      },
      position: { x: 20, y: 20 },
      size: { width: 1160, height: 660 }
    },
    {
      id: "grp-external",
      label: "External Access",
      parentId: "grp-boundary",
      style: {
        backgroundColor: "#F5F5F5AA",
        borderStyle: "solid",
        borderColor: "#666666",
        borderWidth: 1,
        borderRadius: 8,
        labelColor: "#333333"
      },
      position: { x: 40, y: 80 },
      size: { width: 160, height: 280 }
    },
    {
      id: "grp-gateway",
      label: "API Gateway",
      parentId: "grp-boundary",
      style: {
        backgroundColor: "#E8F4FDAA",
        borderStyle: "solid",
        borderColor: "#1E6AA5",
        borderWidth: 1,
        borderRadius: 8,
        labelColor: "#1E6AA5"
      },
      position: { x: 220, y: 80 },
      size: { width: 180, height: 280 }
    },
    {
      id: "grp-compute",
      label: "Application Layer",
      parentId: "grp-boundary",
      style: {
        backgroundColor: "#E8F5E9AA",
        borderStyle: "solid",
        borderColor: "#2E7D32",
        borderWidth: 1,
        borderRadius: 8,
        labelColor: "#2E7D32"
      },
      position: { x: 420, y: 80 },
      size: { width: 300, height: 280 }
    },
    {
      id: "grp-ai",
      label: "AI Services",
      parentId: "grp-boundary",
      style: {
        backgroundColor: "#FFF3E0AA",
        borderStyle: "solid",
        borderColor: "#E65100",
        borderWidth: 1,
        borderRadius: 8,
        labelColor: "#E65100"
      },
      position: { x: 740, y: 80 },
      size: { width: 180, height: 140 }
    },
    {
      id: "grp-data",
      label: "Data Services",
      parentId: "grp-boundary",
      style: {
        backgroundColor: "#F3E5F5AA",
        borderStyle: "solid",
        borderColor: "#7B1FA2",
        borderWidth: 1,
        borderRadius: 8,
        labelColor: "#7B1FA2"
      },
      position: { x: 940, y: 80 },
      size: { width: 220, height: 280 }
    },
    {
      id: "grp-messaging",
      label: "Messaging",
      parentId: "grp-boundary",
      style: {
        backgroundColor: "#E0F7FAAA",
        borderStyle: "solid",
        borderColor: "#00838F",
        borderWidth: 1,
        borderRadius: 8,
        labelColor: "#00838F"
      },
      position: { x: 740, y: 240 },
      size: { width: 180, height: 120 }
    },
    {
      id: "grp-platform",
      label: "Platform & Monitoring",
      parentId: "grp-boundary",
      style: {
        backgroundColor: "#ECEFF1AA",
        borderStyle: "dashed",
        borderColor: "#455A64",
        borderWidth: 1,
        borderRadius: 8,
        labelColor: "#455A64"
      },
      position: { x: 40, y: 400 },
      size: { width: 520, height: 120 }
    },
    {
      id: "grp-security",
      label: "Security",
      parentId: "grp-boundary",
      style: {
        backgroundColor: "#FCE4ECAA",
        borderStyle: "solid",
        borderColor: "#C62828",
        borderWidth: 1,
        borderRadius: 8,
        labelColor: "#C62828"
      },
      position: { x: 580, y: 400 },
      size: { width: 200, height: 120 }
    }
  ],
  nodes: [
    // External Access
    {
      id: "node-user",
      type: "user",
      label: "Users",
      sublabel: null,
      parentGroupId: "grp-external",
      position: { x: 80, y: 140 },
      style: { variant: "default", highlight: false },
      metadata: { description: "End users", tags: [] }
    },
    {
      id: "node-teams",
      type: "ms-teams",
      label: "MS Teams",
      sublabel: null,
      parentGroupId: "grp-external",
      position: { x: 80, y: 240 },
      style: { variant: "default", highlight: false },
      metadata: { description: "Teams integration", tags: [] }
    },
    // Gateway
    {
      id: "node-apim",
      type: "azure-api-management",
      label: "API Management",
      sublabel: null,
      parentGroupId: "grp-gateway",
      position: { x: 270, y: 140 },
      style: { variant: "default", highlight: false },
      metadata: { description: "API Gateway", tags: [] }
    },
    {
      id: "node-frontdoor",
      type: "azure-front-door",
      label: "Front Door",
      sublabel: null,
      parentGroupId: "grp-gateway",
      position: { x: 270, y: 240 },
      style: { variant: "default", highlight: false },
      metadata: { description: "CDN & WAF", tags: [] }
    },
    // Compute
    {
      id: "node-container",
      type: "azure-container-apps",
      label: "Container Apps",
      sublabel: "Backend API",
      parentGroupId: "grp-compute",
      position: { x: 480, y: 140 },
      style: { variant: "default", highlight: true },
      metadata: { description: "Main application", tags: [] }
    },
    {
      id: "node-functions",
      type: "azure-functions",
      label: "Functions",
      sublabel: "Background Jobs",
      parentGroupId: "grp-compute",
      position: { x: 600, y: 140 },
      style: { variant: "default", highlight: false },
      metadata: { description: "Serverless compute", tags: [] }
    },
    {
      id: "node-webapp",
      type: "azure-app-service",
      label: "App Service",
      sublabel: "Frontend",
      parentGroupId: "grp-compute",
      position: { x: 540, y: 260 },
      style: { variant: "default", highlight: false },
      metadata: { description: "Web frontend", tags: [] }
    },
    // AI
    {
      id: "node-openai",
      type: "azure-openai",
      label: "Azure OpenAI",
      sublabel: null,
      parentGroupId: "grp-ai",
      position: { x: 790, y: 130 },
      style: { variant: "default", highlight: false },
      metadata: { description: "AI/LLM", tags: ["ai"] }
    },
    {
      id: "node-search",
      type: "azure-ai-search",
      label: "AI Search",
      sublabel: null,
      parentGroupId: "grp-ai",
      position: { x: 870, y: 130 },
      style: { variant: "default", highlight: false },
      metadata: { description: "Cognitive search", tags: ["ai"] }
    },
    // Messaging
    {
      id: "node-servicebus",
      type: "azure-service-bus",
      label: "Service Bus",
      sublabel: null,
      parentGroupId: "grp-messaging",
      position: { x: 790, y: 290 },
      style: { variant: "default", highlight: false },
      metadata: { description: "Messaging", tags: [] }
    },
    {
      id: "node-eventgrid",
      type: "azure-event-grid",
      label: "Event Grid",
      sublabel: null,
      parentGroupId: "grp-messaging",
      position: { x: 870, y: 290 },
      style: { variant: "default", highlight: false },
      metadata: { description: "Events", tags: [] }
    },
    // Data
    {
      id: "node-sql",
      type: "azure-sql-database",
      label: "SQL Database",
      sublabel: null,
      parentGroupId: "grp-data",
      position: { x: 1000, y: 130 },
      style: { variant: "default", highlight: false },
      metadata: { description: "Relational DB", tags: ["data"] }
    },
    {
      id: "node-cosmos",
      type: "azure-cosmos-db",
      label: "Cosmos DB",
      sublabel: null,
      parentGroupId: "grp-data",
      position: { x: 1100, y: 130 },
      style: { variant: "default", highlight: false },
      metadata: { description: "NoSQL DB", tags: ["data"] }
    },
    {
      id: "node-blob",
      type: "azure-blob-storage",
      label: "Blob Storage",
      sublabel: null,
      parentGroupId: "grp-data",
      position: { x: 1000, y: 240 },
      style: { variant: "default", highlight: false },
      metadata: { description: "File storage", tags: ["data"] }
    },
    {
      id: "node-redis",
      type: "azure-redis-cache",
      label: "Redis Cache",
      sublabel: null,
      parentGroupId: "grp-data",
      position: { x: 1100, y: 240 },
      style: { variant: "default", highlight: false },
      metadata: { description: "Caching", tags: ["data"] }
    },
    // Platform
    {
      id: "node-devops",
      type: "azure-devops",
      label: "DevOps",
      sublabel: null,
      parentGroupId: "grp-platform",
      position: { x: 80, y: 450 },
      style: { variant: "outlined", highlight: false },
      metadata: { description: "CI/CD pipelines", tags: ["platform"] }
    },
    {
      id: "node-keyvault",
      type: "azure-key-vault",
      label: "Key Vault",
      sublabel: null,
      parentGroupId: "grp-platform",
      position: { x: 180, y: 450 },
      style: { variant: "outlined", highlight: false },
      metadata: { description: "Secrets", tags: ["platform"] }
    },
    {
      id: "node-monitor",
      type: "azure-monitor",
      label: "Monitor",
      sublabel: null,
      parentGroupId: "grp-platform",
      position: { x: 280, y: 450 },
      style: { variant: "outlined", highlight: false },
      metadata: { description: "Monitoring", tags: ["platform"] }
    },
    {
      id: "node-appinsights",
      type: "azure-app-insights",
      label: "App Insights",
      sublabel: null,
      parentGroupId: "grp-platform",
      position: { x: 380, y: 450 },
      style: { variant: "outlined", highlight: false },
      metadata: { description: "Telemetry", tags: ["platform"] }
    },
    // Security
    {
      id: "node-entra",
      type: "azure-entra-id",
      label: "Entra ID",
      sublabel: null,
      parentGroupId: "grp-security",
      position: { x: 640, y: 450 },
      style: { variant: "default", highlight: false },
      metadata: { description: "Identity", tags: ["security"] }
    },
    {
      id: "node-defender",
      type: "azure-defender",
      label: "Defender",
      sublabel: null,
      parentGroupId: "grp-security",
      position: { x: 740, y: 450 },
      style: { variant: "default", highlight: false },
      metadata: { description: "Security", tags: ["security"] }
    }
  ],
  edges: [
    {
      id: "e1",
      source: "node-user",
      target: "node-apim",
      label: null,
      type: "solid",
      animated: false,
      arrowDirection: "forward",
      style: { strokeColor: "#333333", strokeWidth: 1.5 }
    },
    {
      id: "e2",
      source: "node-teams",
      target: "node-apim",
      label: null,
      type: "solid",
      animated: false,
      arrowDirection: "forward",
      style: { strokeColor: "#333333", strokeWidth: 1.5 }
    },
    {
      id: "e3",
      source: "node-apim",
      target: "node-container",
      label: null,
      type: "solid",
      animated: false,
      arrowDirection: "forward",
      style: { strokeColor: "#333333", strokeWidth: 1.5 }
    },
    {
      id: "e4",
      source: "node-container",
      target: "node-openai",
      label: null,
      type: "solid",
      animated: false,
      arrowDirection: "forward",
      style: { strokeColor: "#333333", strokeWidth: 1.5 }
    },
    {
      id: "e5",
      source: "node-container",
      target: "node-sql",
      label: null,
      type: "solid",
      animated: false,
      arrowDirection: "forward",
      style: { strokeColor: "#333333", strokeWidth: 1.5 }
    },
    {
      id: "e6",
      source: "node-container",
      target: "node-servicebus",
      label: null,
      type: "solid",
      animated: false,
      arrowDirection: "forward",
      style: { strokeColor: "#888888", strokeWidth: 1 }
    },
    {
      id: "e7",
      source: "node-functions",
      target: "node-blob",
      label: null,
      type: "solid",
      animated: false,
      arrowDirection: "forward",
      style: { strokeColor: "#888888", strokeWidth: 1 }
    }
  ]
};

/**
 * MCP Agent Architecture Template
 * For AI Agent / MCP-based systems
 */
export const mcpAgentArchitecture: EnterpriseArchitectureSchema = {
  title: "MCP Agent Architecture",
  legend: [
    { symbol: "solid-line", color: "#333333", label: "Current Scope" },
    { symbol: "dashed-line", color: "#888888", label: "Future Extension" }
  ],
  groups: [
    {
      id: "grp-boundary",
      label: "Azure Cloud",
      parentId: null,
      style: {
        backgroundColor: "#FFF9E6AA",
        borderStyle: "solid",
        borderColor: "#C8A800",
        borderWidth: 2,
        borderRadius: 12,
        labelColor: "#C8A800"
      },
      position: { x: 20, y: 20 },
      size: { width: 1000, height: 500 }
    },
    {
      id: "grp-container",
      label: "Azure Container App",
      parentId: "grp-boundary",
      style: {
        backgroundColor: "#E8F4FDAA",
        borderStyle: "solid",
        borderColor: "#1E6AA5",
        borderWidth: 1,
        borderRadius: 8,
        labelColor: "#1E6AA5"
      },
      position: { x: 300, y: 80 },
      size: { width: 400, height: 300 }
    },
    {
      id: "grp-mcp",
      label: "MCP Client-Server Layer",
      parentId: "grp-container",
      style: {
        backgroundColor: "#EEF0FAAA",
        borderStyle: "solid",
        borderColor: "#5C6BC0",
        borderWidth: 1,
        borderRadius: 8,
        labelColor: "#5C6BC0"
      },
      position: { x: 320, y: 140 },
      size: { width: 360, height: 200 }
    }
  ],
  nodes: [
    {
      id: "node-user",
      type: "user",
      label: "User",
      sublabel: null,
      parentGroupId: null,
      position: { x: 60, y: 200 },
      style: { variant: "default", highlight: false },
      metadata: { description: null, tags: [] }
    },
    {
      id: "node-teams",
      type: "ms-teams",
      label: "MS Teams",
      sublabel: null,
      parentGroupId: null,
      position: { x: 160, y: 200 },
      style: { variant: "default", highlight: false },
      metadata: { description: null, tags: [] }
    },
    {
      id: "node-orchestrator",
      type: "agent-orchestrator",
      label: "Orchestrator Agent",
      sublabel: "MCP Client",
      parentGroupId: "grp-mcp",
      position: { x: 380, y: 200 },
      style: { variant: "outlined", highlight: true },
      metadata: { description: "Intent identification, workflow planning", tags: ["agent", "mcp-client"] }
    },
    {
      id: "node-mcp-server",
      type: "mcp-server",
      label: "MCP Server",
      sublabel: "Tool Collection",
      parentGroupId: "grp-mcp",
      position: { x: 540, y: 200 },
      style: { variant: "default", highlight: false },
      metadata: { description: null, tags: ["mcp"] }
    },
    {
      id: "node-openai",
      type: "azure-openai",
      label: "Azure OpenAI",
      sublabel: null,
      parentGroupId: null,
      position: { x: 800, y: 120 },
      style: { variant: "default", highlight: false },
      metadata: { description: null, tags: ["ai"] }
    },
    {
      id: "node-sql",
      type: "azure-sql-database",
      label: "Azure SQL",
      sublabel: null,
      parentGroupId: null,
      position: { x: 800, y: 240 },
      style: { variant: "default", highlight: false },
      metadata: { description: null, tags: ["data"] }
    },
    {
      id: "node-sharepoint",
      type: "sharepoint",
      label: "SharePoint",
      sublabel: null,
      parentGroupId: null,
      position: { x: 800, y: 360 },
      style: { variant: "default", highlight: false },
      metadata: { description: null, tags: ["data"] }
    },
    {
      id: "node-keyvault",
      type: "azure-key-vault",
      label: "Key Vault",
      sublabel: null,
      parentGroupId: null,
      position: { x: 540, y: 440 },
      style: { variant: "default", highlight: false },
      metadata: { description: null, tags: ["security"] }
    }
  ],
  edges: [
    {
      id: "e1",
      source: "node-user",
      target: "node-teams",
      label: null,
      type: "solid",
      animated: true,
      arrowDirection: "forward",
      style: { strokeColor: "#333333", strokeWidth: 2 }
    },
    {
      id: "e2",
      source: "node-teams",
      target: "node-orchestrator",
      label: "REST",
      type: "solid",
      animated: true,
      arrowDirection: "forward",
      style: { strokeColor: "#333333", strokeWidth: 2 }
    },
    {
      id: "e3",
      source: "node-orchestrator",
      target: "node-mcp-server",
      label: "Invoke",
      type: "solid",
      animated: false,
      arrowDirection: "forward",
      style: { strokeColor: "#333333", strokeWidth: 1.5 }
    },
    {
      id: "e4",
      source: "node-orchestrator",
      target: "node-openai",
      label: "Invoke",
      type: "solid",
      animated: false,
      arrowDirection: "forward",
      style: { strokeColor: "#333333", strokeWidth: 1.5 }
    },
    {
      id: "e5",
      source: "node-mcp-server",
      target: "node-sql",
      label: "Query",
      type: "solid",
      animated: false,
      arrowDirection: "forward",
      style: { strokeColor: "#333333", strokeWidth: 1.5 }
    },
    {
      id: "e6",
      source: "node-mcp-server",
      target: "node-sharepoint",
      label: "Fetch",
      type: "solid",
      animated: false,
      arrowDirection: "forward",
      style: { strokeColor: "#333333", strokeWidth: 1.5 }
    },
    {
      id: "e7",
      source: "node-orchestrator",
      target: "node-keyvault",
      label: "Secret",
      type: "solid",
      animated: false,
      arrowDirection: "forward",
      style: { strokeColor: "#888888", strokeWidth: 1 }
    }
  ]
};

/**
 * Get all available architecture templates
 */
export function getArchitectureTemplates(): Record<string, EnterpriseArchitectureSchema> {
  return {
    'optistudio': optiStudioArchitecture,
    'mcp-agent': mcpAgentArchitecture,
  };
}
