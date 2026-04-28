/**
 * Local Azure Icon Asset Map
 *
 * Maps icon names (used in LLM-generated architecture diagrams) to local SVG
 * files from src/assets/. These are official Microsoft Azure Architecture icons.
 *
 * The icons are organized by Azure service category, matching the folder
 * structure under src/assets/.
 */

// Dynamically import all SVG files from asset directories
const iconModules = import.meta.glob('../assets/**/*.svg', { eager: true, query: '?url', import: 'default' }) as Record<string, string>;

/**
 * Build a lookup: lowercase filename (without .svg) → resolved URL
 * e.g. "function-apps" → "/src/assets/Compute/Function-Apps.svg"
 */
const filenameLookup: Record<string, string> = {};
for (const [path, url] of Object.entries(iconModules)) {
  // Extract filename without extension: "../assets/Compute/Function-Apps.svg" → "function-apps"
  const filename = path.split('/').pop()?.replace('.svg', '').toLowerCase() ?? '';
  filenameLookup[filename] = url;
}

/**
 * Map of icon-name (from LLM) → local asset filename (lowercase, hyphenated)
 *
 * The LLM produces icon names like "app-service", "cosmos-db", "openai" etc.
 * We map those to the exact filenames in the assets folder.
 */
const iconNameToFilename: Record<string, string> = {
  // Azure Brand (robust mapping for all common names)
  'azure': 'azure-a',
  'azure-logo': 'azure-a',
  'microsoft-azure': 'azure-a',
  'azure_a': 'azure-a',
  'azurebrand': 'azure-a',
  'azurelogo': 'azure-a',
  'microsoftazure': 'azure-a',
  'azure (logo)': 'azure-a',
  'azure (brand)': 'azure-a',
  // Compute
  'app-service': 'app-services',
  'functions': 'function-apps',
  'function-app': 'function-apps',
  'function-apps': 'function-apps',
  'container-apps': 'container-instances',
  'container-instances': 'container-instances',
  'aks': 'kubernetes-services',
  'kubernetes': 'kubernetes-services',
  'virtual-machine': 'virtual-machine',
  'virtual-machines': 'virtual-machine',
  'vm': 'virtual-machine',
  'vm-scale-sets': 'vm-scale-sets',
  'batch': 'batch-accounts',
  'service-fabric': 'service-fabric-clusters',
  'spring-apps': 'azure-spring-apps',
  'static-web-app': 'static-apps',

  // Containers
  'container-registry': 'container-registries',

  // Databases
  'cosmos-db': 'azure-cosmos-db',
  'cosmosdb': 'azure-cosmos-db',
  'sql-database': 'sql-database',
  'sql-server': 'sql-server',
  'azure-sql': 'azure-sql',
  'mysql': 'azure-database-mysql-server',
  'postgresql': 'azure-database-postgresql-server',
  'redis': 'cache-redis',
  'managed-database': 'managed-database',

  // Storage
  'blob-storage': 'storage-accounts',
  'storage': 'storage-accounts',
  'storage-accounts': 'storage-accounts',
  'file-storage': 'azure-fileshares',
  'data-lake': 'data-lake-storage-gen1',
  'netapp': 'azure-netapp-files',

  // AI + Machine Learning
  'openai': 'azure-openai',
  'azure-openai': 'azure-openai',
  'cognitive-services': 'cognitive-services',
  'ai-search': 'cognitive-search',
  'search': 'cognitive-search',
  'machine-learning': 'machine-learning',
  'bot-service': 'bot-services',
  'ai-studio': 'ai-studio',
  'content-safety': 'content-safety',
  'computer-vision': 'computer-vision',
  'speech': 'speech-services',
  'language': 'language',
  'translator': 'translator-text',
  'form-recognizer': 'form-recognizers',
  'anomaly-detector': 'anomaly-detector',
  // AI Foundry / Models
  'ai-foundry': 'ai-studio',
  'azure-ai-foundry': 'ai-studio',
  'foundry-models': 'machine-learning',
  'gpt-4': 'azure-openai',
  'gpt-4o': 'azure-openai',
  'gpt-35-turbo': 'azure-openai',
  'embeddings': 'azure-openai',

  // MCP / Agent Architecture (use AI icons as fallback)
  'mcp-client': 'cognitive-services',
  'mcp-server': 'cognitive-services',
  'mcp-tool': 'cognitive-services',
  'agent-orchestrator': 'cognitive-services',
  'generic-tool': 'cognitive-services',

  // Networking
  'api-management': 'api-management-services',
  'front-door': 'front-door-and-cdn-profiles',
  'virtual-network': 'virtual-networks',
  'vnet': 'virtual-networks',
  'load-balancer': 'load-balancers',
  'cdn': 'cdn-profiles',
  'dns': 'dns-zones',
  'application-gateway': 'application-gateways',
  'firewall': 'firewalls',
  'bastion': 'bastions',
  'ddos': 'ddos-protection-plans',
  'expressroute': 'expressroute-circuits',
  'nat': 'nat',
  'nsg': 'network-security-groups',
  'private-link': 'private-link',
  'traffic-manager': 'traffic-manager-profiles',
  'vpn-gateway': 'virtual-network-gateways',
  // 'waf': 'web-application-firewall-policies(waf)',
  'subnet': 'subnet',

  // Security
  'key-vault': 'key-vaults',
  'entra-id': 'azure-ad-b2c',
  'active-directory': 'azure-ad-b2c',
  'sentinel': 'azure-sentinel',
  'defender': 'microsoft-defender-for-cloud',
  'conditional-access': 'conditional-access',
  'managed-identity': 'managed-identities',
  'mfa': 'multifactor-authentication',

  // Integration
  'service-bus': 'azure-service-bus',
  'event-grid': 'event-grid-domains',
  'event-hub': 'event-grid-topics',
  'logic-apps': 'logic-apps',
  'api-connections': 'api-connections',

  // Messaging / Queues
  'queue-storage': 'storage-accounts',

  // Monitoring / DevOps
  'application-insights': 'application-insights',
  'app-insights': 'application-insights',
  'monitor': 'monitor',
  'azure-monitor': 'monitor',
  'log-analytics': 'monitor',
  'devops': 'azure-devops',
  'azure-devops': 'azure-devops',
  'devtest-labs': 'devtest-labs',

  // App Services
  'app-service-plan': 'app-service-plans',
  'notification-hub': 'notification-hubs',
  'signalr': 'signalr',

  // Management
  'policy': 'policy',
  'automation': 'automation-accounts',
  'arc': 'azure-arc',
  'blueprints': 'blueprints',

  // Identity
  'b2c': 'azure-ad-b2c',
  'app-registration': 'app-registrations',
  'enterprise-app': 'enterprise-applications',

  // General / Misc
  'resource-group': 'resource-groups',
  'subscription': 'subscriptions',
  'dashboard': 'dashboard',
  'user': 'users',
  'users': 'users',
  'browser': 'browser',
  'mobile': 'mobile',
  'website': 'website-staging',
  'web-app': 'app-services',

  // Microsoft 365 / External (map to generic icons)
  'ms-teams': 'notification-hubs',
  'sharepoint': 'storage-accounts',
  'microsoft-fabric': 'data-lake-storage-gen1',
  'power-bi': 'monitor',
  'databricks': 'azure-databricks',
  'synapse': 'azure-synapse-analytics',

  // Additional Networking
  'private-endpoint': 'private-link',
  'azure-private-endpoint': 'private-link',
  // 'application-gateway': 'application-gateways',
  // 'firewall': 'firewalls',
  'waf': 'web-application-firewall-policies(waf)',
  'ddos-protection': 'ddos-protection-plans',
};

/**
 * Get the local asset URL for a given icon name.
 * Returns null if no matching icon is found.
 */
export function getLocalIconUrl(iconName: string): string | null {
  if (!iconName) return null;

  const key = iconName.toLowerCase().trim();

  // 1. Direct mapping from LLM name → filename
  const mappedFilename = iconNameToFilename[key];
  if (mappedFilename && filenameLookup[mappedFilename]) {
    return filenameLookup[mappedFilename];
  }

  // 2. Try the icon name directly as a filename
  if (filenameLookup[key]) {
    return filenameLookup[key];
  }

  // 3. Fuzzy match: try finding a filename that contains the key
  for (const [filename, url] of Object.entries(filenameLookup)) {
    if (filename.includes(key) || key.includes(filename)) {
      return url;
    }
  }

  // 4. Special fallback: if the iconName contains 'azure' and we have 'azure-a', always use it
  if (key.includes('azure') && filenameLookup['azure-a']) {
    return filenameLookup['azure-a'];
  }

  return null;
}

/**
 * Get all available icon names (for debugging / autocomplete)
 */
export function getAvailableIcons(): string[] {
  return Object.keys(iconNameToFilename);
}
