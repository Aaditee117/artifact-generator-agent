/**
 * Container Node Component for React Flow
 * Renders a transparent/light-gray container that houses child nodes.
 * Used for Virtual Networks, Subnets, AI Foundry, Platform sections, etc.
 */

import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';

interface ContainerNodeData {
  label: string;
  containerStyle?: {
    backgroundColor?: string;
    borderColor?: string;
    borderStyle?: 'solid' | 'dashed';
  };
  isFuture?: boolean;
}

interface ContainerNodeProps {
  id: string;
  data: ContainerNodeData;
  selected?: boolean;
}

const ContainerNode: React.FC<ContainerNodeProps> = ({ data, selected }) => {
  const cStyle = data.containerStyle || {};
  const isFuture = data.isFuture || false;

  const borderColor = isFuture
    ? '#E53935'
    : selected
      ? '#0078D4'
      : (cStyle.borderColor || '#90CAF9');

  const borderStyle = isFuture ? 'dashed' : (cStyle.borderStyle || 'dashed');

  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        backgroundColor: cStyle.backgroundColor || 'rgba(0, 120, 212, 0.04)',
        border: `1.5px ${borderStyle} ${borderColor}`,
        borderRadius: 8,
        position: 'relative',
      }}
    >
      <Handle
        type="target"
        position={Position.Left}
        style={{ background: 'transparent', border: 'none', width: 1, height: 1 }}
      />

      {/* Container label at the top */}
      <div
        style={{
          position: 'absolute',
          top: 8,
          left: 12,
          fontSize: '11px',
          fontWeight: 600,
          color: isFuture ? '#E53935' : (cStyle.borderColor || '#1565C0'),
          textTransform: 'uppercase',
          letterSpacing: '0.5px',
          pointerEvents: 'none',
          userSelect: 'none',
        }}
      >
        {data.label}
      </div>

      <Handle
        type="source"
        position={Position.Right}
        style={{ background: 'transparent', border: 'none', width: 1, height: 1 }}
      />
    </div>
  );
};

export default memo(ContainerNode);
