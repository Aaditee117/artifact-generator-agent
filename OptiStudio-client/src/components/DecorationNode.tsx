/**
 * Decoration Node Component for React Flow
 * Renders the Microsoft Azure logo/branding element.
 * No handles, no edges — purely decorative.
 */

import React, { memo } from 'react';
import { getLocalIconUrl } from '../utils/localIconAssets';

interface DecorationNodeData {
  label: string;
  azureType?: string;
}

interface DecorationNodeProps {
  data: DecorationNodeData;
}

const DecorationNode: React.FC<DecorationNodeProps> = ({ data }) => {
  const iconUrl = getLocalIconUrl(data.azureType || 'azure');

  // Make the logo much larger (e.g., 56x56)
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '16px',
        padding: '12px 24px',
        pointerEvents: 'none',
        userSelect: 'none',
      }}
    >
      {iconUrl ? (
        <img
          src={iconUrl}
          alt="Azure"
          style={{ width: 56, height: 56, objectFit: 'contain' }}
        />
      ) : (
        <svg width="56" height="56" viewBox="0 0 96 96">
          <path d="M33.338 6.544h26.038l-27.03 80.455a4.152 4.152 0 01-3.933 2.845H8.149a4.145 4.145 0 01-3.928-5.47L29.404 9.389a4.152 4.152 0 013.934-2.845z" fill="#0078D4" />
          <path d="M71.175 60.261h-41.29a1.911 1.911 0 00-1.305 3.309l26.532 24.764a4.171 4.171 0 002.846 1.121h23.38z" fill="#0078D4" />
          <path d="M33.338 6.544a4.118 4.118 0 00-3.943 2.879L4.252 83.917a4.14 4.14 0 003.908 5.538h20.787a4.443 4.443 0 003.41-2.9l5.014-14.777 17.91 16.705a4.237 4.237 0 002.666.972h23.394L62.262 60.261H34.314L53.233 6.544z" fill="#0078D4" opacity="0.8" />
        </svg>
      )}
      <span
        style={{
          fontSize: '18px',
          fontWeight: 700,
          color: '#0078D4',
          letterSpacing: '0.5px',
        }}
      >
        {data.label}
      </span>
    </div>
  );
};

export default memo(DecorationNode);
