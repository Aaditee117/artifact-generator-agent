/**
 * Architecture Diagram Component
 * Interactive React Flow diagram with export capabilities
 */

import React, { useCallback, useState, useRef, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  BackgroundVariant,
  Panel,
} from '@xyflow/react';
import type { Node, Connection } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import {
  Box,
  Button,
  Typography,
  Paper,
  Tooltip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import ImageIcon from '@mui/icons-material/Image';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import RefreshIcon from '@mui/icons-material/Refresh';
import { toPng, toSvg } from 'html-to-image';

import ArchitectureNode from './ArchitectureNode';
import ContainerNode from './ContainerNode';
import DecorationNode from './DecorationNode';
import { applyDagreLayout, applyEnterpriseLayout } from '../utils/layoutEngine';
import type { ArchitectureGraph } from '../utils/layoutEngine';
import type { EnterpriseArchitectureSchema } from '../utils/enterpriseArchitectureSchema';
import { iconMapping } from '../utils/iconMapping';

// Register custom node types
const nodeTypes = {
  architectureNode: ArchitectureNode,
  containerNode: ContainerNode,
  decorationNode: DecorationNode,
};

interface ArchitectureDiagramProps {
  graph?: ArchitectureGraph;
  enterpriseSchema?: EnterpriseArchitectureSchema;
  projectName: string;
  onExportPng?: (imageBlob: Blob) => void;
  readOnly?: boolean;
}

const ArchitectureDiagram: React.FC<ArchitectureDiagramProps> = ({
  graph,
  enterpriseSchema,
  projectName,
  onExportPng,
  readOnly = false,
}) => {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [addNodeDialogOpen, setAddNodeDialogOpen] = useState(false);
  const [newNode, setNewNode] = useState({
    label: '',
    technology: '',
    group: '',
    icon: 'app-service',
    tooltip: '',
  });

  // Apply layout to graph data - support both legacy and enterprise schemas
  const layoutResult = useMemo(() => {
    if (enterpriseSchema) {
      return applyEnterpriseLayout(enterpriseSchema);
    }
    if (graph) {
      return applyDagreLayout(graph);
    }
    return { nodes: [], edges: [], groupNodes: [] };
  }, [graph, enterpriseSchema]);

  // Initialize nodes and edges state
  const [nodes, setNodes, onNodesChange] = useNodesState([
    ...layoutResult.groupNodes,
    ...layoutResult.nodes,
  ]);
  const [edges, setEdges, onEdgesChange] = useEdgesState(layoutResult.edges);

  // Handle new edge connections
  const onConnect = useCallback(
    (params: Connection) => {
      if (readOnly) return;
      setEdges((eds) =>
        addEdge(
          {
            ...params,
            type: 'smoothstep',
            style: { stroke: '#424242', strokeWidth: 1.5 },
          },
          eds
        )
      );
    },
    [readOnly, setEdges]
  );

  // Handle label changes
  const handleLabelChange = useCallback(
    (nodeId: string, newLabel: string) => {
      setNodes((nds) =>
        nds.map((node) =>
          node.id === nodeId
            ? { ...node, data: { ...node.data, label: newLabel } }
            : node
        )
      );
    },
    [setNodes]
  );

  // Update nodes with label change handler
  const nodesWithHandlers = useMemo(
    () =>
      nodes.map((node) => ({
        ...node,
        data: {
          ...node.data,
          onLabelChange: handleLabelChange,
        },
      })),
    [nodes, handleLabelChange]
  );

  // Delete selected nodes
  const handleDeleteSelected = useCallback(() => {
    setNodes((nds) => nds.filter((node) => !node.selected));
    setEdges((eds) => {
      const selectedNodeIds = nodes.filter((n) => n.selected).map((n) => n.id);
      return eds.filter(
        (edge) =>
          !selectedNodeIds.includes(edge.source) &&
          !selectedNodeIds.includes(edge.target)
      );
    });
  }, [nodes, setNodes, setEdges]);

  // Add new node
  const handleAddNode = useCallback(() => {
    const newNodeId = `node-${Date.now()}`;
    const newFlowNode: Node = {
      id: newNodeId,
      type: 'architectureNode',
      position: { x: 100, y: 100 },
      data: {
        label: newNode.label,
        technology: newNode.technology,
        tooltip: newNode.tooltip,
        group: newNode.group,
        icon: newNode.icon,
        onLabelChange: handleLabelChange,
      },
      draggable: true,
    };
    setNodes((nds) => [...nds, newFlowNode]);
    setAddNodeDialogOpen(false);
    setNewNode({
      label: '',
      technology: '',
      group: '',
      icon: 'app-service',
      tooltip: '',
    });
  }, [newNode, setNodes, handleLabelChange]);

  // Re-layout nodes
  const handleReLayout = useCallback(() => {
    if (!graph) return;
    const newLayout = applyDagreLayout(graph);
    setNodes([...newLayout.groupNodes, ...newLayout.nodes]);
    setEdges(newLayout.edges);
  }, [graph, setNodes, setEdges]);

  // Track export state
  const [isExporting, setIsExporting] = useState(false);

  // Export as PNG with high quality settings for crisp images
  const handleExportPng = useCallback(async () => {
    if (!reactFlowWrapper.current) return;
    setIsExporting(true);

    try {
      // Wait for any pending renders
      await new Promise(resolve => setTimeout(resolve, 100));

      const dataUrl = await toPng(reactFlowWrapper.current, {
        backgroundColor: '#ffffff',
        quality: 1,
        pixelRatio: 3, // Higher resolution for crisp icons (3x for Retina-quality)
        cacheBust: true, // Ensure fresh render
        style: {
          // Ensure all elements are visible during export
          transform: 'none',
        },
        filter: (node) => {
          // Exclude minimap and controls from export for cleaner output
          const classList = node.classList;
          if (classList) {
            if (classList.contains('react-flow__minimap') ||
                classList.contains('react-flow__controls') ||
                classList.contains('react-flow__panel')) {
              return false;
            }
          }
          return true;
        },
      });

      // Convert data URL to blob
      const response = await fetch(dataUrl);
      const blob = await response.blob();

      if (onExportPng) {
        onExportPng(blob);
      } else {
        // Download locally
        const link = document.createElement('a');
        link.download = `${projectName.replace(/\s+/g, '_')}_architecture.png`;
        link.href = dataUrl;
        link.click();
      }
    } catch (error) {
      console.error('Error exporting PNG:', error);
    } finally {
      setIsExporting(false);
    }
  }, [projectName, onExportPng]);

  // Export as SVG with clean output
  const handleExportSvg = useCallback(async () => {
    if (!reactFlowWrapper.current) return;
    setIsExporting(true);

    try {
      await new Promise(resolve => setTimeout(resolve, 100));

      const dataUrl = await toSvg(reactFlowWrapper.current, {
        backgroundColor: '#ffffff',
        cacheBust: true,
        filter: (node) => {
          const classList = node.classList;
          if (classList) {
            if (classList.contains('react-flow__minimap') ||
                classList.contains('react-flow__controls') ||
                classList.contains('react-flow__panel')) {
              return false;
            }
          }
          return true;
        },
      });

      const link = document.createElement('a');
      link.download = `${projectName.replace(/\s+/g, '_')}_architecture.svg`;
      link.href = dataUrl;
      link.click();
    } catch (error) {
      console.error('Error exporting SVG:', error);
    } finally {
      setIsExporting(false);
    }
  }, [projectName]);

  return (
    <Box sx={{ width: '100%', height: '600px', position: 'relative' }}>
      <Paper
        elevation={2}
        sx={{ width: '100%', height: '100%', overflow: 'hidden', borderRadius: 2 }}
      >
        <div ref={reactFlowWrapper} style={{ width: '100%', height: '100%' }}>
          <ReactFlow
            nodes={nodesWithHandlers}
            edges={edges}
            onNodesChange={readOnly ? undefined : onNodesChange}
            onEdgesChange={readOnly ? undefined : onEdgesChange}
            onConnect={onConnect}
            nodeTypes={nodeTypes}
            fitView
            fitViewOptions={{ padding: 0.2 }}
            minZoom={0.1}
            maxZoom={2}
            defaultEdgeOptions={{
              type: 'smoothstep',
              style: { stroke: '#424242', strokeWidth: 1.5 },
            }}
          >
            <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="#e0e0e0" />
            <Controls />
            <MiniMap
              nodeColor={(node) => {
                if (node.type === 'group') return '#f0f0f0';
                return '#0078D4';
              }}
              maskColor="rgba(0, 0, 0, 0.1)"
            />

            {/* Toolbar Panel */}
            <Panel position="top-right">
              <Paper sx={{ p: 1, display: 'flex', gap: 1, alignItems: 'center' }}>
                <Tooltip title={isExporting ? "Exporting..." : "Export PNG (High Quality)"}>
                  <span>
                    <IconButton 
                      onClick={handleExportPng} 
                      color="primary"
                      disabled={isExporting}
                    >
                      {isExporting ? <CircularProgress size={20} /> : <ImageIcon />}
                    </IconButton>
                  </span>
                </Tooltip>
                <Tooltip title={isExporting ? "Exporting..." : "Export SVG"}>
                  <span>
                    <IconButton 
                      onClick={handleExportSvg} 
                      color="primary"
                      disabled={isExporting}
                    >
                      <DownloadIcon />
                    </IconButton>
                  </span>
                </Tooltip>
                {!readOnly && (
                  <>
                    <Tooltip title="Add Node">
                      <IconButton
                        onClick={() => setAddNodeDialogOpen(true)}
                        color="primary"
                      >
                        <AddIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete Selected">
                      <IconButton onClick={handleDeleteSelected} color="error">
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Re-layout">
                      <IconButton onClick={handleReLayout}>
                        <RefreshIcon />
                      </IconButton>
                    </Tooltip>
                  </>
                )}
              </Paper>
            </Panel>

            {/* Project Name Panel */}
            <Panel position="top-left">
              <Paper sx={{ p: 1.5 }}>
                <Typography variant="subtitle1" fontWeight={600}>
                  {projectName} - Architecture
                </Typography>
              </Paper>
            </Panel>

            {/* Microsoft Azure Logo Panel */}
            <Panel position="bottom-right">
              <Paper sx={{ p: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box
                  component="img"
                  src="https://upload.wikimedia.org/wikipedia/commons/a/a8/Microsoft_Azure_Logo.svg"
                  alt="Microsoft Azure"
                  sx={{ height: 24 }}
                  onError={(e) => {
                    (e.target as HTMLImageElement).style.display = 'none';
                  }}
                />
                <Typography variant="caption" color="textSecondary">
                  Azure Architecture
                </Typography>
              </Paper>
            </Panel>
          </ReactFlow>
        </div>
      </Paper>

      {/* Add Node Dialog */}
      <Dialog open={addNodeDialogOpen} onClose={() => setAddNodeDialogOpen(false)}>
        <DialogTitle>Add New Node</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1, minWidth: 300 }}>
            <TextField
              label="Label"
              value={newNode.label}
              onChange={(e) => setNewNode({ ...newNode, label: e.target.value })}
              fullWidth
            />
            <TextField
              label="Technology"
              value={newNode.technology}
              onChange={(e) => setNewNode({ ...newNode, technology: e.target.value })}
              fullWidth
            />
            <FormControl fullWidth>
              <InputLabel>Group</InputLabel>
              <Select
                value={newNode.group}
                label="Group"
                onChange={(e) => setNewNode({ ...newNode, group: e.target.value })}
              >
                <MenuItem value="User">User</MenuItem>
                <MenuItem value="Frontend">Frontend</MenuItem>
                <MenuItem value="Backend">Backend</MenuItem>
                <MenuItem value="AI Services">AI Services</MenuItem>
                <MenuItem value="Data Layer">Data Layer</MenuItem>
                <MenuItem value="Messaging">Messaging</MenuItem>
                <MenuItem value="Security">Security</MenuItem>
                <MenuItem value="Monitoring">Monitoring</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>Icon</InputLabel>
              <Select
                value={newNode.icon}
                label="Icon"
                onChange={(e) => setNewNode({ ...newNode, icon: e.target.value })}
              >
                {Object.keys(iconMapping).map((iconName) => (
                  <MenuItem key={iconName} value={iconName}>
                    {iconName}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="Tooltip"
              value={newNode.tooltip}
              onChange={(e) => setNewNode({ ...newNode, tooltip: e.target.value })}
              fullWidth
              multiline
              rows={2}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddNodeDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleAddNode} variant="contained" disabled={!newNode.label}>
            Add Node
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ArchitectureDiagram;
