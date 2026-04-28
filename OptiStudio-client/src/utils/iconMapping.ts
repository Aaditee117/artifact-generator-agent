/**
 * Azure Architecture Icon Mapping
 * Maps icon names to SVG paths (using Azure Architecture Icons)
 * Icons sourced from: https://learn.microsoft.com/en-us/azure/architecture/icons/
 */

// Icon categories and their Azure blue shades
export const iconColors: Record<string, string> = {
  compute: '#0078D4',
  database: '#5C2D91',
  storage: '#0078D4',
  ai: '#FF8C00',
  security: '#5C2D91',
  networking: '#0078D4',
  monitoring: '#008272',
  devops: '#F25022',
  messaging: '#0078D4',
  user: '#333333',
  frontend: '#61DAFB',
};

// Azure icon SVG inline data (simplified versions for React Flow nodes)
// In production, these would be actual Azure icon SVGs
export const iconMapping: Record<string, { svg: string; color: string; category: string }> = {
  // User/Client
  'user': {
    svg: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>`,
    color: '#333333',
    category: 'user',
  },

  // Frontend / Web Apps
  'app-service': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><path d="M9 0L0 4.5v9L9 18l9-4.5v-9L9 0zM9 2.12l6.22 3.11L9 8.34 2.78 5.23 9 2.12zM1.5 6.48l6.75 3.38v6.02l-6.75-3.38V6.48zm8.25 9.4V9.86l6.75-3.38v6.02l-6.75 3.38z"/></svg>`,
    color: '#0078D4',
    category: 'compute',
  },
  'static-web-app': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><rect x="2" y="2" width="14" height="10" rx="1" fill="none" stroke="currentColor" stroke-width="1.5"/><line x1="5" y1="14" x2="13" y2="14" stroke="currentColor" stroke-width="1.5"/><line x1="9" y1="12" x2="9" y2="16" stroke="currentColor" stroke-width="1.5"/></svg>`,
    color: '#0078D4',
    category: 'compute',
  },
  'react': {
    svg: `<svg viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="2.5"/><ellipse cx="12" cy="12" rx="10" ry="4" fill="none" stroke="currentColor" stroke-width="1"/><ellipse cx="12" cy="12" rx="10" ry="4" fill="none" stroke="currentColor" stroke-width="1" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="10" ry="4" fill="none" stroke="currentColor" stroke-width="1" transform="rotate(120 12 12)"/></svg>`,
    color: '#61DAFB',
    category: 'frontend',
  },
  'angular': {
    svg: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L2 7l1.5 11L12 22l8.5-4L22 7 12 2zm0 2.8l6.5 11.2H14l-1-2.5h-2l-1 2.5H5.5L12 4.8z"/></svg>`,
    color: '#DD0031',
    category: 'frontend',
  },
  'vue': {
    svg: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M2 3h4l6 10 6-10h4L12 21 2 3z"/></svg>`,
    color: '#42B883',
    category: 'frontend',
  },

  // Backend / API
  'functions': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><path d="M13.5 3h-9a1.5 1.5 0 00-1.5 1.5v9A1.5 1.5 0 004.5 15h9a1.5 1.5 0 001.5-1.5v-9A1.5 1.5 0 0013.5 3zm-3.38 9.64l-1.5-2.5-1.5 2.5H5.5l2.12-3.5L5.62 5.5h1.62l1.38 2.28 1.38-2.28h1.62l-2 3.64 2.12 3.5h-1.62z"/></svg>`,
    color: '#FFCA28',
    category: 'compute',
  },
  'container-apps': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><rect x="2" y="2" width="6" height="6" rx="0.5"/><rect x="10" y="2" width="6" height="6" rx="0.5"/><rect x="2" y="10" width="6" height="6" rx="0.5"/><rect x="10" y="10" width="6" height="6" rx="0.5"/></svg>`,
    color: '#326CE5',
    category: 'compute',
  },
  'aks': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><path d="M9 1L2 5v8l7 4 7-4V5L9 1zm0 2.15l4.9 2.8L9 8.75l-4.9-2.8L9 3.15zM3.5 6.52L8.25 9.2v5.28l-4.75-2.7V6.52zm11 0v5.78l-4.75 2.7V9.2l4.75-2.68z"/></svg>`,
    color: '#326CE5',
    category: 'compute',
  },
  'api-management': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><path d="M9 2a7 7 0 100 14A7 7 0 009 2zm0 1.5a5.5 5.5 0 110 11 5.5 5.5 0 010-11zM9 6a1 1 0 100 2 1 1 0 000-2zm0 3a1 1 0 00-1 1v2a1 1 0 002 0v-2a1 1 0 00-1-1z"/></svg>`,
    color: '#68217A',
    category: 'networking',
  },

  // AI / ML
  'cognitive-services': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><path d="M9 1C4.58 1 1 4.58 1 9s3.58 8 8 8 8-3.58 8-8-3.58-8-8-8zm0 14.5c-3.58 0-6.5-2.92-6.5-6.5S5.42 2.5 9 2.5s6.5 2.92 6.5 6.5-2.92 6.5-6.5 6.5z"/><circle cx="6.5" cy="8" r="1.5"/><circle cx="11.5" cy="8" r="1.5"/><path d="M9 14c2.21 0 4-1.34 4-3H5c0 1.66 1.79 3 4 3z"/></svg>`,
    color: '#0078D4',
    category: 'ai',
  },
  'openai': {
    svg: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M22.28 9.37a6.4 6.4 0 00-.55-5.27A6.47 6.47 0 0014.8.5a6.4 6.4 0 00-4.86 2.23A6.47 6.47 0 001.72 9.37a6.4 6.4 0 00.85 7.03 6.47 6.47 0 006.93 3.6 6.4 6.4 0 004.86-2.23 6.47 6.47 0 008.22-6.64 6.4 6.4 0 00-.3-1.76z"/></svg>`,
    color: '#10A37F',
    category: 'ai',
  },
  'azure-openai': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><path d="M9 1L2 5v8l7 4 7-4V5L9 1zm0 2l4.9 2.8L9 8.5 4.1 5.8 9 3zm-5.5 4l5 2.8v5.4l-5-2.8V7zm11 0v5.4l-5 2.8V9.8l5-2.8z"/><circle cx="9" cy="9" r="2" fill="#10A37F"/></svg>`,
    color: '#0078D4',
    category: 'ai',
  },
  'ai-foundry': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><rect x="2" y="2" width="14" height="14" rx="2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M5 9l2 2 4-4" stroke="currentColor" stroke-width="2"/><circle cx="13" cy="5" r="2"/></svg>`,
    color: '#FF8C00',
    category: 'ai',
  },
  'azure-ai-foundry': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><rect x="2" y="2" width="14" height="14" rx="2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M5 9l2 2 4-4" stroke="currentColor" stroke-width="2"/><circle cx="13" cy="5" r="2"/></svg>`,
    color: '#FF8C00',
    category: 'ai',
  },
  'foundry-models': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><circle cx="9" cy="9" r="6" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="9" cy="6" r="1.5"/><circle cx="6" cy="11" r="1.5"/><circle cx="12" cy="11" r="1.5"/><path d="M9 7.5v2M7.5 10l1-1M10.5 10l-1-1" stroke="currentColor"/></svg>`,
    color: '#FF8C00',
    category: 'ai',
  },

  // MCP / Agent Architecture
  'mcp-client': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><rect x="2" y="4" width="14" height="10" rx="1" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M5 8h8M5 11h5" stroke="currentColor"/><circle cx="14" cy="9" r="2" fill="currentColor"/></svg>`,
    color: '#5C6BC0',
    category: 'ai',
  },
  'mcp-server': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><rect x="4" y="2" width="10" height="14" rx="1" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="9" cy="5" r="1.5"/><rect x="6" y="8" width="6" height="2" rx="0.5"/><rect x="6" y="11" width="6" height="2" rx="0.5"/></svg>`,
    color: '#5C6BC0',
    category: 'ai',
  },
  'mcp-tool': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><path d="M11 2l-1 4 4-1 2 2-4 1 1 4-2 2-1-4-4 1-2-2 4-1-1-4 2-2z" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>`,
    color: '#5C6BC0',
    category: 'ai',
  },
  'agent-orchestrator': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><circle cx="9" cy="9" r="3" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="9" cy="3" r="1.5"/><circle cx="3" cy="9" r="1.5"/><circle cx="15" cy="9" r="1.5"/><circle cx="9" cy="15" r="1.5"/><path d="M9 4.5v1.5M9 12v1.5M4.5 9h1.5M12 9h1.5" stroke="currentColor"/></svg>`,
    color: '#7B1FA2',
    category: 'ai',
  },
  'generic-tool': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><path d="M14 4l-2 2 2 2-2 2 2 2M4 4l2 2-2 2 2 2-2 2" stroke="currentColor" stroke-width="1.5" fill="none"/><path d="M7 9h4" stroke="currentColor" stroke-width="2"/></svg>`,
    color: '#607D8B',
    category: 'ai',
  },
  'web-app': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><rect x="2" y="3" width="14" height="11" rx="1" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M2 6h14" stroke="currentColor"/><circle cx="4" cy="4.5" r="0.5"/><circle cx="6" cy="4.5" r="0.5"/><circle cx="8" cy="4.5" r="0.5"/></svg>`,
    color: '#0078D4',
    category: 'compute',
  },
  'machine-learning': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><path d="M9 2L2 6v6l7 4 7-4V6L9 2zm0 2l4.5 2.5L9 9 4.5 6.5 9 4zm-5.5 4l5 2.75v4.5l-5-2.75v-4.5zm11 0v4.5l-5 2.75v-4.5l5-2.75z"/></svg>`,
    color: '#0078D4',
    category: 'ai',
  },
  'bot-service': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><rect x="4" y="3" width="10" height="8" rx="1"/><circle cx="7" cy="7" r="1"/><circle cx="11" cy="7" r="1"/><path d="M6 13h6v2H6z"/><path d="M8 11h2v2H8z"/></svg>`,
    color: '#0078D4',
    category: 'ai',
  },
  'ai-search': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><circle cx="8" cy="8" r="5" fill="none" stroke="currentColor" stroke-width="2"/><line x1="12" y1="12" x2="16" y2="16" stroke="currentColor" stroke-width="2"/><path d="M6 8h4M8 6v4" stroke="currentColor" stroke-width="1"/></svg>`,
    color: '#0078D4',
    category: 'ai',
  },

  // Database
  'cosmos-db': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><ellipse cx="9" cy="5" rx="6" ry="2"/><path d="M3 5v8c0 1.1 2.69 2 6 2s6-.9 6-2V5" fill="none" stroke="currentColor" stroke-width="1.5"/><ellipse cx="9" cy="9" rx="6" ry="2" fill="none" stroke="currentColor" stroke-width="0.5"/></svg>`,
    color: '#0078D4',
    category: 'database',
  },
  'sql-database': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><ellipse cx="9" cy="4" rx="6" ry="2.5"/><path d="M3 4v10c0 1.38 2.69 2.5 6 2.5s6-1.12 6-2.5V4" fill="none" stroke="currentColor" stroke-width="1.5"/><ellipse cx="9" cy="9" rx="6" ry="2.5" fill="none" stroke="currentColor" stroke-width="0.5"/></svg>`,
    color: '#0078D4',
    category: 'database',
  },
  'sql-server': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><ellipse cx="9" cy="4" rx="6" ry="2.5"/><path d="M3 4v10c0 1.38 2.69 2.5 6 2.5s6-1.12 6-2.5V4" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>`,
    color: '#CC2927',
    category: 'database',
  },
  'mysql': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><ellipse cx="9" cy="4" rx="6" ry="2.5"/><path d="M3 4v10c0 1.38 2.69 2.5 6 2.5s6-1.12 6-2.5V4" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>`,
    color: '#4479A1',
    category: 'database',
  },
  'postgresql': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><ellipse cx="9" cy="4" rx="6" ry="2.5"/><path d="M3 4v10c0 1.38 2.69 2.5 6 2.5s6-1.12 6-2.5V4" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>`,
    color: '#336791',
    category: 'database',
  },
  'redis': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><path d="M9 2L2 6v6l7 4 7-4V6L9 2z"/></svg>`,
    color: '#DC382D',
    category: 'database',
  },

  // Storage
  'blob-storage': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><rect x="3" y="3" width="12" height="12" rx="1"/><rect x="5" y="5" width="3" height="3" rx="0.5"/><rect x="10" y="5" width="3" height="3" rx="0.5"/><rect x="5" y="10" width="3" height="3" rx="0.5"/><rect x="10" y="10" width="3" height="3" rx="0.5"/></svg>`,
    color: '#0078D4',
    category: 'storage',
  },
  'file-storage': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><path d="M3 3h9l3 3v9a1 1 0 01-1 1H3a1 1 0 01-1-1V4a1 1 0 011-1z"/><path d="M12 3v3h3" fill="none" stroke="currentColor"/></svg>`,
    color: '#0078D4',
    category: 'storage',
  },
  'data-lake': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><ellipse cx="9" cy="14" rx="7" ry="2"/><path d="M2 14V8c0-3.31 3.13-6 7-6s7 2.69 7 6v6" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>`,
    color: '#0078D4',
    category: 'storage',
  },

  // Messaging
  'service-bus': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><rect x="2" y="4" width="5" height="10" rx="0.5"/><rect x="11" y="4" width="5" height="10" rx="0.5"/><path d="M7 9h4" stroke="currentColor" stroke-width="2"/></svg>`,
    color: '#0078D4',
    category: 'messaging',
  },
  'event-grid': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><rect x="2" y="2" width="4" height="4"/><rect x="7" y="7" width="4" height="4"/><rect x="12" y="12" width="4" height="4"/><path d="M6 4l2 4M11 11l2 2" stroke="currentColor"/></svg>`,
    color: '#0078D4',
    category: 'messaging',
  },
  'event-hub': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><circle cx="9" cy="9" r="6" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="9" cy="9" r="2"/></svg>`,
    color: '#0078D4',
    category: 'messaging',
  },
  'queue-storage': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><rect x="3" y="4" width="12" height="3" rx="0.5"/><rect x="3" y="8" width="12" height="3" rx="0.5"/><rect x="3" y="12" width="12" height="3" rx="0.5"/></svg>`,
    color: '#0078D4',
    category: 'messaging',
  },

  // Security
  'key-vault': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><rect x="4" y="7" width="10" height="8" rx="1"/><circle cx="9" cy="5" r="3" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="9" cy="11" r="1.5"/><path d="M9 12.5v2"/></svg>`,
    color: '#5C2D91',
    category: 'security',
  },
  'active-directory': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><circle cx="9" cy="6" r="3"/><path d="M3 16c0-3.31 2.69-6 6-6s6 2.69 6 6"/></svg>`,
    color: '#0078D4',
    category: 'security',
  },
  'entra-id': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><circle cx="9" cy="6" r="3"/><path d="M3 16c0-3.31 2.69-6 6-6s6 2.69 6 6"/><path d="M14 10l2 2-2 2" stroke="currentColor"/></svg>`,
    color: '#0078D4',
    category: 'security',
  },
  'front-door': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><path d="M2 4h14v10H2z" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M9 4v10M2 9h14"/></svg>`,
    color: '#0078D4',
    category: 'networking',
  },

  // Monitoring
  'application-insights': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><circle cx="9" cy="9" r="7" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M5 9h3l1-3 2 6 1-3h2" stroke="currentColor" stroke-width="1.5" fill="none"/></svg>`,
    color: '#68217A',
    category: 'monitoring',
  },
  'monitor': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><rect x="2" y="3" width="14" height="9" rx="1" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M6 14h6M9 12v2"/></svg>`,
    color: '#0078D4',
    category: 'monitoring',
  },
  'log-analytics': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><rect x="2" y="2" width="14" height="14" rx="1" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M5 6h8M5 9h6M5 12h4" stroke="currentColor"/></svg>`,
    color: '#0078D4',
    category: 'monitoring',
  },

  // Networking
  'virtual-network': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><rect x="2" y="2" width="14" height="14" rx="1" fill="none" stroke="currentColor" stroke-width="1.5" stroke-dasharray="3,2"/><circle cx="5" cy="5" r="1.5"/><circle cx="13" cy="5" r="1.5"/><circle cx="5" cy="13" r="1.5"/><circle cx="13" cy="13" r="1.5"/><path d="M5 5l8 8M13 5l-8 8" stroke="currentColor" stroke-width="0.5"/></svg>`,
    color: '#0078D4',
    category: 'networking',
  },
  'load-balancer': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><circle cx="9" cy="4" r="2"/><circle cx="5" cy="14" r="2"/><circle cx="13" cy="14" r="2"/><path d="M9 6v4M9 10l-4 2M9 10l4 2" stroke="currentColor"/></svg>`,
    color: '#0078D4',
    category: 'networking',
  },
  'cdn': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><circle cx="9" cy="9" r="6" fill="none" stroke="currentColor" stroke-width="1.5"/><ellipse cx="9" cy="9" rx="2.5" ry="6" fill="none" stroke="currentColor" stroke-width="1"/><path d="M3 9h12" stroke="currentColor"/></svg>`,
    color: '#0078D4',
    category: 'networking',
  },
  'dns': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><rect x="2" y="6" width="14" height="6" rx="1" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="5" cy="9" r="1"/><path d="M8 9h6"/></svg>`,
    color: '#0078D4',
    category: 'networking',
  },

  // DevOps
  'devops': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><circle cx="9" cy="9" r="6" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M6 9l2 2 4-4" stroke="currentColor" stroke-width="1.5"/></svg>`,
    color: '#0078D4',
    category: 'devops',
  },
  'github': {
    svg: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.604-3.369-1.341-3.369-1.341-.454-1.155-1.11-1.462-1.11-1.462-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0112 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.163 22 16.418 22 12c0-5.523-4.477-10-10-10z"/></svg>`,
    color: '#181717',
    category: 'devops',
  },
  'container-registry': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><rect x="2" y="2" width="14" height="14" rx="1" fill="none" stroke="currentColor" stroke-width="1.5"/><rect x="5" y="5" width="3" height="3"/><rect x="10" y="5" width="3" height="3"/><rect x="5" y="10" width="3" height="3"/><rect x="10" y="10" width="3" height="3"/></svg>`,
    color: '#0078D4',
    category: 'devops',
  },

  // Microsoft 365 / External
  'ms-teams': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><rect x="2" y="4" width="10" height="10" rx="1" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M5 8h4M7 6v4" stroke="currentColor" stroke-width="1.5"/><circle cx="14" cy="6" r="2" fill="none" stroke="currentColor" stroke-width="1"/><path d="M12 9h4v4h-4z" fill="none" stroke="currentColor"/></svg>`,
    color: '#6264A7',
    category: 'external',
  },
  'sharepoint': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><circle cx="6" cy="9" r="4" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="11" cy="7" r="3" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="13" cy="12" r="2.5" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>`,
    color: '#038387',
    category: 'external',
  },
  'microsoft-fabric': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><path d="M2 9l7-7 7 7-7 7-7-7z" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M5 9h8M9 5v8" stroke="currentColor"/></svg>`,
    color: '#F25022',
    category: 'external',
  },
  'power-bi': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><rect x="3" y="8" width="3" height="7" rx="0.5"/><rect x="7.5" y="5" width="3" height="10" rx="0.5"/><rect x="12" y="2" width="3" height="13" rx="0.5"/></svg>`,
    color: '#F2C811',
    category: 'external',
  },
  'databricks': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><path d="M9 2l7 4v8l-7 4-7-4V6l7-4z" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M2 6l7 4 7-4M9 10v8" stroke="currentColor"/></svg>`,
    color: '#FF3621',
    category: 'external',
  },
  'synapse': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><ellipse cx="9" cy="9" rx="7" ry="3" fill="none" stroke="currentColor" stroke-width="1.5"/><ellipse cx="9" cy="9" rx="7" ry="3" fill="none" stroke="currentColor" stroke-width="1.5" transform="rotate(60 9 9)"/><ellipse cx="9" cy="9" rx="7" ry="3" fill="none" stroke="currentColor" stroke-width="1.5" transform="rotate(120 9 9)"/></svg>`,
    color: '#0078D4',
    category: 'external',
  },

  // Networking additions
  'private-endpoint': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><rect x="2" y="6" width="14" height="6" rx="1" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="5" cy="9" r="1.5" fill="currentColor"/><path d="M7 9h8" stroke="currentColor" stroke-width="1.5"/><circle cx="14" cy="9" r="1" fill="none" stroke="currentColor"/></svg>`,
    color: '#0078D4',
    category: 'networking',
  },
  'azure-private-endpoint': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><rect x="2" y="6" width="14" height="6" rx="1" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="5" cy="9" r="1.5" fill="currentColor"/><path d="M7 9h8" stroke="currentColor" stroke-width="1.5"/><circle cx="14" cy="9" r="1" fill="none" stroke="currentColor"/></svg>`,
    color: '#0078D4',
    category: 'networking',
  },
  'application-gateway': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><rect x="2" y="4" width="14" height="10" rx="1" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M6 7v4M9 7v4M12 7v4" stroke="currentColor" stroke-width="1.5"/></svg>`,
    color: '#0078D4',
    category: 'networking',
  },
  'firewall': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><path d="M9 2l6 3v5c0 3.31-2.69 6-6 6s-6-2.69-6-6V5l6-3z" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M7 8l2 2 2-2" stroke="currentColor" stroke-width="1.5"/></svg>`,
    color: '#C62828',
    category: 'networking',
  },

  // Default fallback
  'default': {
    svg: `<svg viewBox="0 0 18 18" fill="currentColor"><rect x="2" y="2" width="14" height="14" rx="2" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="9" cy="9" r="3"/></svg>`,
    color: '#0078D4',
    category: 'compute',
  },
};

/**
 * Get icon data by name with fallback to default
 */
export function getIconData(iconName: string): { svg: string; color: string; category: string } {
  return iconMapping[iconName] || iconMapping['default'];
}

/**
 * Group background colors
 */
export const groupColors: Record<string, string> = {
  'User': '#F5F5F5',
  'Frontend': '#E3F2FD',
  'Backend': '#E8F5E9',
  'AI Services': '#FFF3E0',
  'AI Layer': '#FFF3E0',
  'Data Layer': '#F3E5F5',
  'Data': '#F3E5F5',
  'Storage': '#F3E5F5',
  'Messaging': '#E0F7FA',
  'Security': '#FCE4EC',
  'Monitoring': '#E8EAF6',
  'Networking': '#E1F5FE',
  'DevOps': '#FFEBEE',
  'External': '#FAFAFA',
  // MCP / Agent specific groups
  'MCP Layer': '#EEF0FA',
  'MCP Client-Server Layer': '#EEF0FA',
  'Agent Layer': '#EDE7F6',
  'Orchestration': '#EDE7F6',
  // Azure architecture groups
  'Azure Container App': '#E8F4FD',
  'Container App': '#E8F4FD',
  'Virtual Network': '#FFF9E6',
  'VNet': '#FFF9E6',
  'Azure AI Foundry': '#FFF3E0',
  'AI Foundry': '#FFF3E0',
  // Data sources
  'Data Sources': '#FFF0F0',
  'External Services': '#FFF0F0',
  'default': '#F3F6FC',
};

/**
 * Get group color by name with fallback
 */
export function getGroupColor(groupName: string): string {
  return groupColors[groupName] || groupColors['default'];
}
