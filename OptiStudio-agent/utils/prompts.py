"""Detailed prompts for LLM analysis, DALL-E generation, and PPT content.

Supports phase-based artifact generation:
- POC (Proof of Concept): Minimal architecture for technical validation
- MVP (Minimum Viable Product): Production-ready architecture for launch
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE TYPE CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

PHASE_TYPE_POC = "poc"
PHASE_TYPE_MVP = "mvp"
PHASE_TYPE_BOTH = "both"

# Phase characteristics for use in prompts
PHASE_CHARACTERISTICS = {
    PHASE_TYPE_POC: {
        "name": "POC (Proof of Concept)",
        "description": "Technical feasibility validation",
        "duration": "1-3 months",
        "architecture_style": "Minimal, single-instance, basic tiers",
        "services": "Free/Basic tiers, minimal redundancy, LRS storage",
        "focus": "Prove technical feasibility with minimal investment",
        "excludes": "HA, monitoring, security hardening, DevOps automation",
    },
    PHASE_TYPE_MVP: {
        "name": "MVP (Minimum Viable Product)",
        "description": "Production-ready for initial launch",
        "duration": "3-6 months ongoing",
        "architecture_style": "Production-ready, multi-instance, standard tiers",
        "services": "Standard tiers, GRS storage, HA configurations",
        "focus": "Launch-ready with security, monitoring, and scalability",
        "includes": "Key Vault, App Insights, multi-region, auto-scaling",
    },
}


def get_phase_context(phase_type: str) -> str:
    """Get phase-specific context to inject into prompts."""
    if phase_type.lower() not in PHASE_CHARACTERISTICS:
        return ""

    phase = PHASE_CHARACTERISTICS[phase_type.lower()]
    return f"""
## PHASE TYPE: {phase['name']}

**Phase Characteristics:**
- Description: {phase['description']}
- Duration: {phase['duration']}
- Architecture Style: {phase['architecture_style']}
- Azure Services: {phase['services']}
- Focus: {phase['focus']}
"""


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE SELECTION PROMPT (shown after artifact upload)
# ═══════════════════════════════════════════════════════════════════════════════

PHASE_SELECTION_PROMPT = """Based on the project artifacts you've uploaded, I can generate deliverables for your project.

**Please select the phase type for your deliverables:**

🔬 **POC (Proof of Concept)**
   - Minimal architecture for technical validation
   - Free/Basic Azure tiers
   - 1-3 month duration
   - Ideal for: Demos, internal testing, concept validation

🚀 **MVP (Minimum Viable Product)**
   - Production-ready architecture for launch
   - Standard Azure tiers with HA
   - Includes security & monitoring
   - Ideal for: Client demos, initial production launch

**Deliverables that will be generated:**
- 📊 Architecture Diagram (tailored for your phase)
- 📈 Data Flow Diagrams (DFD Level 0 & Level 1)
- 📑 Presales Presentation (PPT)
- 💰 Azure Cost Report

Please select: **POC** or **MVP**
"""


# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM PROMPT
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """You are OptiStudio Presales Agent — an expert solution architect at Optimus Information Inc.
Your job is to analyze uploaded project artifacts (documents, meeting transcripts, email threads, PM instructions)
and generate professional presales deliverables.

When analyzing artifacts, extract:
- Project name and client name
- Business problem and objectives
- Functional and non-functional requirements
- Technology stack preferences
- Integration points with external systems
- Data entities and data flows
- User roles and access patterns
- Deployment and infrastructure requirements
- Timeline and budget constraints

Always be thorough and precise. If critical information is missing, list specific questions to ask."""


CLARIFICATION_PROMPT = """Based on the uploaded artifacts, analyze the content and determine what information
is missing to generate a high-quality {artifact_type}.

Return a JSON object with:
{{
  "project_summary": "Brief summary of what you understood from the artifacts",
  "questions": [
    {{
      "id": "q1",
      "question": "The specific question",
      "why": "Why this information is needed",
      "default": "What you would assume if not answered"
    }}
  ]
}}

If you have enough information, return an empty questions array.
Maximum 5 questions. Focus on the most critical gaps only."""


COST_REPORT_CLARIFICATION_PROMPT = """You are an Azure Cloud Cost Estimator. Analyze the uploaded artifacts and determine what information is missing to produce an accurate Azure Pricing Calculator-style cost report.

The cost report will have these exact columns:
| Service category | Service type | Custom name | Region | Description | Estimated monthly cost | Estimated upfront cost |

The "Description" field must be extremely verbose — matching the Azure Pricing Calculator export format (e.g., "Flex Consumption tier, 2048 MB Instance memory size, 3,499 x10 On demand executions per month, 100 Active on demand executions seconds per instance, 1 Active on demand instances").

Ask clarifying questions ONLY about gaps that significantly affect cost estimation. Focus on:
- Expected user load / traffic / requests per month
- Preferred Azure region (default: Canada Central)
- Phase type: POC (free/basic tiers) vs MVP (standard/production tiers) vs Both
- AI model usage: which models, expected token volumes
- Storage needs: data volume, redundancy level
- Database choice and expected throughput (RU/s for Cosmos, DTU for SQL)
- Any specific services the client wants or wants to avoid

Return a JSON object with:
{{
  "project_summary": "Brief summary of the project and its Azure needs based on artifacts",
  "questions": [
    {{
      "id": "q1",
      "question": "The specific question",
      "why": "Why this information is needed for accurate cost estimation",
      "default": "What you would assume if not answered"
    }}
  ]
}}

If you have enough information, return an empty questions array.
Maximum 6 questions. Focus on questions whose answers most affect cost."""


# ═══════════════════════════════════════════════════════════════════════════════
# ARCHITECTURE PROMPTS (Professional Azure Diagram Style)
# ═══════════════════════════════════════════════════════════════════════════════

ARCHITECTURE_ANALYSIS_PROMPT = """You are an expert Azure cloud solution architect. Generate a structured architecture diagram as a React Flow nodes+edges JSON with NESTED CONTAINER NODES (parent/child hierarchy).

IMPORTANT: This is NOT a Data Flow Diagram (DFD) or process flow. Do NOT include any generic "process", "step", "data flow", or similar nodes. Only include Azure infrastructure, services, components, and containers. Every node must represent a real Azure service, resource, or architectural component. Do NOT include any nodes that represent business logic, generic processes, or data movement steps. No DFD/process/flowchart elements are allowed.

PROJECT CONTEXT:
{context}

USER INSTRUCTIONS:
{instructions}

CLARIFICATION ANSWERS:
{answers}

---

## STRICT 5-COLUMN LAYOUT (VISUAL ALIGNMENT)

The canvas uses 5 horizontal zones. Containers and nodes MUST follow these X-coordinates.
Vertical gaps between sibling nodes: 110px. 
IMPORTANT: Children inside containers use RELATIVE (x, y) coordinates.

### Column Map
1. **Col 1 (x: 50):** Entry Point (User, MS Teams, Azure Bot)
2. **Col 2 (x: 350):** Compute/VNet Zone (APIM Subnet, Container App Subnet)
3. **Col 3 (x: 750):** Intelligence Zone (AI Foundry / Agent Container)
4. **Col 4 (x: 1100):** Connectivity (Private Link Subnet / Hub)
5. **Col 5 (x: 1400):** External Data (SharePoint, Fabric, Cosmos, SQL)

---

## NODE HIERARCHY & COORDINATES

### 1. Decoration & Footer (Absolute)
- **Azure Logo:** id: 'decoration', x: 0, y: 0
- **Footer Row:** y: 850. [DevOps x:300], [KeyVault x:500], [Monitor x:700], [AppInsights x:900]

### 2. Main Virtual Network (x:300, y:50, w:950, h:750)
Inside the VNet (parentNode: 'vnet'), place:
- **APIM Subnet:** (x:20, y:50, w:250, h:150) -> Child: [API Management]
- **Container App Subnet:** (x:320, y:50, w:250, h:200) -> Child: [Azure Container App]
- **AI Foundry Container:** (x:20, y:300, w:550, h:400) 
    - **Foundry Agent (Brain):** (x:30, y:50, w:250, h:300)
    - **Tool Nodes:** Stacked at x:350, y:50, 160, 270 (e.g., SharePoint Tool, MS Fabric Tool).
- **Private Link Subnet:** (x:650, y:50, w:180, h:650)
    - **Private Endpoints:** Stacked vertically at x:40, starting y:60.

### 3. Data Sources (x:1400)
Container "Data Sources" (x:1400, y:200, w:250, h:600).
- Vertically stack: SharePoint, MS Fabric, Cosmos DB, SQL DB.

---

```
DECORATION (0,0)   Azure Logo — no handles, no edges
──────────────────────────────────────────────────────────────────────

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
"""

ARCHITECTURE_GRAPH_PROMPT = ARCHITECTURE_ANALYSIS_PROMPT  # Alias for clarity



DFD_ANALYSIS_PROMPT = """Analyze the following project context and generate a unified React Flow graph specification for a Data Flow Diagram (DFD).

PROJECT CONTEXT:
{context}

USER INSTRUCTIONS:
{instructions}

CLARIFICATION ANSWERS:
{answers}

---

## LAYOUT & COMPLEXITY RULES

- The DFD MUST use a TOP-TO-BOTTOM (vertical) layout: nodes are stacked vertically, with data flowing from top to bottom.
- All node positions must increase in the Y direction for each level (parent above child, source above target).
- Minimize horizontal spread; keep X coordinates similar for all nodes unless grouping is needed.
- The diagram MUST be SIMPLE: limit to 3-6 nodes and 2-5 edges total. Only include the most essential entities, processes, and data stores.
- Do NOT generate more than 2 external entities, 2 processes, and 2 data stores unless absolutely necessary.
- Only primary data flows should be shown (no secondary/optional flows).
- Avoid cross-links and cycles; keep the diagram linear and easy to read.

---

You MUST output a JSON object representing the DFD graph containing "groups", "nodes", and "edges".
This replaces both level 0 and level 1 with a single structured view.

Return JSON in this EXACT format:
{{
  "project_name": "Name of the project",
  "groups": [
    {{
      "id": "external",
      "label": "External Entities",
      "color": "#FAFAFA"
    }},
    {{
      "id": "processes",
      "label": "System Processes",
      "color": "#E8F5E9"
    }},
    {{
      "id": "stores",
      "label": "Data Stores",
      "color": "#F3E5F5"
    }}
  ],
  "nodes": [
    {{
      "id": "e1",
      "label": "Customer",
      "group": "external",
      "icon": "user",
      "tooltip": "End user of the system",
      "position": {{"x": 300, "y": 100}}
    }},
    {{
      "id": "p1",
      "label": "User Authentication",
      "group": "processes",
      "icon": "functions",
      "tooltip": "Validates credentials",
      "position": {{"x": 300, "y": 250}}
    }},
    {{
      "id": "d1",
      "label": "Accounts DB",
      "group": "stores",
      "icon": "sql-database",
      "tooltip": "Stores user profiles",
      "position": {{"x": 300, "y": 400}}
    }}
  ],
  "edges": [
    {{
      "source": "e1",
      "target": "p1",
      "label": "Login Credentials"
    }},
    {{
      "source": "p1",
      "target": "d1",
      "label": "Verify Request"
    }}
  ]
}}"""


DALLE_DFD_PROMPT = """Create a highly detailed, clean, and professional Data Flow Diagram (DFD) {level_label} for a system called "{project_name}".

VISUAL STYLE:
- White background, clean technical drawing style
- Use standard DFD notation:
  - RECTANGLES for external entities (light blue fill)
  - ROUNDED RECTANGLES / CIRCLES for processes (light green fill, numbered)
  - OPEN-ENDED RECTANGLES (parallel lines) for data stores (light yellow fill)
  - LABELED ARROWS for data flows (black thin arrows with text labels)
- Arrange in a clear, non-overlapping layout
- Every element must be clearly labeled

{level_specific_content}

IMPORTANT RULES:
- Use standard DFD notation exactly as described above
- Every arrow MUST have a label describing the data
- The diagram must be readable at 1024x1024 resolution
- Make it look like a textbook-quality DFD, NOT an artistic illustration
- Include a title at the top: "{project_name} — DFD {level_label}"
- Include a notation legend in the bottom-right"""


PPT_CONTENT_PROMPT = """Based on the following project context, generate professional presales presentation content.

PROJECT CONTEXT:
{context}

USER INSTRUCTIONS:
{instructions}

CLARIFICATION ANSWERS:
{answers}

Generate a JSON response with content for each slide:
{{
  "title_slide": {{
    "title": "Project name — Presales Proposal",
    "subtitle": "Prepared by Optimus Information Inc.",
    "client": "Client name",
    "date": "Month Year"
  }},
  "executive_summary": {{
    "title": "Executive Summary",
    "points": ["Point 1", "Point 2", "Point 3", "Point 4"]
  }},
  "problem_statement": {{
    "title": "Problem Statement",
    "points": ["Problem 1", "Problem 2", "Problem 3"]
  }},
  "proposed_solution": {{
    "title": "Proposed Solution",
    "points": ["Solution aspect 1", "Solution aspect 2", "Solution aspect 3", "Solution aspect 4"]
  }},
  "architecture": {{
    "title": "Solution Architecture",
    "description": "Brief description of the architecture approach"
  }},
  "data_flow": {{
    "title": "Data Flow",
    "description": "Brief description of how data moves through the system"
  }},
  "tech_stack": {{
    "title": "Technology Stack",
    "categories": {{
      "Frontend": ["Tech 1", "Tech 2"],
      "Backend": ["Tech 1", "Tech 2"],
      "Database": ["Tech 1"],
      "Cloud": ["Azure service 1", "Azure service 2"],
      "DevOps": ["Tool 1", "Tool 2"]
    }}
  }},
  "timeline": {{
    "title": "Timeline & Milestones",
    "phases": [
      {{"phase": "Phase 1: Discovery", "duration": "2 weeks", "deliverables": "Requirements doc, Architecture design"}},
      {{"phase": "Phase 2: Development", "duration": "8 weeks", "deliverables": "Core features, API integration"}},
      {{"phase": "Phase 3: Testing", "duration": "2 weeks", "deliverables": "QA, UAT, Performance testing"}},
      {{"phase": "Phase 4: Deployment", "duration": "1 week", "deliverables": "Production deployment, Monitoring"}}
    ]
  }},
  "cost_estimate": {{
    "title": "Cost Estimate",
    "note": "Detailed cost breakdown will be provided after requirements finalization.",
    "categories": [
      {{"item": "Development Team", "estimate": "TBD"}},
      {{"item": "Azure Infrastructure (Monthly)", "estimate": "TBD"}},
      {{"item": "Licensing", "estimate": "TBD"}}
    ]
  }},
  "next_steps": {{
    "title": "Next Steps",
    "steps": ["Step 1", "Step 2", "Step 3", "Step 4"]
  }}
}}"""


MERMAID_DFD_L0_TEMPLATE = """flowchart TD
    classDef external fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e3a5f
    classDef system fill:#dcfce7,stroke:#16a34a,stroke-width:3px,color:#14532d

{entities}

    SYSTEM["{system_name}"]:::system

{flows}"""


MERMAID_DFD_L1_TEMPLATE = """flowchart TD
    classDef external fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e3a5f
    classDef process fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#14532d
    classDef datastore fill:#fef9c3,stroke:#ca8a04,stroke-width:2px,color:#713f12

{entities}

{processes}

{stores}

{flows}"""


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE-AWARE PPT PROMPT
# ═══════════════════════════════════════════════════════════════════════════════

PPT_CONTENT_PROMPT_POC = """Based on the following project context, generate professional POC (Proof of Concept) presales presentation content.

PROJECT CONTEXT:
{context}

USER INSTRUCTIONS:
{instructions}

CLARIFICATION ANSWERS:
{answers}

**PHASE: POC (Proof of Concept)**
- Focus on: Technical feasibility validation
- Timeline: 1-3 months
- Architecture: Minimal, basic tiers, single instances
- Exclude: Production security, HA, extensive monitoring

Generate a JSON response with content for each slide. The presentation should follow this structure:

1. Title Slide
2. Our Understanding (3 sections: Our Understanding, Current Challenges, AI Opportunity)
3. Objective - Clear, polished 3-4 bullet points focused on POC goals
4. Scope - What's included in the POC
5. High Level Design - POC Architecture overview (will use generated architecture diagram image)
6. Prerequisite - What's needed before starting the POC
7. Definition of Done - POC success criteria with bold section headers
8. Out Of Scope - What's explicitly excluded from POC
9. Timelines & Effort - POC timeline (1-3 months)
10. Timelines & Cost - POC cost breakdown (basic/free tiers)
11. Next Steps - Immediate action items

**CRITICAL FORMATTING RULES:**
1. Our Understanding MUST have 3 sections:
   - Section 1: "Our Understanding" (what we understand about the project)
   - Section 2: "Current Challenges" (problems faced)
   - Section 3: "AI Opportunity" (how AI solves it)
   Each section header should be bold, followed by 2-3 points.

2. Objective: 3-4 polished, concise POC-focused bullet points. NO "Problem Statement" prefix.

3. Prerequisites: Use format "CATEGORY: description" where CATEGORY is bold (e.g., "Azure Environment Access: Contributor access to Azure subscription...")

4. Definition of Done: Use format "SECTION: description" where SECTION is bold (e.g., "Technical Validation: Feasibility proven with demo...")

5. Out of Scope: Direct bullet points, NO section headers. Must include production concerns (HA, security hardening, monitoring).

6. Timeline & Effort: Simple phase list with "Phase Name — Duration" format (keep short, 1-3 months total)

7. Timeline & Cost: Basic/free tier Azure services only

8. Next Steps: Direct POC action items — kickoff, demos, evaluation, go/no-go decision

Return JSON:
{{
  "title_slide": {{
    "title": "Project name — POC Proposal",
    "client": "Client name",
    "date": "Month Year"
  }},
  "our_understanding": {{
    "sections": [
      {{
        "header": "Our Understanding",
        "points": ["We understand point 1", "We understand point 2"]
      }},
      {{
        "header": "Current Challenges",
        "points": ["Challenge 1", "Challenge 2"]
      }},
      {{
        "header": "AI Opportunity",
        "points": ["Opportunity 1", "Opportunity 2"]
      }}
    ]
  }},
  "objective": {{
    "points": ["Validate core technical assumptions", "Demonstrate key integrations", "Prove architecture viability", "Identify risks early"]
  }},
  "scope": {{
    "points": ["POC scope item 1", "POC scope item 2", "POC scope item 3"]
  }},
  "high_level_design": {{
    "note": "POC Architecture diagram will be auto-inserted"
  }},
  "prerequisites": {{
    "items": [
      {{"category": "Azure Environment Access", "description": "Azure subscription with required quotas"}},
      {{"category": "Development Environment", "description": "Local dev environment ready"}},
      {{"category": "Credentials & Access", "description": "Core dependencies and access credentials available"}}
    ]
  }},
  "definition_of_done": {{
    "items": [
      {{"section": "Technical Validation", "description": "Feasibility proven with a working demo"}},
      {{"section": "Integration Verification", "description": "Core integrations tested and functional"}},
      {{"section": "Risk Assessment", "description": "Risks identified, documented, and presented"}}
    ]
  }},
  "out_of_scope": {{
    "points": ["Production security hardening", "High availability and redundancy", "Extensive monitoring and alerting", "Full documentation and handover"]
  }},
  "timeline_cost": {{
    "phases": [
      {{"phase": "Week 1-2: Setup & Core Development", "duration": "2 weeks"}},
      {{"phase": "Week 3-4: Integration & Testing", "duration": "2 weeks"}},
      {{"phase": "Week 5-6: Demo & Evaluation", "duration": "2 weeks"}}
    ]
  }},
  "cost_estimate": {{
    "items": [
      {{"service": "Azure OpenAI (Basic usage)", "cost": "~$15/mo"}},
      {{"service": "Azure Infrastructure (Basic tiers)", "cost": "See POC Cost Report"}},
      {{"service": "Development Team", "cost": "Based on timeline"}}
    ]
  }},
  "next_steps": {{
    "steps": ["POC Kickoff meeting", "Weekly progress demos", "POC evaluation and go/no-go decision", "MVP planning (if successful)"]
  }}
}}"""


PPT_CONTENT_PROMPT_MVP = """Based on the following project context, generate professional MVP (Minimum Viable Product) presales presentation content.

PROJECT CONTEXT:
{context}

USER INSTRUCTIONS:
{instructions}

CLARIFICATION ANSWERS:
{answers}

**PHASE: MVP (Minimum Viable Product)**
- Focus on: Production-ready initial launch
- Timeline: 3-6 months
- Architecture: Full production architecture with HA
- Include: Security, monitoring, DevOps, scalability

Generate a JSON response with content for each slide. The presentation should follow this structure:

1. Title Slide
2. Our Understanding (3 sections: Our Understanding, Current Challenges, AI Opportunity)
3. Objective - Clear, polished 3-4 bullet points
4. Scope - What's included in the project
5. High Level Design - Architecture overview (will use generated architecture diagram image)
6. Prerequisite - What's needed before starting
7. Definition of Done - Success criteria with bold section headers
8. Out Of Scope - What's explicitly excluded
9. Timelines & Effort - Project timeline
10. Timelines & Cost - Cost breakdown
11. Next Steps - Immediate action items

**CRITICAL FORMATTING RULES:**
1. Our Understanding MUST have 3 sections:
   - Section 1: "Our Understanding" (what we understand about the project)
   - Section 2: "Current Challenges" (problems faced)
   - Section 3: "AI Opportunity" (how AI solves it)
   Each section header should be bold, followed by 2-3 points.

2. Objective: 3-4 polished, concise bullet points only. NO "Problem Statement" prefix.

3. Prerequisites: Use format "CATEGORY: description" where CATEGORY is bold (e.g., "Azure Environment Access: Contributor access to Azure subscription with OpenAI quota approved...")

4. Definition of Done: Use format "SECTION: description" where SECTION is bold (e.g., "Documentation & Stakeholder Sign-off: Architecture docs delivered and demo approved...")

5. Out of Scope: Direct bullet points, NO section headers.

6. Timeline & Effort: Simple phase list with "Phase Name — Duration" format

7. Timeline & Cost: Standard/production tier Azure services

8. Next Steps: Direct action items — contract, kickoff, sprint planning, development start

Return JSON:
{{
  "title_slide": {{
    "title": "Project name — MVP Proposal",
    "client": "Client name",
    "date": "Month Year"
  }},
  "our_understanding": {{
    "sections": [
      {{
        "header": "Our Understanding",
        "points": ["We understand point 1", "We understand point 2"]
      }},
      {{
        "header": "Current Challenges",
        "points": ["Challenge 1", "Challenge 2"]
      }},
      {{
        "header": "AI Opportunity",
        "points": ["Opportunity 1", "Opportunity 2"]
      }}
    ]
  }},
  "objective": {{
    "points": ["Polished MVP objective 1", "Polished MVP objective 2", "Polished MVP objective 3"]
  }},
  "scope": {{
    "points": ["MVP scope item 1", "MVP scope item 2", "MVP scope item 3", "MVP scope item 4"]
  }},
  "high_level_design": {{
    "note": "MVP Architecture diagram will be auto-inserted"
  }},
  "prerequisites": {{
    "items": [
      {{"category": "Azure Environment Access", "description": "Azure subscription with OpenAI quota approved"}},
      {{"category": "DevOps Setup", "description": "Pipeline and branching strategy defined"}},
      {{"category": "Security & Compliance", "description": "Security review and compliance requirements confirmed"}},
      {{"category": "Stakeholder Sign-off", "description": "Requirements reviewed and approved"}}
    ]
  }},
  "definition_of_done": {{
    "items": [
      {{"section": "Development Completion", "description": "All core features implemented and unit tested"}},
      {{"section": "Quality Assurance", "description": "Integration and E2E tests passing, security review addressed"}},
      {{"section": "Documentation & Stakeholder Sign-off", "description": "Architecture docs delivered, UAT sign-off obtained"}},
      {{"section": "Production Readiness", "description": "Monitoring, security, and deployment validated"}}
    ]
  }},
  "out_of_scope": {{
    "points": ["Mobile application development", "Legacy system migration", "Third-party CRM / ERP integration", "Multi-region active-active deployment"]
  }},
  "timeline_cost": {{
    "phases": [
      {{"phase": "Phase 1: Discovery & Design", "duration": "2-3 weeks"}},
      {{"phase": "Phase 2: Development Sprint 1-3", "duration": "6-8 weeks"}},
      {{"phase": "Phase 3: QA & Security", "duration": "2-3 weeks"}},
      {{"phase": "Phase 4: Launch", "duration": "1-2 weeks"}}
    ]
  }},
  "cost_estimate": {{
    "items": [
      {{"service": "Development Team", "cost": "Based on timeline"}},
      {{"service": "Azure Infrastructure (Monthly)", "cost": "See detailed cost report"}},
      {{"service": "Licensing & Tools", "cost": "TBD"}}
    ]
  }},
  "next_steps": {{
    "steps": ["Contract finalization", "Kickoff meeting and sprint planning", "Development start", "Weekly progress reviews"]
  }}
}}"""


def get_ppt_prompt(phase_type: str) -> str:
    """Get the appropriate PPT prompt based on phase selection."""
    if phase_type.lower() == PHASE_TYPE_POC:
        return PPT_CONTENT_PROMPT_POC
    elif phase_type.lower() == PHASE_TYPE_MVP:
        return PPT_CONTENT_PROMPT_MVP
    else:
        return PPT_CONTENT_PROMPT  # Default/legacy prompt


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE-AWARE ARCHITECTURE PROMPT
# ═══════════════════════════════════════════════════════════════════════════════

ARCHITECTURE_ANALYSIS_PROMPT_POC = ARCHITECTURE_ANALYSIS_PROMPT + """

**PHASE: POC (Proof of Concept)**
Design a MINIMAL architecture suitable for POC:
- Use FREE/BASIC tier Azure services only
- Single instances (no HA/redundancy)
- Skip production concerns (Key Vault, App Insights, etc.)
- Focus on core functionality validation
- Simpler, fewer components

POC SERVICE TIER MAPPINGS:
| Service | Use This Tier |
|---------|---------------|
| App Service | B1 Basic |
| Azure OpenAI | Pay-as-you-go minimal |
| Storage | LRS (not GRS) |
| Cosmos DB | Serverless |
| AI Search | Free tier |
"""


ARCHITECTURE_ANALYSIS_PROMPT_MVP = ARCHITECTURE_ANALYSIS_PROMPT + """

**PHASE: MVP (Minimum Viable Product)**
Design a PRODUCTION-READY architecture suitable for MVP launch:
- Use STANDARD tier Azure services
- Include high availability (2+ instances)
- MUST include: Key Vault, Application Insights
- Include security layer (Entra ID, API Management)
- Design for scalability

MVP SERVICE TIER MAPPINGS:
| Service | Use This Tier |
|---------|---------------|
| App Service | S1/P1 Standard |
| Azure OpenAI | Pay-as-you-go production |
| Storage | GRS redundancy |
| Cosmos DB | Provisioned throughput |
| AI Search | Basic/Standard |
| Security | Key Vault, Entra ID |
| Monitoring | Application Insights |
"""


def get_architecture_prompt(phase_type: str) -> str:
    """Get the appropriate architecture prompt based on phase selection."""
    if phase_type.lower() == PHASE_TYPE_POC:
        return ARCHITECTURE_ANALYSIS_PROMPT_POC
    elif phase_type.lower() == PHASE_TYPE_MVP:
        return ARCHITECTURE_ANALYSIS_PROMPT_MVP
    else:
        return ARCHITECTURE_ANALYSIS_PROMPT  # Default


# ═══════════════════════════════════════════════════════════════════════════════
# COST REPORT PROMPTS (Phase-aware)
# ═══════════════════════════════════════════════════════════════════════════════

def get_cost_report_prompt(phase_type: str) -> str:
    """Get the appropriate cost report prompt based on phase selection.

    Args:
        phase_type: 'poc', 'mvp', or 'both'

    Returns:
        The appropriate prompt string
    """
    if phase_type.lower() == PHASE_TYPE_POC:
        return AZURE_COST_REPORT_PROMPT_POC
    elif phase_type.lower() == PHASE_TYPE_MVP:
        return AZURE_COST_REPORT_PROMPT_MVP
    else:
        return AZURE_COST_REPORT_PROMPT_BOTH


AZURE_COST_REPORT_PROMPT_POC = """You are an Azure Cloud Cost Estimator producing output matching the official Azure Pricing Calculator export format.

PROJECT CONTEXT:
{context}

USER INSTRUCTIONS:
{instructions}

CLARIFICATION ANSWERS:
{answers}

---

## POC CHARACTERISTICS

**POC (Proof of Concept) focuses on:**
- Minimal viable architecture to prove technical feasibility
- Lower tiers/SKUs (Free, Basic, B1, Consumption, Flex Consumption)
- Single region deployment (Canada Central preferred)
- Minimal redundancy (LRS storage, single instances)
- Limited scale (small token limits, minimal storage)
- Duration: 1-3 months
- No production security/monitoring overhead

---

## OUTPUT FORMAT (STRICT JSON — Azure Pricing Calculator Style)

The "description" field MUST match the Azure Pricing Calculator export verbosity. Include exact tier names, instance sizes, quantities, units, regions, redundancy types, and configuration details.

Example description formats:
- "Flex Consumption tier, 2048 MB Instance memory size, 3,499 x10 On demand executions per month, 100 Active on demand executions seconds per instance, 1 Active on demand instances"
- "Standard Tier, 1 registry x 30 days, 0 GB Extra Storage, Container Build - 1 CPUs x 1 Seconds"
- "Consumption Plan Type, 0.05 million requests per month, Pay as you go, 20 concurrent requests per container app, 100 milliseconds execution time per request, 1 vCPU, 1 GiB memory, Pay as you go"
- "Azure Cosmos DB for NoSQL (formerly Core), Serverless, 1 million RU/s consumed, 1 GB transactional storage, Analytical storage disabled"
- "Block Blob Storage, General Purpose V2, Flat Namespace, LRS Redundancy, Hot Access Tier, 10 GB Capacity - Pay as you go, 10 x 10,000 Write operations, 10 x 10,000 Read operations"
- "Language Models, GPT 4.1, Standard (On-Demand), Global, 10,000 x 1,000 input tokens, 0 x 1,000 cached input, 1,000 x 1,000 output tokens"

Generate this exact JSON structure:
{{
  "report_title": "Microsoft Azure Estimate",
  "phase_name": "POC (Proof of Concept)",
  "phase_description": "Technical feasibility validation - 1-3 months",
  "client": "[Client name from artifacts]",
  "prepared_by": "Optimus Information Inc.",
  "date": "[Current Month Year]",
  "currency": "USD",

  "summary": {{
    "total_monthly": 0.00,
    "total_annual": 0.00,
    "upfront_cost": 0.00,
    "total_services": 0
  }},

  "services": [
    {{
      "service_category": "Compute",
      "service_type": "Azure Functions",
      "custom_name": "",
      "region": "Canada Central",
      "description": "Flex Consumption tier, 2048 MB Instance memory size, 100 x10 On demand executions per month, 100 Active on demand executions seconds per instance, 1 Active on demand instances",
      "estimated_monthly_cost": 0.00,
      "estimated_upfront_cost": 0.00
    }}
  ],

  "footer": {{
    "support_monthly": 0.00,
    "licensing_program": "Microsoft Customer Agreement (MCA)",
    "billing_account": "",
    "billing_profile": ""
  }}
}}

---

## POC TIER GUIDELINES

| Service | POC Tier | Typical Cost |
|---------|----------|--------------|
| Azure OpenAI | GPT 4.1, 10K tokens/mo | ~$15/mo |
| AI Search | Free (50MB) | $0/mo |
| App Service | B1 Basic | $13.14/mo |
| Container Apps | Consumption minimal | ~$0.01/mo |
| Storage | LRS, Block Blob, 10GB | ~$1/mo |
| Cosmos DB | Serverless | ~$5/mo |
| Functions | Flex Consumption free tier | $0/mo |
| Container Registry | Basic | ~$5/mo |

---

## IMPORTANT RULES

1. Use FREE and BASIC tiers wherever possible
2. Single instances only (no HA/redundancy)
3. LRS storage (not GRS)
4. Skip security services (Key Vault) unless critical
5. Skip monitoring (App Insights) for POC
6. Use REAL Azure pricing (Canada Central region preferred)
7. Every service must be justified by project requirements
8. Calculate summary totals accurately
9. description MUST be verbose like Azure Pricing Calculator — include tier, SKU, quantities, units, region specifics
10. Include the footer section with Support and Licensing Program

## EXAMPLE: Complete row for Azure Functions
{{
  "service_category": "Compute",
  "service_type": "Azure Functions",
  "custom_name": "",
  "region": "Canada Central",
  "description": "Flex Consumption tier, 2048 MB Instance memory size, 3,499 x10 On demand executions per month, 100 Active on demand executions seconds per instance, 1 Active on demand instances",
  "estimated_monthly_cost": 0.00,
  "estimated_upfront_cost": 0.00
}}

## EXAMPLE: Complete row for Azure Cosmos DB
{{
  "service_category": "Databases",
  "service_type": "Azure Cosmos DB",
  "custom_name": "",
  "region": "Canada Central",
  "description": "Azure Cosmos DB for NoSQL (formerly Core), Serverless, 1 million RU/s consumed, 1 GB transactional storage, Analytical storage disabled",
  "estimated_monthly_cost": 5.11,
  "estimated_upfront_cost": 0.00
}}

## EXAMPLE: Complete row for Storage Account
{{
  "service_category": "Storage",
  "service_type": "Storage Accounts",
  "custom_name": "",
  "region": "Canada Central",
  "description": "Block Blob Storage, General Purpose V2, Flat Namespace, LRS Redundancy, Hot Access Tier, 10 GB Capacity - Pay as you go, 10 x 10,000 Write operations, 10 x 10,000 Read operations, 10 x 10,000 Iterative Read operations, 10 x 10,000 Others operations, 10 x 10,000 Iterative Write operations, 100 GB Data Retrieval - Pay as you go, 100 GB Data Write - Pay as you go",
  "estimated_monthly_cost": 1.32,
  "estimated_upfront_cost": 0.00
}}"""


AZURE_COST_REPORT_PROMPT_MVP = """You are an Azure Cloud Cost Estimator producing output matching the official Azure Pricing Calculator export format.

PROJECT CONTEXT:
{context}

USER INSTRUCTIONS:
{instructions}

CLARIFICATION ANSWERS:
{answers}

---

## MVP CHARACTERISTICS

**MVP (Minimum Viable Product) focuses on:**
- Production-ready architecture for initial launch
- Standard/Production tiers (Standard, S1, P1)
- High availability considerations (multi-instance, GRS)
- Realistic scale for initial user base
- Includes monitoring, security, DevOps
- Duration: 3-6 months ongoing
- Ready for real users/clients

---

## OUTPUT FORMAT (STRICT JSON — Azure Pricing Calculator Style)

The "description" field MUST match the Azure Pricing Calculator export verbosity. Include exact tier names, instance sizes, quantities, units, regions, redundancy types, and configuration details.

Example description formats:
- "Standard S1, 1 Unit(s), 1 Month, 430K semantic queries"
- "Vault: 1 operations, 0 advanced operations, 0 renewals, 0 protected keys; Managed HSM Pools: 0 Standard B1 HSM Pool(s) x 730 Hours"
- "Azure Cosmos DB for NoSQL (formerly Core), Standard provisioned throughput (manual), Always-free quantity disabled, Pay as you go, General Purpose, Single Write- Canada Central (Write Region), 4,000 RUs x 1 Month, 0 GB transactional storage, Analytical storage disabled, 2 copies of periodic backup storage, Dedicated Gateway not enabled"
- "Language Models, GPT 4.1, Standard (On-Demand), Global, 80,000 x 1,000 input tokens, 0 x 1,000 cached input, 1,499 x 1,000 output tokens"

Generate this exact JSON structure:
{{
  "report_title": "Microsoft Azure Estimate",
  "phase_name": "MVP (Minimum Viable Product)",
  "phase_description": "Production-ready for initial launch - 3-6 months",
  "client": "[Client name from artifacts]",
  "prepared_by": "Optimus Information Inc.",
  "date": "[Current Month Year]",
  "currency": "USD",

  "summary": {{
    "total_monthly": 0.00,
    "total_annual": 0.00,
    "upfront_cost": 0.00,
    "total_services": 0
  }},

  "services": [
    {{
      "service_category": "AI + Machine Learning",
      "service_type": "Azure OpenAI",
      "custom_name": "",
      "region": "East US 2",
      "description": "Language Models, GPT 4.1, Standard (On-Demand), Global, 80,000 x 1,000 input tokens, 0 x 1,000 cached input, 1,499 x 1,000 output tokens",
      "estimated_monthly_cost": 171.99,
      "estimated_upfront_cost": 0.00
    }},
    {{
      "service_category": "Security",
      "service_type": "Key Vault",
      "custom_name": "",
      "region": "East US",
      "description": "Vault: 1 operations, 0 advanced operations, 0 renewals, 0 protected keys, 0 advanced protected keys; Managed HSM Pools: 0 Standard B1 HSM Pool(s) x 730 Hours",
      "estimated_monthly_cost": 0.03,
      "estimated_upfront_cost": 0.00
    }}
  ],

  "footer": {{
    "support_monthly": 0.00,
    "licensing_program": "Microsoft Customer Agreement (MCA)",
    "billing_account": "",
    "billing_profile": ""
  }}
}}

---

## MVP TIER GUIDELINES

| Service | MVP Tier | Typical Cost |
|---------|----------|--------------|
| Azure OpenAI | GPT 4.1, 80K+ tokens/mo | ~$172/mo |
| AI Search | Standard S1 | $674/mo |
| App Service | S1 Standard | $69.35/mo |
| Container Apps | Consumption + dedicated | ~$87/mo |
| Storage | GRS, 250GB+ | ~$12/mo |
| Cosmos DB | Standard 4,000 RU/s | ~$257/mo |
| Functions | Flex Consumption | ~$5/mo |
| Key Vault | Standard | ~$0.03/mo |
| Azure Monitor | App Insights + Logs | ~$58/mo |
| Container Registry | Standard | ~$20/mo |

---

## IMPORTANT RULES

1. Use STANDARD/PRODUCTION tiers
2. Include high availability (2+ instances where applicable)
3. GRS storage for redundancy
4. MUST include Key Vault for secrets
5. MUST include Application Insights for monitoring
6. Use REAL Azure pricing (prefer Canada Central, East US, East US 2)
7. Every service must be justified by project requirements
8. Calculate summary totals accurately
9. description MUST be verbose like Azure Pricing Calculator — include tier, SKU, quantities, units, region specifics
10. Include the footer section with Support and Licensing Program

## EXAMPLE: Complete row for Azure Cosmos DB (MVP)
{{
  "service_category": "Databases",
  "service_type": "Azure Cosmos DB",
  "custom_name": "",
  "region": "Canada Central",
  "description": "Azure Cosmos DB for NoSQL (formerly Core), Standard provisioned throughput (manual), Always-free quantity disabled, Pay as you go, General Purpose, Single Write- Canada Central (Write Region), 4,000 RUs x 1 Month, 0 GB transactional storage, Analytical storage disabled, 2 copies of periodic backup storage, Dedicated Gateway not enabled",
  "estimated_monthly_cost": 257.40,
  "estimated_upfront_cost": 0.00
}}

## EXAMPLE: Complete row for Container Apps (MVP)
{{
  "service_category": "Containers",
  "service_type": "Azure Container Apps",
  "custom_name": "",
  "region": "Canada Central",
  "description": "Consumption Plan Type, 1 million requests per month, Pay as you go, 20 concurrent requests per container app, 500 milliseconds execution time per request, 2 vCPU, 4 GiB memory, Pay as you go",
  "estimated_monthly_cost": 87.60,
  "estimated_upfront_cost": 0.00
}}

## EXAMPLE: Complete row for App Service (MVP)
{{
  "service_category": "Compute",
  "service_type": "App Service",
  "custom_name": "",
  "region": "Canada Central",
  "description": "Standard Tier; 1 S1 (1 Core(s), 1.75 GB RAM, 50 GB Storage) x 730 Hours; Linux OS",
  "estimated_monthly_cost": 69.35,
  "estimated_upfront_cost": 0.00
}}"""


AZURE_COST_REPORT_PROMPT_BOTH = """You are an Azure Cloud Cost Estimator producing output matching the official Azure Pricing Calculator export format.

PROJECT CONTEXT:
{context}

USER INSTRUCTIONS:
{instructions}

CLARIFICATION ANSWERS:
{answers}

---

## PHASE DEFINITIONS

**POC (Proof of Concept):**
- Minimal architecture, free/basic tiers
- Single region (Canada Central), no redundancy
- 1-3 months duration
- No security/monitoring overhead

**MVP (Minimum Viable Product):**
- Production-ready architecture
- Standard tiers, HA considerations
- Includes security (Key Vault) & monitoring (App Insights, Azure Monitor)
- 3-6 months ongoing

---

## OUTPUT FORMAT (STRICT JSON — Azure Pricing Calculator Style)

The "description" field MUST match the Azure Pricing Calculator export verbosity. Include exact tier names, instance sizes, quantities, units, regions, redundancy types, and configuration details.

Example description formats:
- "Flex Consumption tier, 2048 MB Instance memory size, 3,499 x10 On demand executions per month, 100 Active on demand executions seconds per instance, 1 Active on demand instances"
- "Consumption Plan Type, 0.05 million requests per month, Pay as you go, 20 concurrent requests per container app, 100 milliseconds execution time per request, 1 vCPU, 1 GiB memory, Pay as you go"
- "Azure Cosmos DB for NoSQL (formerly Core), Standard provisioned throughput (manual), Always-free quantity disabled, Pay as you go, General Purpose, Single Write- Canada Central (Write Region), 4,000 RUs x 1 Month, 0 GB transactional storage, Analytical storage disabled, 2 copies of periodic backup storage, Dedicated Gateway not enabled"
- "Block Blob Storage, General Purpose V2, Flat Namespace, LRS Redundancy, Hot Access Tier, 10 GB Capacity - Pay as you go, 10 x 10,000 Write operations, 10 x 10,000 List and Create Container Operations, 10 x 10,000 Read operations, 1 x 10,000 Other operations. 10 GB Data Retrieval, 1,000 GB Data Write, SFTP disabled, Object Replication disabled"
- "Language Models, GPT 4.1, Standard (On-Demand), Global, 80,000 x 1,000 input tokens, 0 x 1,000 cached input, 1,499 x 1,000 output tokens"
- "Standard S1, 1 Unit(s), 1 Month, 430K semantic queries"

Generate this exact JSON structure with BOTH POC and MVP:
{{
  "report_title": "Microsoft Azure Estimate",
  "client": "[Client name from artifacts]",
  "prepared_by": "Optimus Information Inc.",
  "date": "[Current Month Year]",
  "currency": "USD",

  "poc": {{
    "phase_name": "POC (Proof of Concept)",
    "phase_description": "Technical feasibility validation - 1-3 months",
    "summary": {{
      "total_monthly": 0.00,
      "total_annual": 0.00,
      "upfront_cost": 0.00,
      "total_services": 0
    }},
    "services": [
      {{
        "service_category": "AI + Machine Learning",
        "service_type": "Azure OpenAI",
        "custom_name": "",
        "region": "East US 2",
        "description": "Language Models, GPT 4.1, Standard (On-Demand), Global, 10,000 x 1,000 input tokens, 0 x 1,000 cached input, 1,000 x 1,000 output tokens",
        "estimated_monthly_cost": 28.56,
        "estimated_upfront_cost": 0.00
      }}
    ],
    "footer": {{
      "support_monthly": 0.00,
      "licensing_program": "Microsoft Customer Agreement (MCA)",
      "billing_account": "",
      "billing_profile": ""
    }}
  }},

  "mvp": {{
    "phase_name": "MVP (Minimum Viable Product)",
    "phase_description": "Production-ready for initial launch - 3-6 months",
    "summary": {{
      "total_monthly": 0.00,
      "total_annual": 0.00,
      "upfront_cost": 0.00,
      "total_services": 0
    }},
    "services": [
      {{
        "service_category": "AI + Machine Learning",
        "service_type": "Azure OpenAI",
        "custom_name": "",
        "region": "East US 2",
        "description": "Language Models, GPT 4.1, Standard (On-Demand), Global, 80,000 x 1,000 input tokens, 0 x 1,000 cached input, 1,499 x 1,000 output tokens",
        "estimated_monthly_cost": 171.99,
        "estimated_upfront_cost": 0.00
      }},
      {{
        "service_category": "Security",
        "service_type": "Key Vault",
        "custom_name": "",
        "region": "East US",
        "description": "Vault: 1 operations, 0 advanced operations, 0 renewals, 0 protected keys, 0 advanced protected keys; Managed HSM Pools: 0 Standard B1 HSM Pool(s) x 730 Hours",
        "estimated_monthly_cost": 0.03,
        "estimated_upfront_cost": 0.00
      }}
    ],
    "footer": {{
      "support_monthly": 0.00,
      "licensing_program": "Microsoft Customer Agreement (MCA)",
      "billing_account": "",
      "billing_profile": ""
    }}
  }}
}}

---

## TIER COMPARISON

| Service | POC Tier | MVP Tier |
|---------|----------|----------|
| Azure OpenAI | GPT 4.1, 10K tokens | GPT 4.1, 80K+ tokens |
| AI Search | Free | Standard S1 $674/mo |
| App Service | B1 $13/mo | S1 $69/mo |
| Storage | LRS 10GB | GRS 250GB |
| Cosmos DB | Serverless | Standard 4,000 RU/s |
| Key Vault | — | Standard |
| Azure Monitor | — | App Insights + Logs |
| Container Registry | Basic $5/mo | Standard $20/mo |

---

## IMPORTANT RULES

1. Generate BOTH poc and mvp sections
2. POC uses minimal/free tiers
3. MVP uses production-ready tiers
4. MVP typically costs 3-5x more than POC
5. Use REAL Azure pricing (Canada Central, East US, East US 2)
6. Calculate summary totals accurately for each phase
7. description MUST be verbose like Azure Pricing Calculator — include all config details
8. Include footer section with Support and Licensing Program for each phase

## EXAMPLE: How a complete "description" field should look
- "Flex Consumption tier, 2048 MB Instance memory size, 3,499 x10 On demand executions per month, 100 Active on demand executions seconds per instance, 1 Active on demand instances"
- "Azure Cosmos DB for NoSQL (formerly Core), Standard provisioned throughput (manual), Always-free quantity disabled, Pay as you go, General Purpose, Single Write- Canada Central (Write Region), 4,000 RUs x 1 Month, 0 GB transactional storage, Analytical storage disabled, 2 copies of periodic backup storage, Dedicated Gateway not enabled"
- "Block Blob Storage, General Purpose V2, Flat Namespace, LRS Redundancy, Hot Access Tier, 10 GB Capacity - Pay as you go, 10 x 10,000 Write operations, 10 x 10,000 Read operations, 10 x 10,000 Iterative Read operations, 10 x 10,000 Others operations"
- "Standard Tier; 1 S1 (1 Core(s), 1.75 GB RAM, 50 GB Storage) x 730 Hours; Linux OS"
- "Standard S1, 1 Unit(s), 1 Month, 430K semantic queries"
- "Standard Tier, 1 registry x 30 days, 0 GB Extra Storage, Container Build - 1 CPUs x 1 Seconds"

EVERY description in the output MUST be this verbose. Short descriptions like "Basic tier" or "Standard plan" are NOT acceptable."""


# Keep backward compatibility - this is the default prompt
AZURE_COST_REPORT_PROMPT = AZURE_COST_REPORT_PROMPT_BOTH


INTENT_RECOGNITION_PROMPT = """Analyze the user's message and determine their intent.

USER MESSAGE:
{message}

CONTEXT:
- Current session has artifacts: {has_artifacts}
- Previously generated: {previous_generations}

Classify the intent into one of these categories:
1. "generate_architecture" - User wants to create/generate an architecture diagram
2. "generate_dfd" - User wants to create/generate a data flow diagram
3. "generate_ppt" - User wants to create/generate a presentation deck
4. "generate_cost" - User wants to create/generate a cost report
5. "generate_cost_poc" - User wants POC cost report specifically
6. "generate_cost_mvp" - User wants MVP cost report specifically
7. "edit_architecture" - User wants to modify/update an existing architecture diagram
8. "edit_dfd" - User wants to modify/update an existing data flow diagram
9. "edit_ppt" - User wants to modify/update an existing presentation
10. "edit_cost" - User wants to modify/update an existing cost report
11. "select_phase" - User is selecting POC or MVP phase
12. "clarify" - User is asking a question or needs clarification
13. "upload" - User is uploading or discussing artifacts
14. "unknown" - Cannot determine intent

Return a JSON response:
{{
    "intent": "intent_category",
    "action": "generate" or "edit" or "select" or "other",
    "target": "architecture" or "dfd" or "ppt" or "cost" or "cost_poc" or "cost_mvp" or null,
    "phase_type": "poc" or "mvp" or "both" or null,
    "confidence": 0.0 to 1.0,
    "extracted_instructions": "Any specific instructions the user mentioned"
}}"""


ENHANCED_ARCHITECTURE_IMAGE_PROMPT = """Create a professional Microsoft Azure architecture diagram matching the official Azure documentation style exactly.

PROJECT: {project_name}

## MANDATORY VISUAL REQUIREMENTS

**Icon Format (CRITICAL):**
- ALL service icons must be SQUARE (not rectangular)
- Label text must be BELOW each icon (not inside)
- Icon size: 48x48 or 64x64 pixels
- Clean, official Azure icon colors

**Layout Style:**
- WHITE background (pure white, no gray)
- Use thin DASHED-LINE or SOLID-LINE rectangles for grouping (no colored fills)
- Professional technical diagram style like draw.io or Microsoft Visio
- Left-to-right flow direction

**MANDATORY Elements (Non-negotiable):**
1. **Microsoft Azure Logo** - TOP-RIGHT corner: 4-color square logo with "Microsoft Azure" text to the right
2. **NO TEXT ON ARROWS** - Arrows are plain thin black lines WITHOUT labels
3. **4 Monitoring Icons at Bottom-Left** - SQUARE icons with labels BELOW:
   - Azure DevOps (blue infinity loop)
   - Key Vault (gold key)
   - Azure Monitor (blue speedometer)
   - App Insights (purple lightbulb)
4. **Virtual Network** - Dashed border encompassing Azure cloud services

**Azure Service Icons (SQUARE with label below):**
- User: Blue person silhouette
- Azure Bot: Blue robot icon
- Container Apps: Green hexagonal container
- MS Teams: Purple T icon
- API Management: Purple cloud with API
- Azure Functions: Yellow lightning bolt
- Cosmos DB: Blue globe with dots
- Blob Storage: Blue storage blocks
- AI Search: Blue magnifying glass
- Azure OpenAI: Blue brain icon
- AI Foundry/Agents: Purple hexagonal gem (use for MCP Client/Orchestrator)
- Document Intelligence: Blue document with sparkles
- SharePoint: Teal S icon
- Microsoft Fabric: Orange/teal hexagon
- Databricks: Red diamond

## COMPONENTS TO INCLUDE:
{components_description}

## CONNECTIONS:
{connections_description}

## EXTERNAL SYSTEMS:
{external_description}

## LAYOUT STRUCTURE (Match Reference)

**Left Side (Users):**
- User icon (blue person) with label below
- Entry points: Azure Bot, Container Apps, MS Teams (square icons, labels below)

**Center-Left (Gateway):**
- "APIM Subnet" group with API Management inside

**Center (Core Processing):**
- "Container App Subnet" group
- Azure Container Apps icons

**Center (AI Foundry section with light blue background):**
- "AI Foundry" group containing:
  - Foundry Agents (purple gem icon, label: "Foundry Agents (Chooses/Switches required Tools)")
  - Tool icons in row: SharePoint Tool, Plot Tool, MS Fabric Tool, Databricks Tool

**Right Side (Data):**
- "Data Sources" group containing:
  - SharePoint icon with label
  - Microsoft Fabric icon with label  
  - Azure Databricks icon with label

**Top:**
- "Virtual Network" with dashed border
- "Private Link Subnet" group

**Bottom-Left (Always Present):**
- Horizontal row of 4 SQUARE icons with labels BELOW:
  - Azure DevOps
  - Key Vault
  - Azure Monitor
  - App Insights

**Optional (if applicable):**
- "Current Scope" - Green filled square
- "Future Extension" - White square with green border

## ARROW STYLE (NO TEXT)

- Thin black lines (1px)
- Simple arrowheads pointing to target
- **NO TEXT ON ARROWS** - arrows are completely plain
- Connect centers of icons

## TEXT REQUIREMENTS

- Font: Segoe UI or similar clean sans-serif
- Icon labels: 10-12pt, BELOW each square icon (centered)
- Group labels: 12-14pt bold, at top-left of groups
- All text must be spelled correctly and legible

## CRITICAL RULES

1. ALL icons are SQUARE with label BELOW (not text inside rectangular boxes)
2. Microsoft Azure logo in TOP-RIGHT corner
3. NO text on arrows - arrows are plain lines only
4. 4 monitoring icons at bottom-left as SQUARE icons with labels below
5. Use thin borders for groups, transparent or very light backgrounds
6. For AI Foundry/Agents use purple hexagonal gem icon
7. Tools use gray chain/wrench icons
8. Pure WHITE background
9. Professional technical style - NOT artistic
10. Resolution must be clear at 1024x1024"""


ENHANCED_PPT_CONTENT_PROMPT = """Based on the following project context, generate professional presales presentation content.

PROJECT CONTEXT:
{context}

USER INSTRUCTIONS:
{instructions}

CLARIFICATION ANSWERS:
{answers}

Generate a JSON response with content for each slide. The presentation should follow this structure:

1. Title Slide
2. Our Understanding (3 sections: Our Understanding, Current Challenges, AI Opportunity)
3. Objective - Clear, polished 3-4 bullet points
4. Scope - What's included in the project
5. High Level Design - Architecture overview (will use generated architecture diagram image)
6. Prerequisite - What's needed before starting
7. Definition of Done - Success criteria with bold section headers
8. Out Of Scope - What's explicitly excluded
9. Timelines & Effort - Project timeline
10. Timelines & Cost - Cost breakdown
11. Next Steps - Immediate action items

**CRITICAL FORMATTING RULES:**
1. Our Understanding MUST have 3 sections:
   - Section 1: "Our Understanding" (what we understand)
   - Section 2: "Current Challenges" (problems faced)
   - Section 3: "AI Opportunity" (how AI solves it)
   Each section header should be bold, followed by 2-3 points.

2. Objective: 3-4 polished, concise bullet points only. NO "Problem Statement" prefix.

3. Prerequisites: Use format "CATEGORY: description" where CATEGORY is bold (e.g., "Azure Environment Access: Contributor access...")

4. Definition of Done: Use format "SECTION: description" where SECTION is bold (e.g., "Documentation & Stakeholder Sign-off: Architecture docs delivered...")

5. Out of Scope: Direct bullet points, NO section headers

6. Timeline & Effort: Simple phase list with "Phase Name — Duration" format

7. Timeline & Cost: Table-style format with Service/Item and Cost columns

8. Next Steps: Direct action items, NO title repetition

Return JSON:
{{
  "title_slide": {{
    "title": "Project name — Presales Proposal",
    "client": "Client name",
    "date": "Month Year"
  }},
  "our_understanding": {{
    "sections": [
      {{
        "header": "Our Understanding",
        "points": ["We understand point 1", "We understand point 2"]
      }},
      {{
        "header": "Current Challenges",
        "points": ["Challenge 1", "Challenge 2"]
      }},
      {{
        "header": "AI Opportunity",
        "points": ["Opportunity 1", "Opportunity 2"]
      }}
    ]
  }},
  "objective": {{
    "points": ["Polished objective 1", "Polished objective 2", "Polished objective 3"]
  }},
  "scope": {{
    "points": ["Scope item 1", "Scope item 2", "Scope item 3", "Scope item 4"]
  }},
  "high_level_design": {{
    "note": "Architecture diagram will be auto-inserted"
  }},
  "prerequisites": {{
    "items": [
      {{"category": "Azure Environment Access", "description": "Contributor access to Azure subscription"}},
      {{"category": "Source Documents", "description": "Access to knowledge base and documentation"}},
      {{"category": "DevOps Setup", "description": "GitHub repo and pipeline configured"}}
    ]
  }},
  "definition_of_done": {{
    "items": [
      {{"section": "Development Completion", "description": "All features implemented and tested"}},
      {{"section": "Documentation & Stakeholder Sign-off", "description": "Architecture docs delivered and demo approved"}},
      {{"section": "Production Readiness", "description": "Monitoring, security, and deployment validated"}}
    ]
  }},
  "out_of_scope": {{
    "points": ["Excluded item 1", "Excluded item 2", "Excluded item 3"]
  }},
  "timeline_cost": {{
    "phases": [
      {{"phase": "Phase 1: Discovery", "duration": "2 weeks"}},
      {{"phase": "Phase 2: Development", "duration": "8 weeks"}},
      {{"phase": "Phase 3: Testing", "duration": "2 weeks"}},
      {{"phase": "Phase 4: Deployment", "duration": "1 week"}}
    ]
  }},
  "cost_estimate": {{
    "items": [
      {{"service": "Development Team", "cost": "Based on timeline"}},
      {{"service": "Azure Infrastructure (Monthly)", "cost": "See detailed cost report"}},
      {{"service": "Licensing & Tools", "cost": "TBD"}}
    ]
  }},
  "next_steps": {{
    "steps": ["Contract finalization", "Kickoff meeting and sprint planning", "Development start", "Weekly progress reviews"]
  }}
}}"""
