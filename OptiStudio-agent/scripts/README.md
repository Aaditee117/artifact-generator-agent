# Azure Architecture Icons Management

This directory contains tools and documentation for managing Azure architecture icons used in OptiStudio's diagram generation.

## Overview

OptiStudio uses official Microsoft Azure architecture icons from two sources:
1. **Local Icons**: SVG files stored in `OptiStudio-client/src/assets/` (608+ icons)
2. **Draw.io Icons**: Built-in Azure2 library in draw.io (for draw.io diagram generation)

## Directory Structure

```
OptiStudio-agent/scripts/
├── update_azure_icons.py              # Script to update local icons from Microsoft
├── azure_services_metadata.json       # Service status tracking (current/deprecated/discontinued)
└── README.md                          # This file

OptiStudio-client/src/assets/
├── AI-and-Machine-Learning/           # AI service icons (OpenAI, Cognitive Services, etc.)
├── Analytics/                         # Analytics icons (Synapse, Databricks, etc.)
├── App-Services/                      # App Service icons
├── Compute/                           # Compute icons (VMs, Functions, etc.)
├── Containers/                        # Container icons (AKS, Container Apps, etc.)
├── Databases/                         # Database icons (Cosmos DB, SQL, etc.)
├── Networking/                        # Networking icons (VNet, Gateway, etc.)
├── Security/                          # Security icons (Key Vault, Sentinel, etc.)
├── Storage/                           # Storage icons
└── ... (more categories)
```

## Icon Sources

### Official Microsoft Azure Icons

**Source**: https://learn.microsoft.com/en-us/azure/architecture/icons/  
**GitHub**: https://github.com/microsoft/azure-icons

Microsoft provides official Azure architecture icons that are:
- Regularly updated with new services
- Consistent in style and branding
- Optimized for architecture diagrams
- Free to use with proper attribution

### Icon Guidelines

When using Azure icons in diagrams, follow Microsoft's guidelines:

1. **Use Official Icons**: Always use official Microsoft icons, not third-party alternatives
2. **Consistent Style**: All icons should be from the same Azure icon set (2024+ style)
3. **Proper Sizing**: Icons should be 64x64 or 80x80 pixels in diagrams
4. **Azure Branding**: Include Azure logo in top-right corner of architecture diagrams
5. **Color Consistency**: Use Azure's official colors:
   - Azure Blue: `#0078D4`
   - AI Orange: `#FF8C00`
   - Security Purple: `#5C2D91`
   - Data Blue: `#50E6FF`

## Updating Icons

### Automated Update (Recommended)

Run the update script to fetch the latest icons from Microsoft:

```bash
cd OptiStudio-agent
python scripts/update_azure_icons.py
```

Options:
- `--force` or `-f`: Force re-download all icons even if unchanged

The script will:
1. Fetch latest icons from Microsoft's GitHub repository
2. Categorize them automatically
3. Save them to `OptiStudio-client/src/assets/`
4. Update `azure_services_metadata.json` with service status
5. Report new, updated, and skipped icons

### Manual Icon Management

If you need to add a specific icon manually:

1. Download the SVG from https://github.com/microsoft/azure-icons/tree/main/icons
2. Save it to the appropriate category folder in `OptiStudio-client/src/assets/`
3. Update `OptiStudio-client/src/utils/localIconAssets.ts` if needed
4. Update `azure_services_metadata.json` with service info

## Service Status Tracking

The `azure_services_metadata.json` file tracks:

### Service Status Categories

1. **Current Services**: Active Azure services in production
2. **Preview Services**: Services in public/private preview
3. **Deprecated Services**: Services being phased out (with replacement info)
4. **Discontinued Services**: Services no longer available

### Example Metadata Entry

```json
{
  "azure-openai": {
    "display_name": "Azure OpenAI",
    "status": "current",
    "category": "AI-and-Machine-Learning",
    "description": "Azure OpenAI Service provides REST API access to OpenAI's powerful language models",
    "icon_filename": "Azure-OpenAI.svg",
    "official_docs": "https://learn.microsoft.com/en-us/azure/ai-services/openai/"
  }
}
```

### Deprecated Services

When a service is deprecated or renamed:

```json
{
  "name": "azure-active-directory",
  "replaced_by": "entra-id",
  "deprecation_date": "2023-07-01",
  "note": "Renamed to Microsoft Entra ID"
}
```

## Icon Mapping

Icons are mapped in two places:

### 1. Frontend (React Flow Diagrams)

**File**: `OptiStudio-client/src/utils/localIconAssets.ts`

Maps icon names used by the LLM to local SVG files:

```typescript
const iconNameToFilename: Record<string, string> = {
  'openai': 'azure-openai',
  'cosmos-db': 'azure-cosmos-db',
  // ...
};
```

### 2. Backend (Draw.io Diagrams)

**File**: `OptiStudio-agent/tools/drawio_client.py`

Maps icon names to draw.io's built-in Azure2 library:

```python
AZURE_ICON_STYLES = {
    "openai": "sketch=0;...image=img/lib/azure2/ai_machine_learning/Azure_OpenAI.svg;",
    "cosmos-db": "sketch=0;...image=img/lib/azure2/databases/Azure_Cosmos_DB.svg;",
    # ...
}
```

## Microsoft Architecture Diagram Style

Generated diagrams should match Microsoft's official architecture diagram style:

### Layout Guidelines

1. **Logical Grouping**: Group related services in containers/subnets
2. **Left-to-Right Flow**: User → Frontend → API → Backend → Data
3. **Vertical Tiers**: 
   - Top: External entities (users, devices)
   - Middle: Application tiers (frontend, backend, AI services)
   - Bottom: Infrastructure (monitoring, security, DevOps)
4. **Clear Connections**: Show data flow with labeled arrows
5. **Azure Branding**: Azure logo in top-right corner

### Professional Elements

- **Containers**: Use rounded rectangles with dashed borders for VNets/subnets
- **Service Icons**: Official Azure icons at consistent size
- **Labels**: Clear, concise service names below icons
- **Arrows**: Use orthogonal (right-angle) connectors, not diagonal
- **Colors**:
  - Containers: Light blue (#E1F5FF)
  - Future components: Red dashed borders (#E53935)
  - Standard borders: Dark gray (#333333)

### Example Architecture Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                                           [Azure Logo]       │
│                                                               │
│  [User] → [API Mgmt] → [Container Apps] → [AI Services]     │
│                             ↓                    ↓            │
│                        [Cosmos DB]          [Blob Storage]   │
│                                                               │
│  [DevOps]  [Key Vault]  [Monitor]  [App Insights]          │
└─────────────────────────────────────────────────────────────┘
```

## Service Naming Conventions

### Current Naming (2024-2026)

Microsoft has renamed several services. Use these current names:

| Old Name | Current Name | Icon Key |
|----------|--------------|----------|
| Azure Active Directory | Microsoft Entra ID | `entra-id` |
| Cognitive Search | Azure AI Search | `ai-search` |
| Form Recognizer | Azure AI Document Intelligence | `document-intelligence` |
| Cognitive Services | Azure AI Services | `cognitive-services` |

### Avoid Deprecated Names

Do not use these in new diagrams:
- ❌ Azure AD (use Microsoft Entra ID)
- ❌ Cognitive Search (use Azure AI Search)
- ❌ Form Recognizer (use Document Intelligence)
- ❌ Machine Learning Studio Classic (use Azure Machine Learning)

## Best Practices

### For Icon Updates

1. **Regular Updates**: Update icons monthly or when major Azure services launch
2. **Version Control**: Commit icon changes with clear messages
3. **Test After Update**: Verify diagram generation works after icon updates
4. **Document Changes**: Update metadata file when adding/removing services

### For Diagram Generation

1. **Use Current Services**: Check service status before including in diagrams
2. **Show Replacements**: For deprecated services, show migration path to replacement
3. **Consistent Naming**: Use official Microsoft service names
4. **Professional Layout**: Follow Microsoft's architecture diagram guidelines
5. **Include Branding**: Always include Azure logo

## Troubleshooting

### Icon Not Found

If an icon is missing:

1. Check if the service name is correct in `azure_services_metadata.json`
2. Verify the icon exists in `OptiStudio-client/src/assets/`
3. Update `localIconAssets.ts` mapping if needed
4. Run update script to fetch latest icons

### Deprecated Service Warning

If generating a diagram with deprecated services:

1. Check `azure_services_metadata.json` for replacement service
2. Update diagram to use current service
3. Add migration note if showing transition from old to new

### Draw.io Icon Not Rendering

If draw.io icons don't show:

1. Verify icon key exists in `AZURE_ICON_STYLES` dictionary
2. Check draw.io Azure2 library has the icon
3. Use fallback icon if specific icon unavailable
4. Update `drawio_client.py` mapping

## Contributing

When adding new Azure services:

1. Download official icon from Microsoft's repository
2. Save to appropriate category folder
3. Add entry to `azure_services_metadata.json`
4. Update `localIconAssets.ts` mapping
5. Update `drawio_client.py` if used in draw.io diagrams
6. Test diagram generation
7. Commit with descriptive message

## Resources

- [Microsoft Azure Architecture Icons](https://learn.microsoft.com/en-us/azure/architecture/icons/)
- [Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/)
- [Azure Icon GitHub Repository](https://github.com/microsoft/azure-icons)
- [Azure Naming Conventions](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/resource-naming)
- [Azure Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/)

## License

Microsoft Azure icons are provided by Microsoft and subject to their usage guidelines. Always include proper attribution when using in external-facing materials.

---

**Last Updated**: April 2026  
**Maintained By**: OptiStudio Development Team
