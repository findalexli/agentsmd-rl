#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "\u251c\u2500\u2500 agents/              # Agent persona definitions (backend, frontend, infrast" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -70,12 +70,30 @@ Apply these principles to every task.
 ## Repository Structure
 
 ```
+AGENTS.md                # Agent configuration template
+CATALOG.md               # Full skill catalog
+
 .github/
-├── skills/           # Domain-specific knowledge packages
-│   └── */SKILL.md    # Each skill has YAML frontmatter + markdown body
-├── prompts/          # Reusable prompt templates
-├── agents/           # Agent persona definitions
+├── skills/              # All 127 skills (flat structure with language suffixes)
+│   └── */SKILL.md       # Each skill has YAML frontmatter + markdown body
+├── prompts/             # Reusable prompt templates
+├── agents/              # Agent persona definitions (backend, frontend, infrastructure, planner, presenter)
+├── scripts/             # Automation scripts (doc scraping)
+├── workflows/           # GitHub Actions (daily doc updates)
 └── copilot-instructions.md
+
+output/                  # Generated llms.txt files (daily workflow)
+├── llms.txt             # Links + summaries
+└── llms-full.txt        # Full content
+
+skills/                  # Symlinks for backward compatibility
+├── python/              # -> ../.github/skills/*-py
+├── dotnet/              # -> ../.github/skills/*-dotnet
+├── typescript/          # -> ../.github/skills/*-ts
+└── java/                # -> ../.github/skills/*-java
+
+.vscode/
+└── mcp.json             # MCP server configurations
 ```
 
 ## Skills
@@ -84,27 +102,41 @@ Skills are domain-specific knowledge packages in `.github/skills/`. Each skill h
 - **YAML frontmatter** (`name`, `description`) — triggers skill loading
 - **Markdown body** — loaded only when skill activates
 
-### Available Skills
+### Skill Naming Convention
+
+Skills use language suffixes for discoverability:
+
+| Language | Suffix | Examples |
+|----------|--------|----------|
+| **Core** | — | `mcp-builder`, `skill-creator`, `azd-deployment` |
+| **Python** | `-py` | `inference-py`, `cosmos-db-py`, `foundry-sdk-py` |
+| **.NET** | `-dotnet` | `inference-dotnet`, `cosmosdb-dotnet` |
+| **TypeScript** | `-ts` | `inference-ts`, `agents-ts`, `nextgen-frontend-ts` |
+| **Java** | `-java` | `inference-java`, `cosmos-java` |
+
+### Featured Skills
 
 | Skill | Purpose |
 |-------|---------|
-| `azure-ai-search-python` | Search SDK patterns, vector/hybrid search, agentic retrieval |
-| `azure-ai-agents-python` | Low-level agents SDK for CRUD, threads, streaming, tools |
-| `azure-ai-voicelive-skill` | Real-time voice AI with Azure AI Voice Live SDK |
-| `foundry-sdk-python` | High-level Foundry project client, versioned agents, evals |
-| `foundry-iq-python` | Agentic retrieval with knowledge bases |
-| `foundry-nextgen-frontend` | NextGen Design System UI patterns (Vite + React) |
-| `agent-framework-azure-hosted-agents` | Agent Framework SDK for persistent Azure agents |
+| `azure-ai-search-py` | Search SDK patterns, vector/hybrid search, agentic retrieval |
+| `azure-ai-agents-py` | Low-level agents SDK for CRUD, threads, streaming, tools |
+| `azure-ai-voicelive-py` | Real-time voice AI with Azure AI Voice Live SDK |
+| `foundry-sdk-py` | High-level Foundry project client, versioned agents, evals |
+| `foundry-iq-py` | Agentic retrieval with knowledge bases |
+| `nextgen-frontend-ts` | NextGen Design System UI patterns (Vite + React) |
+| `agent-framework-py` | Agent Framework SDK for persistent Azure agents |
 | `azd-deployment` | Azure Developer CLI deployment to Container Apps with Bicep |
-| `mcp-builder` | Building MCP servers (Python/Node) |
-| `cosmos-db-python-skill` | Cosmos DB NoSQL with Python/FastAPI |
-| `fastapi-router` | FastAPI routers with CRUD, auth, response models |
-| `pydantic-models` | Pydantic v2 multi-model patterns |
-| `zustand-store` | Zustand stores with TypeScript and subscribeWithSelector |
-| `react-flow-node` | React Flow custom nodes with TypeScript |
+| `mcp-builder` | Building MCP servers (Python/Node/C#) |
+| `cosmos-db-py` | Cosmos DB NoSQL with Python/FastAPI |
+| `fastapi-router-py` | FastAPI routers with CRUD, auth, response models |
+| `pydantic-models-py` | Pydantic v2 multi-model patterns |
+| `zustand-store-ts` | Zustand stores with TypeScript and subscribeWithSelector |
+| `react-flow-node-ts` | React Flow custom nodes with TypeScript |
 | `podcast-generation` | Podcast generation workflows |
 | `skill-creator` | Guide for creating new skills |
-| `issue-creator` | GitHub issue creation patterns |
+| `github-issue-creator` | GitHub issue creation patterns |
+
+📖 **See [CATALOG.md](../CATALOG.md) for all 127 skills**
 
 ### Skill Selection
 
@@ -218,15 +250,19 @@ assert result == expected
 ## Creating New Skills
 
 1. Create a new directory under `.github/skills/<skill-name>/`
+   - Use language suffix: `-py`, `-dotnet`, `-ts`, `-java`
+   - Core/cross-language skills have no suffix
+   - Example: `cosmos-db-py`, `inference-dotnet`, `mcp-builder`
 2. Add a `SKILL.md` file with YAML frontmatter:
    ```yaml
    ---
-   name: skill-name
+   name: skill-name-py
    description: Brief description of what the skill does and when to use it
    ---
    ```
 3. Add detailed instructions in the markdown body
 4. Keep skills focused on a single domain
+5. Reference official docs via `microsoft-docs` MCP for current API patterns
 
 ---
 
PATCH

echo "Gold patch applied."
