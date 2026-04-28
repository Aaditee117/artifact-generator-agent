/**
 * Layout Engine for Architecture Diagrams
 * Uses dagre for automatic left-to-right hierarchical layout
 * Supports both legacy and enterprise architecture schemas
 */

import dagre from 'dagre';
import type { Node, Edge } from '@xyflow/react';
import { getGroupColor } from './iconMapping';
import type { EnterpriseArchitectureSchema, EnterpriseGroup } from './enterpriseArchitectureSchema';

export interface ArchitectureGroup {
  id: string;
  label: string;
  color?: string;
  position?: { x: number; y: number };
  width?: number;
  height?: number;
}

export interface ArchitectureNode {
  id: string;
  label: string;
  technology: string;
  tooltip: string;
  group: string;
  icon: string;
  position?: { x: number; y: number };
  type?: string;
  // Parent/child container support
  azureType?: string;
  nodeType?: 'container' | 'service' | 'brain' | 'future' | 'decoration';
  parentNode?: string | null;
  isFuture?: boolean;
  width?: number;
  height?: number;
  containerStyle?: {
    backgroundColor?: string;
    borderColor?: string;
    borderStyle?: 'solid' | 'dashed';
  };
}

export interface ArchitectureEdge {
  source: string;
  target: string;
  label: string;
  protocol: string;
  isFuture?: boolean;
}

export interface ArchitectureGraph {
  groups: ArchitectureGroup[];
  nodes: ArchitectureNode[];
  edges: ArchitectureEdge[];
}

// Node dimensions
const NODE_WIDTH = 160;
const NODE_HEIGHT = 80;
const GROUP_PADDING = 40;

/**
 * Apply layout to nodes and edges
 * Detects parent/child container layout from LLM, falls back to dagre
 */
export function applyDagreLayout(
  graph: ArchitectureGraph
): { nodes: Node[]; edges: Edge[]; groupNodes: Node[] } {

  // Detect new container-based layout: any node has nodeType === 'container'
  const hasContainers = graph.nodes.some(n => n.nodeType === 'container');

  if (hasContainers) {
    return applyContainerLayout(graph);
  }

  // Check if nodes have positions from LLM
  const hasLLMPositions = graph.nodes.some(n => n.position?.x !== undefined);

  if (hasLLMPositions) {
    return applyLLMLayout(graph);
  }

  // Fall back to dagre layout
  return applyDagreAutoLayout(graph);
}

/**
 * Use positions provided by LLM
 */
function applyLLMLayout(
  graph: ArchitectureGraph
): { nodes: Node[]; edges: Edge[]; groupNodes: Node[] } {

  // Convert to React Flow nodes using LLM positions
  const nodes: Node[] = graph.nodes.map((node) => ({
    id: node.id,
    type: 'architectureNode',
    position: {
      x: node.position?.x ?? 100,
      y: node.position?.y ?? 100,
    },
    data: {
      label: node.label,
      technology: node.technology,
      tooltip: node.tooltip,
      group: node.group,
      icon: node.icon,
    },
    draggable: true,
  }));

  // Convert to React Flow edges
  const edges: Edge[] = graph.edges.map((edge, index) => ({
    id: `edge-${index}`,
    source: edge.source,
    target: edge.target,
    label: edge.label,
    type: 'smoothstep',
    animated: false,
    style: { stroke: '#424242', strokeWidth: 1.5 },
    labelStyle: { fontSize: 10, fill: '#666' },
    labelBgStyle: { fill: 'white', fillOpacity: 0.8 },
  }));

  // Create group nodes (layer containers) using LLM positions
  const groupNodes: Node[] = graph.groups.map((group) => ({
    id: `group-${group.id}`,
    type: 'group',
    position: {
      x: group.position?.x ?? 0,
      y: group.position?.y ?? 0,
    },
    data: {
      label: group.label,
    },
    style: {
      width: group.width ?? 220,
      height: group.height ?? 500,
      backgroundColor: group.color ?? '#F3F6FC',
      border: '1px dashed #ccc',
      borderRadius: 8,
      padding: 10,
      zIndex: -1,
    },
    draggable: false,
    selectable: false,
  }));

  return { nodes, edges, groupNodes };
}

/**
 * Layout with parent/child container nesting (React Flow sub-flows).
 * Handles decoration nodes, container zIndex, and overlap prevention.
 */
function applyContainerLayout(
  graph: ArchitectureGraph
): { nodes: Node[]; edges: Edge[]; groupNodes: Node[] } {

  // Constants for overlap prevention
  const MIN_V_GAP = 100;  // min vertical gap between siblings
  const NODE_H = 80;       // approximate rendered node height
  const CONTAINER_PADDING = 50; // padding inside containers

  // Separate by type
  const containers = graph.nodes.filter(n => n.nodeType === 'container');
  const decorations = graph.nodes.filter(n => n.nodeType === 'decoration');
  const services = graph.nodes.filter(
    n => n.nodeType !== 'container' && n.nodeType !== 'decoration'
  );

  const containerIds = new Set(containers.map(c => c.id));

  // Sort containers: parents before children (by nesting depth)
  const sortedContainers = [...containers].sort((a, b) => {
    return getParentDepth(a, graph.nodes) - getParentDepth(b, graph.nodes);
  });

  // --- Dynamic container sizing ---
  // For each container, count its children and auto-expand height if needed
  const childCountMap = new Map<string, ArchitectureNode[]>();
  for (const svc of services) {
    if (svc.parentNode && containerIds.has(svc.parentNode)) {
      if (!childCountMap.has(svc.parentNode)) {
        childCountMap.set(svc.parentNode, []);
      }
      childCountMap.get(svc.parentNode)!.push(svc);
    }
  }

  // --- Clamp children inside container bounds (relative positions) ---
  for (const [containerId, children] of childCountMap) {
    const container = containers.find(c => c.id === containerId);
    if (!container) continue;
    const cw = container.width || 300;
    const ch = container.height || 200;
    for (const child of children) {
      const cx = child.position?.x ?? CONTAINER_PADDING;
      const cy = child.position?.y ?? CONTAINER_PADDING;
      child.position = {
        x: Math.max(10, Math.min(cx, cw - 140)),
        y: Math.max(30, Math.min(cy, ch - NODE_H - 10)),
      };
    }
  }

  // Build container (groupNodes) array
  const groupNodes: Node[] = sortedContainers.map((node) => {
    const children = childCountMap.get(node.id) || [];
    // Also count nested containers as children for sizing
    const nestedContainers = containers.filter(c => c.parentNode === node.id);

    // Dynamic height: ensure container fits all children
    let height = node.height || 200;
    if (children.length > 0) {
      const maxChildY = Math.max(...children.map(c => (c.position?.y ?? 0) + NODE_H));
      const neededHeight = maxChildY + CONTAINER_PADDING;
      height = Math.max(height, neededHeight);
    }
    if (nestedContainers.length > 0) {
      const maxNestedY = Math.max(...nestedContainers.map(c => (c.position?.y ?? 0) + (c.height || 200)));
      height = Math.max(height, maxNestedY + CONTAINER_PADDING);
    }

    // Dynamic width: ensure container fits all children
    let width = node.width || 300;
    if (children.length > 0) {
      const maxChildX = Math.max(...children.map(c => (c.position?.x ?? 0) + 140));
      width = Math.max(width, maxChildX + CONTAINER_PADDING);
    }
    if (nestedContainers.length > 0) {
      const maxNestedX = Math.max(...nestedContainers.map(c => (c.position?.x ?? 0) + (c.width || 300)));
      width = Math.max(width, maxNestedX + CONTAINER_PADDING);
    }

    const base: Node = {
      id: node.id,
      type: 'containerNode',
      position: { x: node.position?.x ?? 0, y: node.position?.y ?? 0 },
      data: {
        label: node.label,
        containerStyle: node.containerStyle,
        isFuture: node.isFuture,
      },
      style: {
        width,
        height,
        zIndex: -1,
      },
      draggable: false,
      selectable: false,
    };
    if (node.parentNode && containerIds.has(node.parentNode)) {
      (base as Record<string, unknown>).parentId = node.parentNode;
      (base as Record<string, unknown>).extent = 'parent';
      (base as Record<string, unknown>).expandParent = true;
    }
    return base;
  });

  // --- Overlap prevention for service nodes within the same container ---
  // Group services by parentNode (or '' for top-level)
  const siblingGroups = new Map<string, ArchitectureNode[]>();
  for (const svc of services) {
    const key = svc.parentNode || '';
    if (!siblingGroups.has(key)) siblingGroups.set(key, []);
    siblingGroups.get(key)!.push(svc);
  }
  // For each group, sort by y then enforce minimum vertical gap
  for (const [, siblings] of siblingGroups) {
    siblings.sort((a, b) => (a.position?.y ?? 0) - (b.position?.y ?? 0));
    for (let i = 1; i < siblings.length; i++) {
      const prev = siblings[i - 1];
      const curr = siblings[i];
      const prevY = prev.position?.y ?? 0;
      const currY = curr.position?.y ?? 0;
      // Only if same x-column (within 30px), push down to avoid overlap
      const sameCol = Math.abs((prev.position?.x ?? 0) - (curr.position?.x ?? 0)) < 30;
      if (sameCol && currY < prevY + NODE_H + MIN_V_GAP) {
        curr.position = { x: curr.position?.x ?? 0, y: prevY + NODE_H + MIN_V_GAP };
      }
    }
  }

  // Build decoration nodes array (Azure logo — no handles, not draggable)
  const decorationNodes: Node[] = decorations.map((node) => ({
    id: node.id,
    type: 'decorationNode',
    position: { x: node.position?.x ?? 20, y: node.position?.y ?? 20 },
    data: {
      label: node.label,
      azureType: node.azureType || 'azure',
    },
    draggable: false,
    selectable: false,
    connectable: false,
  }));

  // Build service nodes array
  const serviceNodes: Node[] = services.map((node) => {
    const base: Node = {
      id: node.id,
      type: 'architectureNode',
      position: { x: node.position?.x ?? 0, y: node.position?.y ?? 0 },
      data: {
        label: node.label,
        technology: node.technology || '',
        tooltip: node.tooltip || '',
        group: node.group || '',
        icon: node.azureType || node.icon || 'app-service',
        azureType: node.azureType || node.icon,
        nodeType: node.nodeType,
        isFuture: node.isFuture,
      },
      draggable: true,
      style: { zIndex: 10 },
    };
    if (node.parentNode && containerIds.has(node.parentNode)) {
      (base as Record<string, unknown>).parentId = node.parentNode;
      (base as Record<string, unknown>).extent = 'parent';
      (base as Record<string, unknown>).expandParent = true;
    }
    return base;
  });

  // Merge decoration + service nodes
  const nodes: Node[] = [...decorationNodes, ...serviceNodes];

  // Build edges — exclude decoration nodes from edges
  const decorationIds = new Set(decorations.map(d => d.id));
  const edges: Edge[] = graph.edges
    .filter(e => !decorationIds.has(e.source) && !decorationIds.has(e.target))
    .map((edge, index) => {
      const isFuture = edge.isFuture || false;
      return {
        id: `edge-${index}`,
        source: edge.source,
        target: edge.target,
        label: edge.label || undefined,
        type: 'smoothstep',
        animated: false,
        style: {
          stroke: isFuture ? '#E53935' : '#424242',
          strokeWidth: 1.5,
          ...(isFuture ? { strokeDasharray: '5,5' } : {}),
        },
        markerEnd: {
          type: 'arrowclosed' as const,
          color: isFuture ? '#E53935' : '#424242',
        },
        labelStyle: { fontSize: 10, fill: '#666' },
        labelBgStyle: { fill: 'white', fillOpacity: 0.8 },
      };
    });

  return { nodes, edges, groupNodes };
}

/** Calculate nesting depth of a node (0 = top-level, 1 = one parent, etc.) */
function getParentDepth(node: ArchitectureNode, allNodes: ArchitectureNode[]): number {
  let depth = 0;
  let current = node;
  while (current.parentNode) {
    depth++;
    const parent = allNodes.find(n => n.id === current.parentNode);
    if (!parent) break;
    current = parent;
  }
  return depth;
}

/**
 * Fall back to dagre auto-layout
 */
function applyDagreAutoLayout(
  graph: ArchitectureGraph
): { nodes: Node[]; edges: Edge[]; groupNodes: Node[] } {
  const dagreGraph = new dagre.graphlib.Graph();
  
  // Set graph direction (LR = left to right)
  dagreGraph.setGraph({
    rankdir: 'LR',
    nodesep: 60,
    ranksep: 120,
    marginx: 40,
    marginy: 40,
  });
  
  dagreGraph.setDefaultEdgeLabel(() => ({}));

  // Group nodes by their tier/group
  const groupedNodes = new Map<string, ArchitectureNode[]>();
  graph.nodes.forEach((node) => {
    const group = node.group || 'default';
    if (!groupedNodes.has(group)) {
      groupedNodes.set(group, []);
    }
    groupedNodes.get(group)!.push(node);
  });

  // Add nodes to dagre graph
  graph.nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: NODE_WIDTH, height: NODE_HEIGHT });
  });

  // Add edges to dagre graph
  graph.edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  // Run dagre layout
  dagre.layout(dagreGraph);

  // Convert to React Flow nodes
  const nodes: Node[] = graph.nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    return {
      id: node.id,
      type: 'architectureNode',
      position: {
        x: nodeWithPosition.x - NODE_WIDTH / 2,
        y: nodeWithPosition.y - NODE_HEIGHT / 2,
      },
      data: {
        label: node.label,
        technology: node.technology,
        tooltip: node.tooltip,
        group: node.group,
        icon: node.icon,
      },
      draggable: true,
    };
  });

  // Convert to React Flow edges
  const edges: Edge[] = graph.edges.map((edge, index) => ({
    id: `edge-${index}`,
    source: edge.source,
    target: edge.target,
    label: edge.label,
    type: 'smoothstep',
    animated: false,
    style: { stroke: '#424242', strokeWidth: 1.5 },
    labelStyle: { fontSize: 10, fill: '#666' },
    labelBgStyle: { fill: 'white', fillOpacity: 0.8 },
  }));

  // Calculate group boundaries
  const groupNodes = calculateGroupBoundaries(nodes, graph.groups, groupedNodes);

  return { nodes, edges, groupNodes };
}

/**
 * Calculate group boundaries based on node positions
 */
function calculateGroupBoundaries(
  nodes: Node[],
  groups: ArchitectureGroup[],
  groupedNodes: Map<string, ArchitectureNode[]>
): Node[] {
  const groupNodesList: Node[] = [];

  groups.forEach((group) => {
    const nodesInGroup = groupedNodes.get(group.id) || [];
    if (nodesInGroup.length === 0) return;

    // Find min/max positions of nodes in this group
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;

    nodesInGroup.forEach((archNode) => {
      const flowNode = nodes.find((n) => n.id === archNode.id);
      if (flowNode) {
        minX = Math.min(minX, flowNode.position.x);
        minY = Math.min(minY, flowNode.position.y);
        maxX = Math.max(maxX, flowNode.position.x + NODE_WIDTH);
        maxY = Math.max(maxY, flowNode.position.y + NODE_HEIGHT);
      }
    });

    // Add padding around group
    const groupNode: Node = {
      id: `group-${group.id}`,
      type: 'group',
      position: {
        x: minX - GROUP_PADDING,
        y: minY - GROUP_PADDING - 30, // Extra space for label
      },
      data: {
        label: group.label,
      },
      style: {
        width: maxX - minX + GROUP_PADDING * 2,
        height: maxY - minY + GROUP_PADDING * 2 + 30,
        backgroundColor: group.color || getGroupColor(group.label),
        border: '1px dashed #ccc',
        borderRadius: 8,
        padding: 10,
        zIndex: -1,
      },
      draggable: false,
      selectable: false,
    };

    groupNodesList.push(groupNode);
  });

  return groupNodesList;
}

/**
 * Simple tier-based layout (alternative to dagre)
 * Arranges nodes in columns based on their tier/group
 */
export function applyTierLayout(graph: ArchitectureGraph): { nodes: Node[]; edges: Edge[] } {
  // Define tier order (left to right)
  const tierOrder = [
    'User',
    'Frontend',
    'Backend',
    'AI Services',
    'Data Layer',
    'Messaging',
    'Security',
    'Monitoring',
    'External',
  ];

  // Group nodes by tier
  const tiers = new Map<string, ArchitectureNode[]>();
  graph.nodes.forEach((node) => {
    const tier = node.group || 'Backend';
    if (!tiers.has(tier)) {
      tiers.set(tier, []);
    }
    tiers.get(tier)!.push(node);
  });

  // Calculate positions
  const TIER_WIDTH = 220;
  const NODE_SPACING = 100;
  const START_X = 50;
  const START_Y = 100;

  const nodes: Node[] = [];
  let tierIndex = 0;

  tierOrder.forEach((tierName) => {
    const tierNodes = tiers.get(tierName);
    if (!tierNodes || tierNodes.length === 0) return;

    const x = START_X + tierIndex * TIER_WIDTH;

    tierNodes.forEach((node, nodeIndex) => {
      const y = START_Y + nodeIndex * NODE_SPACING;
      nodes.push({
        id: node.id,
        type: 'architectureNode',
        position: { x, y },
        data: {
          label: node.label,
          technology: node.technology,
          tooltip: node.tooltip,
          group: node.group,
          icon: node.icon,
        },
        draggable: true,
      });
    });

    tierIndex++;
  });

  // Convert edges
  const edges: Edge[] = graph.edges.map((edge, index) => ({
    id: `edge-${index}`,
    source: edge.source,
    target: edge.target,
    label: edge.label,
    type: 'smoothstep',
    animated: false,
    style: { stroke: '#424242', strokeWidth: 1.5 },
    labelStyle: { fontSize: 10, fill: '#666' },
  }));

  return { nodes, edges };
}

// ============================================
// Enterprise Architecture Layout Functions
// ============================================

/**
 * Apply enterprise schema layout with nested groups and custom styling
 */
export function applyEnterpriseLayout(
  schema: EnterpriseArchitectureSchema
): { nodes: Node[]; edges: Edge[]; groupNodes: Node[] } {

  // Sort groups by hierarchy (parent groups first)
  const sortedGroups = sortGroupsByHierarchy(schema.groups);

  // Create group nodes with proper styling
  const groupNodes: Node[] = sortedGroups.map((group) => ({
    id: group.id,
    type: 'group',
    position: group.position,
    data: {
      label: group.label,
    },
    style: {
      width: group.size.width,
      height: group.size.height,
      backgroundColor: group.style.backgroundColor,
      border: `${group.style.borderWidth}px ${group.style.borderStyle} ${group.style.borderColor}`,
      borderRadius: group.style.borderRadius,
      padding: 10,
      zIndex: group.parentId ? -1 : -2, // Parent groups behind child groups
    },
    draggable: false,
    selectable: false,
    // Add label styling
    className: 'enterprise-group',
  }));

  // Create architecture nodes
  const nodes: Node[] = schema.nodes.map((node) => ({
    id: node.id,
    type: 'architectureNode',
    position: node.position,
    data: {
      label: node.label,
      technology: node.sublabel || '',
      tooltip: node.metadata.description || '',
      group: node.parentGroupId || '',
      icon: mapEnterpriseTypeToIcon(node.type),
      highlight: node.style.highlight,
      variant: node.style.variant,
    },
    draggable: true,
  }));

  // Create edges with enterprise styling
  const edges: Edge[] = schema.edges.map((edge) => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
    label: edge.label || undefined,
    type: 'smoothstep',
    animated: edge.animated,
    style: {
      stroke: edge.style.strokeColor,
      strokeWidth: edge.style.strokeWidth,
      strokeDasharray: edge.type === 'dashed' ? '5,5' : undefined,
    },
    labelStyle: { fontSize: 10, fill: '#666' },
    labelBgStyle: { fill: 'white', fillOpacity: 0.8 },
    markerEnd: edge.arrowDirection !== 'backward' ? {
      type: 'arrowclosed' as const,
      color: edge.style.strokeColor,
    } : undefined,
    markerStart: edge.arrowDirection === 'backward' || edge.arrowDirection === 'bidirectional' ? {
      type: 'arrowclosed' as const,
      color: edge.style.strokeColor,
    } : undefined,
  }));

  return { nodes, edges, groupNodes };
}

/**
 * Sort groups by hierarchy - parent groups come before child groups
 */
function sortGroupsByHierarchy(groups: EnterpriseGroup[]): EnterpriseGroup[] {
  const sorted: EnterpriseGroup[] = [];
  const remaining = [...groups];

  // First pass: add root groups (no parent)
  const rootGroups = remaining.filter(g => !g.parentId);
  sorted.push(...rootGroups);

  // Remove root groups from remaining
  rootGroups.forEach(rg => {
    const idx = remaining.findIndex(g => g.id === rg.id);
    if (idx !== -1) remaining.splice(idx, 1);
  });

  // Add remaining groups (child groups)
  sorted.push(...remaining);

  return sorted;
}

/**
 * Map enterprise node type to icon name
 */
function mapEnterpriseTypeToIcon(type: string): string {
  // Handle azure- prefix
  if (type.startsWith('azure-')) {
    return type.replace('azure-', '');
  }

  // Map common types
  const typeMap: Record<string, string> = {
    'user': 'user',
    'ms-teams': 'ms-teams',
    'sharepoint': 'sharepoint',
    'microsoft-fabric': 'microsoft-fabric',
    'power-bi': 'power-bi',
    'mcp-client': 'mcp-client',
    'mcp-server': 'mcp-server',
    'mcp-tool': 'mcp-tool',
    'agent-orchestrator': 'agent-orchestrator',
    'generic-tool': 'generic-tool',
    'web-app': 'app-service',
  };

  return typeMap[type] || type;
}

/**
 * Create a simple enterprise diagram from minimal input
 */
export function createEnterpriseGraph(
  title: string,
  nodes: Array<{ id: string; type: string; label: string; group?: string; x: number; y: number }>,
  edges: Array<{ source: string; target: string; label?: string }>,
  groups: Array<{ id: string; label: string; x: number; y: number; width: number; height: number; color?: string }>
): EnterpriseArchitectureSchema {
  return {
    title,
    legend: [
      { symbol: 'solid-line', color: '#333333', label: 'Data Flow' },
    ],
    groups: groups.map(g => ({
      id: g.id,
      label: g.label,
      parentId: null,
      style: {
        backgroundColor: g.color || '#E8F4FDAA',
        borderStyle: 'solid' as const,
        borderColor: '#1E6AA5',
        borderWidth: 1 as const,
        borderRadius: 8,
        labelColor: '#1E6AA5',
      },
      position: { x: g.x, y: g.y },
      size: { width: g.width, height: g.height },
    })),
    nodes: nodes.map(n => ({
      id: n.id,
      type: n.type,
      label: n.label,
      sublabel: null,
      parentGroupId: n.group || null,
      position: { x: n.x, y: n.y },
      style: { variant: 'default' as const, highlight: false },
      metadata: { description: null, tags: [] },
    })),
    edges: edges.map((e, i) => ({
      id: `e${i}`,
      source: e.source,
      target: e.target,
      label: e.label || null,
      type: 'solid' as const,
      animated: false,
      arrowDirection: 'forward' as const,
      style: { strokeColor: '#333333', strokeWidth: 1.5 as const },
    })),
  };
}
