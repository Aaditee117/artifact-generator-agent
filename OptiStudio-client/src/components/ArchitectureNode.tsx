/**
 * Custom Architecture Node Component for React Flow
 * Renders a node with a centered Azure icon and label below it.
 * Supports variants: service (default), brain (blue orchestrator), future (dashed red).
 */

import React, { memo, useState } from 'react';
import { Handle, Position } from '@xyflow/react';
import { Tooltip, TextField, IconButton } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';
import { getIconData } from '../utils/iconMapping';
import { getLocalIconUrl } from '../utils/localIconAssets';

interface ArchitectureNodeData {
  label: string;
  technology: string;
  tooltip: string;
  group: string;
  icon: string;
  azureType?: string;
  nodeType?: 'service' | 'brain' | 'future';
  isFuture?: boolean;
  onLabelChange?: (id: string, newLabel: string) => void;
  position?: { x: number; y: number };
}

interface ArchitectureNodeProps {
  id: string;
  data: ArchitectureNodeData;
  selected?: boolean;
}

const ArchitectureNode: React.FC<ArchitectureNodeProps> = ({ id, data, selected }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedLabel, setEditedLabel] = useState(data.label);

  const iconKey = data.azureType || data.icon;
  const iconData = getIconData(iconKey);
  const localIconUrl = getLocalIconUrl(iconKey);

  const isFuture = data.isFuture || data.nodeType === 'future';
  const isBrain = data.nodeType === 'brain';

  // Visual style per variant
  const bgColor = isBrain ? '#E3F2FD' : isFuture ? '#FFF0F0' : '#ffffff';
  const borderColor = isFuture
    ? '#E53935'
    : selected
      ? iconData.color
      : '#333333';
  const borderStyle = isFuture ? '2px dashed' : `1px solid`;

  const handleSave = () => {
    if (data.onLabelChange) {
      data.onLabelChange(id, editedLabel);
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedLabel(data.label);
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSave();
    } else if (e.key === 'Escape') {
      handleCancel();
    }
  };

  // Special left-align for footer nodes
  const isFooter = ["devops", "key-vault", "monitor", "application-insights"].includes(
    (data.azureType || data.icon || '').toLowerCase()
  ) && data.position && data.position.y === 800;

  return (
    <Tooltip title={data.tooltip || data.technology} placement="top" arrow>
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: isFooter ? 'flex-start' : 'center',
          padding: isBrain ? '14px 20px' : '10px 12px',
          borderRadius: '6px',
          backgroundColor: bgColor,
          border: `${borderStyle} ${borderColor}`,
          boxShadow: selected
            ? `0 4px 12px rgba(0, 0, 0, 0.15)`
            : '0 1px 3px rgba(0, 0, 0, 0.08)',
          minWidth: isBrain ? '130px' : '80px',
          maxWidth: isBrain ? '200px' : '140px',
          cursor: 'grab',
          transition: 'all 0.2s ease',
          ...(isFuture ? { strokeDasharray: '5,5' } : {}),
        }}
      >
        {/* Input handle (left side) */}
        <Handle
          type="target"
          position={Position.Left}
          style={{
            background: iconData.color,
            width: 8,
            height: 8,
            border: '2px solid white',
          }}
        />

        {/* Icon — centered above label */}
        <div style={{ marginBottom: '6px' }}>
          {localIconUrl ? (
            <img
              src={localIconUrl}
              alt={iconKey}
              style={{
                width: isBrain ? 44 : 36,
                height: isBrain ? 44 : 36,
                objectFit: 'contain',
              }}
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = 'none';
                const sibling = (e.target as HTMLImageElement).nextElementSibling as HTMLElement;
                if (sibling) sibling.style.display = 'flex';
              }}
            />
          ) : null}
          <div
            style={{
              width: isBrain ? 44 : 36,
              height: isBrain ? 44 : 36,
              display: localIconUrl ? 'none' : 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: iconData.color,
            }}
            dangerouslySetInnerHTML={{ __html: iconData.svg }}
          />
        </div>

        {/* Label below icon */}
        <div style={{ textAlign: 'center', width: '100%' }}>
          {isEditing ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '2px' }}>
              <TextField
                value={editedLabel}
                onChange={(e) => setEditedLabel(e.target.value)}
                onKeyDown={handleKeyDown}
                size="small"
                autoFocus
                sx={{ flex: 1 }}
                inputProps={{ style: { fontSize: '11px', padding: '4px 6px' } }}
              />
              <IconButton size="small" onClick={handleSave} color="primary">
                <CheckIcon sx={{ fontSize: 12 }} />
              </IconButton>
              <IconButton size="small" onClick={handleCancel}>
                <CloseIcon sx={{ fontSize: 12 }} />
              </IconButton>
            </div>
          ) : (
            <div
              style={{
                fontWeight: isBrain ? 700 : 600,
                fontSize: isBrain ? '12px' : '11px',
                color: isFuture ? '#C62828' : '#333',
                lineHeight: '1.3',
                wordWrap: 'break-word',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '3px',
              }}
            >
              {data.label}
              {selected && (
                <IconButton
                  size="small"
                  onClick={() => setIsEditing(true)}
                  sx={{ padding: '1px' }}
                >
                  <EditIcon sx={{ fontSize: 12 }} />
                </IconButton>
              )}
            </div>
          )}
        </div>

        {/* Output handle (right side) */}
        <Handle
          type="source"
          position={Position.Right}
          style={{
            background: iconData.color,
            width: 8,
            height: 8,
            border: '2px solid white',
          }}
        />
      </div>
    </Tooltip>
  );
};

export default memo(ArchitectureNode);
