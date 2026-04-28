/**
 * Official Azure Architecture Icon CDN URLs
 * Source: https://learn.microsoft.com/en-us/azure/architecture/icons/
 *
 * These map icon names used in the LLM-generated architecture diagrams
 * to the official Microsoft Azure icon SVG URLs.
 *
 * CDN base: https://raw.githubusercontent.com/microsoft/azure-icons/main/icons/
 */

const AZURE_ICON_CDN_BASE =
  'https://raw.githubusercontent.com/microsoft/azure-icons/main/icons';

/** Map of icon-name → CDN path (relative to base) */
export const azureIconCdnMap: Record<string, string> = {
  // Compute
  'app-service': `${AZURE_ICON_CDN_BASE}/App%20Services.svg`,
  'functions': `${AZURE_ICON_CDN_BASE}/Function%20Apps.svg`,
  'container-apps': `${AZURE_ICON_CDN_BASE}/Container%20Apps.svg`,
  'aks': `${AZURE_ICON_CDN_BASE}/Kubernetes%20Services.svg`,
  'static-web-app': `${AZURE_ICON_CDN_BASE}/Static%20Apps.svg`,
  'virtual-machine': `${AZURE_ICON_CDN_BASE}/Virtual%20Machine.svg`,

  // Containers
  'container-registry': `${AZURE_ICON_CDN_BASE}/Container%20Registries.svg`,

  // Databases
  'cosmos-db': `${AZURE_ICON_CDN_BASE}/Azure%20Cosmos%20DB.svg`,
  'sql-database': `${AZURE_ICON_CDN_BASE}/SQL%20Database.svg`,
  'sql-server': `${AZURE_ICON_CDN_BASE}/SQL%20Server.svg`,
  'mysql': `${AZURE_ICON_CDN_BASE}/Azure%20Database%20for%20MySQL.svg`,
  'postgresql': `${AZURE_ICON_CDN_BASE}/Azure%20Database%20for%20PostgreSQL.svg`,
  'redis': `${AZURE_ICON_CDN_BASE}/Azure%20Cache%20for%20Redis.svg`,

  // Storage
  'blob-storage': `${AZURE_ICON_CDN_BASE}/Storage%20Accounts.svg`,
  'file-storage': `${AZURE_ICON_CDN_BASE}/Storage%20Accounts.svg`,
  'data-lake': `${AZURE_ICON_CDN_BASE}/Data%20Lake.svg`,

  // AI + Machine Learning
  'openai': `${AZURE_ICON_CDN_BASE}/Azure%20OpenAI.svg`,
  'cognitive-services': `${AZURE_ICON_CDN_BASE}/Cognitive%20Services.svg`,
  'ai-search': `${AZURE_ICON_CDN_BASE}/AI%20Search.svg`,
  'machine-learning': `${AZURE_ICON_CDN_BASE}/Machine%20Learning.svg`,
  'bot-service': `${AZURE_ICON_CDN_BASE}/Bot%20Services.svg`,

  // Networking
  'api-management': `${AZURE_ICON_CDN_BASE}/API%20Management%20Services.svg`,
  'front-door': `${AZURE_ICON_CDN_BASE}/Front%20Doors.svg`,
  'virtual-network': `${AZURE_ICON_CDN_BASE}/Virtual%20Networks.svg`,
  'load-balancer': `${AZURE_ICON_CDN_BASE}/Load%20Balancers.svg`,
  'cdn': `${AZURE_ICON_CDN_BASE}/CDN%20Profiles.svg`,
  'dns': `${AZURE_ICON_CDN_BASE}/DNS%20Zones.svg`,
  'application-gateway': `${AZURE_ICON_CDN_BASE}/Application%20Gateways.svg`,

  // Security
  'key-vault': `${AZURE_ICON_CDN_BASE}/Key%20Vaults.svg`,
  'entra-id': `${AZURE_ICON_CDN_BASE}/Entra%20ID.svg`,
  'active-directory': `${AZURE_ICON_CDN_BASE}/Entra%20ID.svg`,

  // Messaging
  'service-bus': `${AZURE_ICON_CDN_BASE}/Service%20Bus.svg`,
  'event-grid': `${AZURE_ICON_CDN_BASE}/Event%20Grid%20Domains.svg`,
  'event-hub': `${AZURE_ICON_CDN_BASE}/Event%20Hubs.svg`,
  'queue-storage': `${AZURE_ICON_CDN_BASE}/Storage%20Accounts.svg`,

  // Monitoring / DevOps
  'application-insights': `${AZURE_ICON_CDN_BASE}/Application%20Insights.svg`,
  'monitor': `${AZURE_ICON_CDN_BASE}/Monitor.svg`,
  'log-analytics': `${AZURE_ICON_CDN_BASE}/Log%20Analytics%20Workspaces.svg`,
  'devops': `${AZURE_ICON_CDN_BASE}/Azure%20DevOps.svg`,
};

/**
 * Get the official Azure CDN icon URL for a given icon name.
 * Returns null if no CDN URL is available (falls back to inline SVG).
 */
export function getAzureIconUrl(iconName: string): string | null {
  return azureIconCdnMap[iconName] ?? null;
}
