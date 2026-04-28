/**
 * Enterprise Architecture Diagram Schema
 * 
 * Defines the schema for enterprise-grade Azure architecture diagrams
 * with support for nested groups, custom styling, and edge types.
 */

// ============================================
// Legend & Metadata Types
// ============================================

export interface LegendItem {
  symbol: 'solid-line' | 'dashed-line' | 'filled-box' | 'outlined-box';
  color: string;
  label: string;
}

// ============================================
// Group (Container/Section) Types
// ============================================

export interface GroupStyle {
  backgroundColor: string;
  borderStyle: 'solid' | 'dashed';
  borderColor: string;
  borderWidth: 1 | 2;
  borderRadius: number;
  labelColor: string;
}

export interface EnterpriseGroup {
  id: string;
  label: string;
  parentId: string | null;
  style: GroupStyle;
  position: { x: number; y: number };
  size: { width: number; height: number };
}

// ============================================
// Node Types
// ============================================

export type AzureServiceType =
  // Compute
  | 'azure-container-apps'
  | 'azure-app-service'
  | 'azure-functions'
  | 'azure-kubernetes-service'
  | 'azure-virtual-machines'
  | 'azure-batch'
  // Integration & API
  | 'azure-api-management'
  | 'azure-logic-apps'
  | 'azure-service-bus'
  | 'azure-event-grid'
  | 'azure-event-hubs'
  | 'azure-data-factory'
  // AI & ML
  | 'azure-openai'
  | 'azure-ai-search'
  | 'azure-machine-learning'
  | 'azure-cognitive-services'
  | 'azure-bot-service'
  | 'azure-ai-foundry'
  | 'azure-foundry-models'
  // Data & Storage
  | 'azure-cosmos-db'
  | 'azure-sql-database'
  | 'azure-storage-account'
  | 'azure-blob-storage'
  | 'azure-data-lake'
  | 'azure-synapse-analytics'
  | 'azure-redis-cache'
  | 'azure-databricks'
  // Networking
  | 'azure-virtual-network'
  | 'azure-api-gateway'
  | 'azure-application-gateway'
  | 'azure-cdn'
  | 'azure-private-endpoint'
  | 'azure-load-balancer'
  | 'azure-front-door'
  // Security & Identity
  | 'azure-entra-id'
  | 'azure-key-vault'
  | 'azure-defender'
  | 'azure-sentinel'
  // Monitoring & DevOps
  | 'azure-monitor'
  | 'azure-app-insights'
  | 'azure-log-analytics'
  | 'azure-devops'
  // Microsoft 365 / External
  | 'ms-teams'
  | 'sharepoint'
  | 'microsoft-fabric'
  | 'power-bi'
  // Protocol / Tool Nodes
  | 'mcp-client'
  | 'mcp-server'
  | 'mcp-tool'
  | 'agent-orchestrator'
  | 'user'
  | 'generic-tool'
  | 'web-app';

export interface NodeStyle {
  variant: 'default' | 'outlined' | 'filled';
  highlight: boolean;
}

export interface NodeMetadata {
  description: string | null;
  tags: string[];
}

export interface EnterpriseNode {
  id: string;
  type: AzureServiceType | string;
  label: string;
  sublabel: string | null;
  parentGroupId: string | null;
  position: { x: number; y: number };
  style: NodeStyle;
  metadata: NodeMetadata;
}

// ============================================
// Edge Types
// ============================================

export interface EdgeStyle {
  strokeColor: string;
  strokeWidth: 1 | 1.5 | 2;
}

export interface EnterpriseEdge {
  id: string;
  source: string;
  target: string;
  label: string | null;
  type: 'solid' | 'dashed';
  animated: boolean;
  arrowDirection: 'forward' | 'backward' | 'bidirectional';
  style: EdgeStyle;
}

// ============================================
// Complete Architecture Schema
// ============================================

export interface EnterpriseArchitectureSchema {
  title: string;
  legend: LegendItem[];
  groups: EnterpriseGroup[];
  nodes: EnterpriseNode[];
  edges: EnterpriseEdge[];
}

// ============================================
// Conversion Helpers
// ============================================

/**
 * Convert enterprise schema to legacy ArchitectureGraph format
 * for backward compatibility with existing components
 */
export function convertToLegacyGraph(schema: EnterpriseArchitectureSchema) {
  return {
    groups: schema.groups.map(g => ({
      id: g.id,
      label: g.label,
      color: g.style.backgroundColor,
      position: g.position,
      width: g.size.width,
      height: g.size.height,
    })),
    nodes: schema.nodes.map(n => ({
      id: n.id,
      label: n.label,
      technology: n.sublabel || '',
      tooltip: n.metadata.description || '',
      group: n.parentGroupId || '',
      icon: n.type,
      position: n.position,
    })),
    edges: schema.edges.map(e => ({
      source: e.source,
      target: e.target,
      label: e.label || '',
      protocol: '',
    })),
  };
}

// ============================================
// Default Group Color Palette
// ============================================

export const enterpriseGroupColors = {
  // Azure boundary
  systemBoundary: { bg: '#FAFBFCAA', border: '#0078D4' },
  // Functional layers
  external: { bg: '#F5F5F5AA', border: '#666666' },
  gateway: { bg: '#E8F4FDAA', border: '#1E6AA5' },
  compute: { bg: '#E8F5E9AA', border: '#2E7D32' },
  ai: { bg: '#FFF3E0AA', border: '#E65100' },
  data: { bg: '#F3E5F5AA', border: '#7B1FA2' },
  messaging: { bg: '#E0F7FAAA', border: '#00838F' },
  platform: { bg: '#ECEFF1AA', border: '#455A64' },
  security: { bg: '#FCE4ECAA', border: '#C62828' },
  mcp: { bg: '#EEF0FAAA', border: '#5C6BC0' },
};
