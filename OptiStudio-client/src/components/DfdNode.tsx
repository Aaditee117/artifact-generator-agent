import React, { memo, useState } from 'react';
import { Handle, Position } from '@xyflow/react';
import { Tooltip, TextField, IconButton } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';

interface DfdNodeData {
  label: string;
  technology: string;
  tooltip: string;
  icon: string;
  onLabelChange?: (id: string, newLabel: string) => void;
}

interface DfdNodeProps {
  id: string;
  data: DfdNodeData;
  selected?: boolean;
}

const DfdNode: React.FC<DfdNodeProps> = ({ id, data, selected }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedLabel, setEditedLabel] = useState(data.label);

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
    if (e.key === 'Enter') handleSave();
    else if (e.key === 'Escape') handleCancel();
  };

  const isDb = data.icon === 'sql-database' || data.icon === 'database';
  const isUser = data.icon === 'user' || data.technology?.toLowerCase().includes('user');
  const isDecision = data.label.includes('?');

  let borderRadius = '6px';
  if (isUser) borderRadius = '50px';
  else if (isDecision) borderRadius = '20px';

  let bgColor = '#ffffff';
  if (isDb) bgColor = '#fcf9e8';
  else if (isUser) bgColor = '#e8f4fc';
  else if (isDecision) bgColor = '#fce8f4';

  return (
    <Tooltip title={data.tooltip || data.technology || ''} placement="top" arrow>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '14px 24px',
          backgroundColor: bgColor,
          border: '2px solid #e0e0e0',
          borderRadius,
          boxShadow: selected ? '0 4px 12px rgba(0, 0, 0, 0.15)' : '0 2px 4px rgba(0, 0, 0, 0.05)',
          minWidth: '100px',
          maxWidth: '180px',
          cursor: 'grab',
          transition: 'all 0.2s ease',
        }}
      >
        <Handle
          type="target"
          position={Position.Left}
          style={{ background: '#555', width: 8, height: 8, border: '2px solid white' }}
        />

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
                inputProps={{ style: { fontSize: '13px', padding: '4px 6px' } }}
              />
              <IconButton size="small" onClick={handleSave} color="primary" sx={{ padding: '2px' }}>
                <CheckIcon sx={{ fontSize: 14 }} />
              </IconButton>
              <IconButton size="small" onClick={handleCancel} sx={{ padding: '2px' }}>
                <CloseIcon sx={{ fontSize: 14 }} />
              </IconButton>
            </div>
          ) : (
            <div
              style={{
                fontWeight: 600,
                fontSize: '13px',
                color: '#333',
                lineHeight: '1.4',
                wordWrap: 'break-word',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '4px',
              }}
            >
              {data.label}
              {selected && (
                <IconButton size="small" onClick={() => setIsEditing(true)} sx={{ padding: '1px' }}>
                  <EditIcon sx={{ fontSize: 12, color: '#0078d4' }} />
                </IconButton>
              )}
            </div>
          )}
        </div>

        <Handle
          type="source"
          position={Position.Right}
          style={{ background: '#555', width: 8, height: 8, border: '2px solid white' }}
        />
      </div>
    </Tooltip>
  );
};

export default memo(DfdNode);

