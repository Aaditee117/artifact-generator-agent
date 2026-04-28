"""
DEV-ONLY SCRIPT: One-off mutation tool to rewrite utils/prompts.py in-place.
Do NOT include in production builds or Docker images.
Move to scripts/ and exclude from releases.
"""
"""Replace ARCHITECTURE_ANALYSIS_PROMPT with strict column-based layout."""
import pathlib

PROMPTS_FILE = pathlib.Path(__file__).parent / "utils" / "prompts.py"

NEW_PROMPT = r'''ARCHITECTURE_ANALYSIS_PROMPT = """You are an expert Azure cloud solution architect. Generate a structured architecture diagram as a React Flow nodes+edges JSON with NESTED CONTAINER NODES (parent/child hierarchy).

PROJECT CONTEXT:
{context}

USER INSTRUCTIONS:
{instructions}

CLARIFICATION ANSWERS:
{answers}

---

## STRICT 5-COLUMN LAYOUT (EXACT COORDINATES — NO OVERLAP)

The canvas uses 5 fixed columns. Every node MUST be placed at its column's X coordinate.
Minimum vertical gap between nodes: 100px. Container children use RELATIVE positions.

### Column Map (each service node ≈ 120×80 px)

```
DECORATION (0,0)   Azure Logo — no handles, no edges
──────────────────────────────────────────────────────────────────────
Col 1 (x:50)   Col 2 (x:300)          Col 3 (x:600)           Col 4 (x:1100)   Col 5 (x:1350)
Identity        Compute Subnet         AI Foundry (400×500)    Private Link     Data Sources
                (container)            (container)             Subnet (narrow)

┌──────────┐   ┌──────────────────────────────────────────┐   ┌──────┐  ┌────────────┐
│ MS Teams  │   │       Virtual Network  (container)       │   │ PL   │  │ SharePoint │
│           │   │  ┌────────────┐  ┌──────────────────┐   │   │ Sub  │  │            │
│ Users     │──>│  │APIM Subnet │  │ AI Foundry       │   │──>│ net  │─>│ Cosmos DB  │
│           │   │  │            │  │                  │   │   │      │  │            │
│           │   │  │ [APIM]     │  │ [Brain: Agent]   │   │   │ [PE] │  │ Blob Store │
│           │   │  │ [Container │  │ [Models]  [Tool] │   │   │ [PE] │  │            │
│           │   │  │  App]      │  │ [Tool]    [Tool] │   │   │      │  │ SQL DB     │
│           │   │  │ [Entra ID] │  └──────────────────┘   │   │      │  │            │
│           │   │  └────────────┘                         │   │      │  │            │
│           │   └──────────────────────────────────────────┘   └──────┘  └────────────┘
──────────────────────────────────────────────────────────────────────
FOOTER ROW (y:800): [DevOps x:300] [Key Vault x:500] [Monitor x:700] [App Insights x:900]
```

---

## COLUMN COORDINATES (ABSOLUTE — MANDATORY)

### Decoration Node
| id | label | azureType | nodeType | x | y |
|----|-------|-----------|----------|---|---|
| decoration | Microsoft Azure | azure | decoration | 0 | 0 |

### Column 1 — Identity (x: 50, top-level, no parentNode)
Stack vertically: y=100, y=220.
| Node       | azureType |
|------------|-----------|
| MS Teams   | ms-teams  |
| Users      | user      |

### Column 2 — Core Compute (x: 300)
**Virtual Network** container: x=300, y=70, width=700, height=550.
Inside VNet, two sub-containers side by side:

**APIM Subnet** (parentNode=vnet, x=20, y=40, width=220, height=440):
  Children stacked vertically (RELATIVE to subnet, x=30, starting y=50, gap=120):
  - API Management        x=30, y=50
  - Container App         x=30, y=170
  - Entra ID              x=30, y=290

**AI Foundry** (parentNode=vnet, x=270, y=40, width=400, height=500):
  Left column (x=30) for brain + models. Right column (x=210) for tools.
  All positions RELATIVE to AI Foundry:
  - Brain (Foundry Agent): x=30,  y=60
  - Foundry Models:        x=30,  y=200
  - Tool 1:                x=210, y=60
  - Tool 2:                x=210, y=200
  - Tool 3:                x=210, y=340

  AI Foundry height = max(N_tools × 130 + 80, 500) where N = number of tools.

### Column 4 — Connectivity (x: 1100)
**Private Link Subnet** container: x=1100, y=70, width=120, height=550, parentNode=null.
Stack Private Endpoint nodes vertically (RELATIVE, x=15, y=50, gap=110).

### Column 5 — Data Sources (x: 1350, top-level, no parentNode)
Stack vertically: y=100, y=230, y=360, y=490.
| Node         | azureType    |
|--------------|--------------|
| SharePoint   | sharepoint   |
| Cosmos DB    | cosmos-db    |
| Blob Storage | blob-storage |
| SQL Database | sql-database |

### Footer Row — Platform & Monitoring (y: 800)
Top-level service nodes, NO container. All at y=800:
| Node              | azureType            | x   |
|-------------------|----------------------|-----|
| Azure DevOps      | devops               | 300 |
| Key Vault         | key-vault            | 500 |
| Azure Monitor     | monitor              | 700 |
| Application Insights | application-insights | 900 |

---

## JSON OUTPUT FORMAT (STRICT)

Return ONLY valid JSON:

{{
  "project_name": "Project Name",
  "architecture_style": "microservices|serverless|hybrid",
  "groups": [],
  "nodes": [
    {{
      "id": "unique-id",
      "label": "Short Label (1-3 words)",
      "azureType": "service-type-key",
      "nodeType": "container|service|brain|future|decoration",
      "parentNode": null,
      "position": {{ "x": 0, "y": 0 }},
      "isFuture": false,
      "tooltip": "Brief description of this component",
      "width": null,
      "height": null,
      "containerStyle": null
    }}
  ],
  "edges": [
    {{
      "source": "source-node-id",
      "target": "target-node-id",
      "label": "",
      "isFuture": false
    }}
  ]
}}

### Node Fields
| Field          | Required | Description |
|----------------|----------|-------------|
| id             | Yes | Unique string ID |
| label          | Yes | Short display name (1-3 words) |
| azureType      | Yes | Service key for icon mapping |
| nodeType       | Yes | "container", "service", "brain", "future", or "decoration" |
| parentNode     | No  | ID of parent container (null for top-level) |
| position       | Yes | RELATIVE to parent if parentNode set, ABSOLUTE otherwise |
| isFuture       | Yes | true for planned/future components |
| tooltip        | Yes | Brief description |
| width          | Container only | Width in pixels |
| height         | Container only | Height in pixels |
| containerStyle | Container only | {{ "backgroundColor": "rgba(...)", "borderColor": "#hex", "borderStyle": "dashed" or "solid" }} |

---

## AZURE TYPE KEYS (azureType values)

**Compute**: `app-service`, `functions`, `container-apps`, `aks`, `virtual-machines`, `batch`
**Integration**: `api-management`, `logic-apps`, `service-bus`, `event-grid`, `event-hub`, `data-factory`
**AI/ML**: `openai`, `ai-search`, `machine-learning`, `cognitive-services`, `bot-service`, `ai-foundry`
**Data**: `cosmos-db`, `sql-database`, `blob-storage`, `data-lake`, `synapse`, `redis`, `databricks`
**Networking**: `virtual-network`, `subnet`, `application-gateway`, `cdn`, `private-endpoint`, `load-balancer`, `front-door`
**Security**: `entra-id`, `key-vault`, `defender`, `sentinel`
**Monitoring**: `monitor`, `application-insights`, `log-analytics`, `devops`
**External**: `user`, `ms-teams`, `sharepoint`, `power-bi`, `microsoft-fabric`

---

## NODE ORDERING (CRITICAL for React Flow rendering)

Container nodes MUST appear BEFORE their children in the array. Strict order:
1. Decoration node (Azure logo)
2. Outermost containers (VNet, Private Link Subnet)
3. Nested containers (APIM Subnet, AI Foundry — parentNode = VNet)
4. Service/brain/future nodes inside containers
5. Top-level service nodes (Col 1 identity, Col 5 data sources, footer row)

---

## EDGE RULES

- All edges use `type: "smoothstep"` — right-angle circuit-board routing
- Arrow marker on target end
- Standard: solid, color #424242
- Future: dashed, color #E53935, isFuture: true
- Short labels (1-3 words) or empty string
- Max 15 edges — only PRIMARY data flows
- Do NOT draw edges from/to decoration node or footer nodes
- Do NOT draw diagonal edges — smoothstep handles routing

---

## MANDATORY COMPONENTS

Always include:
- **Decoration** node (Azure logo) at (0, 0)
- **Entra ID** for auth (inside APIM Subnet)
- **API Management** if frontend calls backend (inside APIM Subnet)
- **Footer row** with exactly 4 nodes: Azure DevOps, Key Vault, Azure Monitor, App Insights

---

## CRITICAL RULES

1. Container nodes MUST have `width`, `height`, and `containerStyle`
2. Service/brain/future/decoration nodes MUST NOT have `width`/`height`
3. Every `parentNode` MUST match an existing container node's `id`
4. Every edge source/target MUST match an existing node `id`
5. All positions must be positive integers — no nulls, no negative values
6. The "brain" node is the main orchestrator — place prominently inside AI Foundry
7. Mark speculative/planned components as `nodeType: "future"` and `isFuture: true`
8. AI Foundry height = max(N_tools × 130 + 80, 500)
9. Generate 10-20 service nodes plus containers
10. Return ONLY valid JSON — no markdown, no code fences, no comments
11. NO two service nodes may share the same absolute (x, y) position
12. Minimum 100px vertical gap between sibling nodes in the same container
13. Footer nodes are top-level (no container) — all at y=800
14. Children inside containers use RELATIVE positions (to the parent container)
"""'''

src = PROMPTS_FILE.read_text(encoding="utf-8")

# Find the start and end of ARCHITECTURE_ANALYSIS_PROMPT
start_marker = 'ARCHITECTURE_ANALYSIS_PROMPT = """'
end_marker = '"""\n\nARCHITECTURE_GRAPH_PROMPT'

start_idx = src.index(start_marker)
end_idx = src.index(end_marker) + 3  # include the closing """

# Replace the old prompt with the new strict column-based layout prompt
new_src = src[:start_idx] + NEW_PROMPT + src[end_idx:]
# Overwrite the prompts.py file with the updated content
PROMPTS_FILE.write_text(new_src, encoding="utf-8")
print(f"✅ Prompt replaced. New file size: {len(new_src)} chars")
# Verify
new_src2 = PROMPTS_FILE.read_text(encoding="utf-8")
assert "STRICT 5-COLUMN LAYOUT" in new_src2, "Column layout not found!"
assert "Col 1 (x:50)" in new_src2, "Col 1 reference not found!"
assert "ARCHITECTURE_GRAPH_PROMPT = ARCHITECTURE_ANALYSIS_PROMPT" in new_src2, "Alias lost!"
print("✅ All verification checks passed")
