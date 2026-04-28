# Azure Services Quick Reference Card
**Last Updated**: April 2026 | **OptiStudio Presales Agent**

## 🟢 Current Azure Services (Use These)

### AI & Machine Learning
| Service | Icon Key | Use For |
|---------|----------|---------|
| Azure OpenAI | `openai`, `azure-openai` | GPT-4, GPT-3.5, Embeddings, DALL-E |
| Azure AI Search | `ai-search`, `search` | Cognitive search, RAG applications |
| Azure AI Document Intelligence | `document-intelligence` | Extract text from documents |
| Azure Machine Learning | `machine-learning`, `ml` | ML model training & deployment |
| Azure AI Services | `cognitive-services`, `ai-services` | Vision, Speech, Language APIs |
| Bot Services | `bot-service` | Conversational AI bots |

### Compute
| Service | Icon Key | Use For |
|---------|----------|---------|
| Azure App Service | `app-service`, `web-app` | Web apps, REST APIs |
| Azure Functions | `functions`, `function-app` | Serverless compute |
| Azure Container Apps | `container-apps` | Container hosting (serverless) |
| Azure Kubernetes Service (AKS) | `aks`, `kubernetes` | Container orchestration |
| Virtual Machines | `vm`, `virtual-machine` | IaaS compute |
| Static Web Apps | `static-web-app`, `static-app` | Static site hosting |

### Databases
| Service | Icon Key | Use For |
|---------|----------|---------|
| Azure Cosmos DB | `cosmos-db`, `cosmosdb` | NoSQL, multi-model database |
| Azure SQL Database | `sql-database`, `sql` | Managed SQL Server |
| Azure Database for MySQL | `mysql` | Managed MySQL |
| Azure Database for PostgreSQL | `postgresql` | Managed PostgreSQL |
| Azure Cache for Redis | `redis`, `cache-redis` | In-memory caching |

### Storage
| Service | Icon Key | Use For |
|---------|----------|---------|
| Azure Storage Account | `storage`, `storage-account`, `blob` | Blob, File, Queue, Table storage |
| Azure Data Lake Storage | `data-lake` | Big data analytics storage |

### Networking
| Service | Icon Key | Use For |
|---------|----------|---------|
| Azure Virtual Network | `vnet`, `virtual-network` | Network isolation |
| Azure API Management | `api-management`, `apim` | API gateway |
| Azure Application Gateway | `application-gateway` | Load balancer with WAF |
| Azure Front Door | `front-door` | Global CDN and load balancer |
| Azure Private Link | `private-link`, `private-endpoint` | Private connectivity |

### Security & Identity
| Service | Icon Key | Use For |
|---------|----------|---------|
| **Microsoft Entra ID** | `entra-id`, `entra` | Identity & access management |
| Azure Key Vault | `key-vault`, `keyvault` | Secrets, keys, certificates |
| Microsoft Defender for Cloud | `defender` | Cloud security posture |
| Microsoft Sentinel | `sentinel` | SIEM & SOAR |

### Monitoring & DevOps
| Service | Icon Key | Use For |
|---------|----------|---------|
| Azure Monitor | `monitor`, `azure-monitor` | Monitoring & alerting |
| Azure Application Insights | `application-insights`, `app-insights` | APM & diagnostics |
| Azure DevOps | `devops`, `azure-devops` | CI/CD pipelines |
| Azure Log Analytics | `log-analytics` | Log collection & analysis |

### Integration
| Service | Icon Key | Use For |
|---------|----------|---------|
| Azure Service Bus | `service-bus` | Enterprise messaging |
| Azure Event Hubs | `event-hub`, `event-hubs` | Big data streaming |
| Azure Event Grid | `event-grid` | Event-driven architectures |
| Azure Logic Apps | `logic-apps` | Workflow automation |

### Analytics
| Service | Icon Key | Use For |
|---------|----------|---------|
| Azure Synapse Analytics | `synapse`, `synapse-analytics` | Data warehousing & analytics |
| Azure Databricks | `databricks` | Apache Spark analytics |
| Azure Data Factory | `data-factory` | ETL/ELT orchestration |

---

## ⚠️ Deprecated Services (Use Replacements)

| Deprecated Service ❌ | Replacement ✅ | Icon Key | Since |
|----------------------|----------------|----------|-------|
| Azure Active Directory | **Microsoft Entra ID** | `entra-id` | July 2023 |
| Cognitive Search | **Azure AI Search** | `ai-search` | Nov 2023 |
| Form Recognizer | **Azure AI Document Intelligence** | `document-intelligence` | Jan 2024 |
| Cognitive Services | **Azure AI Services** | `ai-services` | 2024 |
| Machine Learning Studio Classic | **Azure Machine Learning** | `machine-learning` | Aug 2024 |

### Migration Notes

#### Azure AD → Microsoft Entra ID
- **Status**: Name change only, same service
- **Action**: Update all diagrams and documentation to use "Microsoft Entra ID"
- **Functionality**: Unchanged

#### Cognitive Search → Azure AI Search
- **Status**: Rebranded with enhanced AI capabilities
- **Action**: Use new name in all new diagrams
- **Functionality**: Enhanced with AI features

#### Form Recognizer → Document Intelligence
- **Status**: Rebranded with expanded capabilities
- **Action**: Use new name for all document processing
- **Functionality**: More document types supported

---

## 🚫 Discontinued Services (Do Not Use)

| Service | Discontinued | Alternative |
|---------|--------------|-------------|
| Azure Blockchain Service | Sept 2021 | Quorum Blockchain Service or partner solutions |
| Azure Blockchain Workbench | Sept 2021 | Custom development |
| Kinect DK | Oct 2023 | Azure Kinect Body Tracking SDK (limited) |
| Azure Internet Analyzer | Jan 2024 | Azure Monitor Network Insights |
| Microsoft Genomics | Sept 2024 | Partner genomics solutions |

---

## 🔵 Microsoft 365 Services (External Integration)

| Service | Icon Key | Use For |
|---------|----------|---------|
| Microsoft Teams | `teams`, `ms-teams` | Collaboration platform |
| Microsoft SharePoint | `sharepoint` | Document management |
| Microsoft Power BI | `power-bi` | Business intelligence |
| Microsoft Fabric | `microsoft-fabric` | Unified analytics platform |

---

## 🎨 Icon Usage Guidelines

### Quick Selection Guide

**For AI/ML Projects**:
- `azure-openai` - LLM capabilities
- `ai-search` - Semantic search
- `document-intelligence` - Document processing
- `machine-learning` - Custom ML models

**For Web Applications**:
- `app-service` - Web apps & APIs
- `functions` - Serverless functions
- `static-web-app` - Static sites
- `api-management` - API gateway

**For Data Storage**:
- `cosmos-db` - NoSQL (multi-model)
- `sql-database` - Relational data
- `storage` - Blobs, files, queues
- `cache-redis` - In-memory cache

**For Security**:
- `entra-id` - Identity (use this, not "Azure AD")
- `key-vault` - Secrets management
- `defender` - Cloud security
- `sentinel` - SIEM

**For Monitoring**:
- `monitor` - Metrics & alerts
- `application-insights` - APM
- `log-analytics` - Log analysis
- `devops` - CI/CD

---

## 💡 Pro Tips

### Always Use Current Names
✅ DO: "Microsoft Entra ID provides authentication..."  
❌ DON'T: "Azure AD provides authentication..."

### Check Service Status First
Before adding a service to a diagram:
1. Check `azure_services_metadata.json`
2. Verify status is "current"
3. Use official display name

### Icon Naming Patterns
- Hyphens, not spaces: `azure-openai`, not `azure openai`
- Lowercase: `cosmos-db`, not `Cosmos-DB`
- Abbreviations OK: `aks`, `acr`, `apim`

### Common Mistakes to Avoid
❌ Using `azure-ad` → ✅ Use `entra-id`  
❌ Using `cognitive-search` → ✅ Use `ai-search`  
❌ Using `form-recognizer` → ✅ Use `document-intelligence`  

---

## 📊 Architecture Patterns

### Standard Web App
```
User → [API Management] → [App Service] → [SQL Database]
                               ↓
                         [Blob Storage]
```

### AI-Powered Application
```
User → [API Management] → [Container Apps] → [Azure OpenAI]
                               ↓                    ↓
                         [Cosmos DB]          [AI Search]
```

### Microservices Architecture
```
[API Management] → [AKS] → [Service Bus]
                     ↓            ↓
                [Cosmos DB]  [Event Hub]
```

---

## 🔄 Monthly Update Checklist

- [ ] Run `update_azure_icons.py`
- [ ] Review `azure_services_metadata.json` for new services
- [ ] Check for deprecated services
- [ ] Update diagrams with new service names
- [ ] Test diagram generation

---

## 📞 Quick Commands

```bash
# Update icons
cd OptiStudio-agent
python scripts/update_azure_icons.py

# Force update
python scripts/update_azure_icons.py --force

# Check service status
code scripts/azure_services_metadata.json
```

---

**Print this page and keep it handy when creating architecture diagrams!**

**Remember**: Always use current service names and check metadata for status before using a service in diagrams.
