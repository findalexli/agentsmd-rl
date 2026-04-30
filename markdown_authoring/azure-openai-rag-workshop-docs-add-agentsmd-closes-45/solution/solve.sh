#!/usr/bin/env bash
set -euo pipefail

cd /workspace/azure-openai-rag-workshop

# Idempotency guard
if grep -qF "- For example, look for files that may contain the project name, idea, vision, r" ".github/prompts/create-agents.md.prompt.md" && grep -qF "A monorepo sample + workshop showing how to build a Retrieval\u2011Augmented Generati" "AGENTS.md" && grep -qF "- Responsibilities: Accept chat requests, perform embedding + vector similarity," "src/backend/AGENTS.md" && grep -qF "- Wrong API URL: Confirm build hook in root `azure.yaml` sets `BACKEND_API_URI` " "src/frontend/AGENTS.md" && grep -qF "- Keep parsing & chunking modular (add new file format handlers as separate util" "src/ingestion/AGENTS.md" && grep -qF "- Low default capacity to avoid quota deployment failures; adjust after deployme" "trainer/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/prompts/create-agents.md.prompt.md b/.github/prompts/create-agents.md.prompt.md
@@ -0,0 +1,87 @@
+---
+description: Generates an AGENTS.md file for a project repository
+---
+
+# Create high‑quality AGENTS.md file
+
+- **Input**: Any files that may provide context about the project, including but not limited to README files, documentation, configuration files (e.g., package.json, pyproject.toml, etc.), CI/CD workflows and any other relevant files.
+
+## Role
+
+You are an expert software architect and code agent. Your task is to create a complete, accurate `AGENTS.md` at the root of this repository that follows the public guidance at https://agents.md/.
+
+AGENTS.md is an open format designed to provide coding agents with the context and instructions they need to work effectively on a project.
+
+## Goal
+
+Based on your analysis of the project, your goal is to generate these:
+
+- Create or update `AGENTS.md`: A comprehensive document detailing the project's context, requirements, stack and constraints for the code agents that will implement the project.
+- There must at least one `AGENTS.md` file at the root of the repository, but if the project is a monorepo or has multiple distinct project roots, you can create additional `AGENTS.md` files in each relevant subdirectories.
+
+When creating the `AGENTS.md` file, prioritize clarity, completeness, and actionability. The goal is to give any coding agent enough context to effectively contribute to the project without requiring additional human guidance.
+
+## Instructions
+
+1. Examine the current project to understand its context, requirements, constraints, architecture, tech stack and specificities, and any existing files that may provide insights.
+  - For example, look for files that may contain the project name, idea, vision, requirements, technology stack and constraints. This may include README files, project documentation, configuration files (e.g., package.json, pyproject.toml, etc.), CI/CD workflows and any other relevant files.
+  - If the project is a monorepo or has multiple distinct project roots, identify the relevant subdirectories that may require their own `AGENTS.md` files.
+
+2. Once you have all the necessary information, create or update the `AGENTS.md` file with all relevant project context, requirements, stack and constraints for the code agents that will implement the project.
+  - When doing so, use this the template for structuring the document:
+    ```md
+    # [project_name]
+    [Project summary]
+
+    ## Overview
+    - [Brief description of what the project does, its purpose and audience]
+    - [Architecture overview if complex]
+    - [Project structure if relevant]
+
+    ## Key Technologies and Frameworks
+    - [List of main technologies, frameworks, and libraries used in the project]
+
+    ## Constraints and Requirements [if any]
+    - [Any specific constraints, requirements, or considerations for the project]
+
+    ## Challenges and Mitigation Strategies [if any]
+    - [Potential challenges and how they will be addressed]
+
+    ## Development Workflow [if applicable]
+    - [Most important scripts, commands, and tools for development, testing, and deployment. How to start dev server, run tests, build for production, etc.]
+
+    ## Coding Guidelines [if any]
+    - [Any specific coding standards, style guides, or best practices to follow]
+
+    ## Security Considerations [if any]
+    - [Any security practices or considerations relevant to the project]
+
+    ## Pull Request Guidelines [if any]
+    - [Any specific guidelines for creating pull requests, such as, title format, required checks, review process, commit message conventions, etc.]
+
+    ## Debugging and Troubleshooting [if applicable]
+    - [Common issues and solutions, logging patterns, debug configuration, performance considerations]
+    ```
+  - If a section is not relevant, you can omit it.
+  - **Be specific and concise**: include exact commands, and information from the provided context, do not make any assumptions or add unnecessary details.
+  - Only use information you found to fill the sections.
+  - Use standard Markdown formatting.
+  - If needed, you can add specific sections relevant to the project that are not covered by the template if they provide important context for the code agents.
+  - If the file already contains enough relevant information, you can skip this step.
+
+## Best Practices
+
+- **Be specific**: Include exact commands, not vague descriptions
+- **Use code blocks**: Wrap commands in backticks for clarity
+- **Include context**: Explain why certain steps are needed
+- **Stay current**: Update as the project evolves
+- **Test commands**: Ensure all listed commands actually work
+- **Keep it focused** on what agents need to know, not general project information
+
+## Monorepo Considerations
+
+For large monorepos:
+- Place a main `AGENTS.md` at the repository root
+- Create additional `AGENTS.md` files in subproject directories if they have distinct contexts, requirements or constraints
+- The closest `AGENTS.md` file takes precedence for any given location
+- Include navigation tips between packages/projects
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,119 @@
+# Azure OpenAI RAG Workshop (Node.js)
+A monorepo sample + workshop showing how to build a Retrieval‑Augmented Generation (RAG) chat experience using LangChain.js with Azure OpenAI (optionally Qdrant) and expose it through a Fastify backend, an ingestion Fastify service, and a Lit + Vite frontend. Infrastructure is provisioned and deployed to Azure using `azd` (Azure Developer CLI) with Azure Container Apps, Azure Static Web Apps, Azure AI Search (or Qdrant), and optional OpenAI proxy for training scenarios.
+
+## Overview
+- Purpose: Educational reference and workshop material for building a production‑minded RAG chat application on Azure.
+- Audience: Developers learning Azure OpenAI + vector search patterns (Azure AI Search or Qdrant), workshop trainers, contributors.
+- Architecture (core runtime):
+  - Frontend (Static Web App): Lit web components served via Vite build; proxies `/chat` to backend during local dev.
+  - Backend API (Container App): Fastify service orchestrating chat + retrieval via LangChain, Azure OpenAI (or provided OpenAI endpoint), Azure AI Search or Qdrant for vector retrieval.
+  - Ingestion API (Container App): Fastify service handling PDF uploads and embedding ingestion into chosen vector store.
+  - (Optional) Qdrant (Container App) or Azure AI Search (managed) selected via `useQdrant` parameter.
+  - Trainer Proxy (separate project in `trainer/`): Fastify reverse proxy to share a single Azure OpenAI instance with attendees.
+  - Observability: Azure Monitor / Application Insights via Bicep modules.
+- Project layout (selected):
+  - `src/frontend`: Web UI (Lit, Vite).
+  - `src/backend`: Chat + RAG API (Fastify + LangChain + OpenAI + Search/Qdrant).
+  - `src/ingestion`: Document ingestion API (Fastify) + PDF parsing.
+  - `infra`: Bicep templates (`main.bicep`, parameters, core modules) for full environment.
+  - `scripts`: Helper scripts (PDF ingestion upload).
+  - `trainer`: Workshop trainer proxy & material references.
+  - `docs`: Workshop and slide assets.
+  - Root `package.json`: Defines npm workspaces and shared tooling.
+
+## Key Technologies and Frameworks
+- Language: TypeScript (Node.js 20+, npm 10+).
+- Backend / Ingestion / Proxy: Fastify, Fastify CLI, Fastify plugins (cors, sensible, autoload, multipart, http-proxy).
+- RAG / AI: LangChain.js (`@langchain/*`, `langchain`), Azure OpenAI (or custom endpoint), token counting (`@dqbd/tiktoken`).
+- Vector Stores: Azure AI Search (`@azure/search-documents`) or Qdrant (`@qdrant/qdrant-js`, `@langchain/qdrant`).
+- Frontend: Vite, Lit, custom elements.
+- Infra / Deployment: Azure Developer CLI (`azd`), Bicep, Azure Container Apps, Azure Static Web Apps, Managed Identities, Application Insights, Log Analytics.
+- Tooling: ESLint (plugins: import, n, unicorn, @typescript-eslint), Prettier, concurrently, rimraf, TypeScript compiler.
+- Containerization: Dockerfiles per service (backend, ingestion, trainer), multi-stage builds.
+
+## Constraints and Requirements
+- Node.js >= 20, npm >= 10 (enforced via `engines`).
+- Monorepo with npm workspaces: `src/ingestion`, `src/backend`, `src/frontend`.
+- Azure subscription with Azure OpenAI access (or external OpenAI endpoint via `openAiUrl`).
+- Environment provisioning and deployment handled by `azd up` referencing `azure.yaml` + Bicep templates.
+- Vector DB choice controlled by parameter `useQdrant` (Bicep). If false => Azure AI Search; if true => Qdrant Container App + identity.
+- Model + deployment parameters externalized in `main.parameters.json` (e.g., `chatModelName`, `embeddingsModelName`, versions, capacities, free tier flags).
+- Managed Identity required (free search SKU unsupported) — roles assigned in Bicep (`role.bicep` modules) for OpenAI and Search.
+- Local dev uses environment variables loaded via `azd env get-values` (scripts reference). In docker-compose local mode, Qdrant may run at `http://qdrant:6333`.
+
+## Challenges and Mitigation Strategies
+- Multi-service coordination: Use npm workspaces and root scripts invoking scoped scripts via `concurrently`.
+- Environment variable drift: Regenerate `.env` after `azd provision` via postprovision hook (`azd env get-values > .env`).
+- Vector store abstraction: Both Azure AI Search and Qdrant dependencies included — ensure conditional logic in code respects `useQdrant` flag (code agents should not assume only one path).
+- Limited quotas (trainer scenario): Trainer proxy in `trainer/` allows shared OpenAI usage; capacity parameters can be tuned (`chatDeploymentCapacity`, `embeddingsDeploymentCapacity`).
+
+## Development Workflow
+Root scripts (`package.json`):
+- Start backend + frontend concurrently:
+  - `npm start` (invokes `concurrently "npm:start:*" --kill-others`).
+  - `start:frontend` => `npm run dev --workspace=frontend` (Vite dev server, default port 8000).
+  - `start:backend` => `npm run dev --workspace=backend` (Fastify dev, port 3000).
+- Ingestion service (not auto-started by root): `npm run dev --workspace=ingestion` (Fastify dev, port 3001).
+- Build all workspaces: `npm run build`.
+- Clean all: `npm run clean`.
+- Lint: `npm run lint`; Fix: `npm run lint:fix`.
+- Format: `npm run format`.
+- Docker build (all that implement `docker:build`): `npm run docker:build`.
+
+Per service notable scripts:
+- Backend (`src/backend/package.json`): `dev`, `build`, `start`, `docker:build`, `docker:run`, `clean`.
+- Ingestion (`src/ingestion/package.json`): same pattern (port 3001), plus multipart upload handling.
+- Frontend (`src/frontend/package.json`): `dev`, `build`, `watch`, `lint`, `clean`.
+- Trainer proxy (`trainer/package.json`): similar Fastify script set.
+
+Local ingestion helper script (after services running):
+```
+./scripts/ingest-data.sh
+```
+Uploads PDFs (`data/*.pdf`) to ingestion API (defaults to `http://localhost:3001`).
+
+Deployment (Azure):
+```
+azd auth login
+azd up
+```
+Outputs URIs and environment variables (captured into `.env` via postprovision hook). Clean up with:
+```
+azd down --purge
+```
+
+## Infrastructure Notes
+- Defined in `infra/main.bicep` + supporting modules under `infra/core/**`.
+- Subscription-scope deployment creates resource group, container apps env, registry, static web app, optional search service, optional Qdrant, OpenAI resource (unless `openAiUrl` provided), identities, role assignments, and monitoring stack.
+- Key outputs surfaced (e.g., `BACKEND_API_URI`, `INGESTION_API_URI`, `FRONTEND_URI`, `QDRANT_URL`, `AZURE_OPENAI_API_ENDPOINT`).
+- Parameterization via `main.parameters.json` referencing AZD environment variables.
+- `azure.yaml` ties logical services (frontend static web app build hook sets `BACKEND_API_URI`).
+- Post-up hook auto-runs ingestion script (PowerShell or Bash variant).
+
+## Coding Guidelines
+- TypeScript strictness implied (check `tsconfig` in each service; agents should preserve module resolution and ES module usage).
+- Use ES modules (`"type": "module"`).
+- Maintain Prettier formatting (config embedded in root `package.json`).
+- Lint with existing ESLint plugins; do not introduce new global dependencies without necessity.
+- Keep service Dockerfiles multi-stage minimal and aligned with Node 20 Alpine base.
+- Avoid duplicating logic between backend and ingestion — factor shared utilities if patterns recur (currently none specified; create new shared workspace only if needed).
+
+## Security Considerations
+- Managed Identities used for Azure resources; local auth disabled for certain services (`disableLocalAuth: true` in Bicep for OpenAI/Search when created).
+- Environment variables contain service endpoints and model names — do not commit secrets (no API keys are stored when using managed identity).
+- PDF upload endpoint (`/documents`) handles multipart; enforce size/content checks if extending (currently not detailed here, so preserve existing behavior).
+- CORS: Backend/ingestion use `@fastify/cors`; ensure allowed origins include deployed frontend (Bicep sets `allowedOrigins`).
+- Trainer proxy: Shares OpenAI capacity; treat as controlled-access (future task in TODO mentions adding event key restriction).
+
+## Debugging and Troubleshooting
+- If local services fail to start concurrently, run each individually to isolate (`npm run dev --workspace=backend`).
+- Vector backend selection issues: Verify `useQdrant` parameter in azd environment and ensure Qdrant Container App deployed (or Azure AI Search endpoint present in outputs).
+- Ingestion not populating data: Confirm `INGESTION_API_URI` and that PDF curl uploads return 2xx. Re-run ingestion script after redeploy.
+- Frontend API base: Logged at Vite startup (`Using chat API base URL:`) sourced from `BACKEND_API_URI` passed via build hook.
+
+---
+Closest project‑root `AGENTS.md` governs unless a subdirectory defines its own. See per‑service agent guides:
+- `src/backend/AGENTS.md`
+- `src/ingestion/AGENTS.md`
+- `src/frontend/AGENTS.md`
+- `trainer/AGENTS.md`
diff --git a/src/backend/AGENTS.md b/src/backend/AGENTS.md
@@ -0,0 +1,63 @@
+# Backend Service (Chat RAG API)
+Fastify + LangChain service providing chat responses augmented with document retrieval via Azure AI Search or Qdrant.
+
+## Overview
+- Entry: `src/app.ts` (exported via `package.json` exports).
+- Port: 3000 (Docker & dev).
+- Responsibilities: Accept chat requests, perform embedding + vector similarity, construct prompts with retrieved context, call Azure OpenAI (or provided OpenAI endpoint).
+- Vector Source: Conditional (Azure AI Search or Qdrant) depending on deployment parameters (`useQdrant`).
+
+## Key Dependencies
+- Fastify ecosystem (`fastify`, `@fastify/*`).
+- LangChain: `langchain`, `@langchain/core`, `@langchain/openai`, `@langchain/community`, `@langchain/qdrant`.
+- Azure SDK: `@azure/search-documents`, `@azure/identity`.
+- Token utilities: `@dqbd/tiktoken`.
+- Env mgmt: `dotenv` (ensure it loads early if used in code extensions).
+
+## Scripts
+```
+npm run dev        # Build + watch + start with pretty logs (debug level)
+npm run build      # tsc -> dist
+npm start          # Production (fastify start -l info dist/app.js)
+npm run docker:build  # docker build --tag backend --file ./Dockerfile ../..
+npm run docker:run    # Runs container exposing 3000
+npm run clean      # Remove dist
+```
+
+## Environment Variables (Injected via Bicep/azd)
+Expect (subset):
+- AZURE_OPENAI_API_ENDPOINT / *_MODEL / *_DEPLOYMENT_NAME / *_VERSION
+- AZURE_AISEARCH_ENDPOINT (empty when using Qdrant)
+- QDRANT_URL (empty when using Azure AI Search)
+- AZURE_CLIENT_ID (managed identity)
+
+Code should:
+- Branch feature logic based on presence/absence of `QDRANT_URL`.
+- Avoid hardcoding model names; use env.
+
+## Coding Guidelines
+- Use existing TypeScript config & ES modules.
+- Keep Fastify plugins modular (autoload pattern is present). Add new routes/plugins under standard directories (match existing layout when extending).
+- Prefer async/await, minimal side effects in global scope.
+
+## Testing / Verification (Manual)
+1. Start dependency (ingestion) and ensure documents ingested.
+2. `curl http://localhost:3000/chat` (exact routes depend on existing implementation—inspect routes before extending).
+
+## Performance Considerations
+- Minimize unnecessary embedding calls (reuse embeddings where possible if caching layer is introduced—none exists yet; do not add without request).
+- Token counting helps with prompt size control.
+
+## Security
+- CORS restricted to frontend origin (set at deploy). Preserve origin checks when modifying.
+- Managed identity for Azure OpenAI / Search; do not introduce API key storage unless explicitly required.
+
+## Extension Points
+- Middleware: Add via Fastify plugin under plugins folder.
+- Retrieval strategies: Introduce new retriever module wrapping Azure AI Search or Qdrant queries; select via env gating.
+
+## Troubleshooting
+- Missing search results: Confirm `AZURE_AISEARCH_ENDPOINT` or `QDRANT_URL` not both empty.
+- Auth errors: Validate managed identity role assignments completed (Bicep handles; during early provisioning there may be propagation delay).
+
+This file overrides root `AGENTS.md` for context within `src/backend`.
diff --git a/src/frontend/AGENTS.md b/src/frontend/AGENTS.md
@@ -0,0 +1,40 @@
+# Frontend (Chat UI)
+Lit + Vite web client providing the chat interface to the backend RAG API.
+
+## Overview
+- Dev server: Vite (port 8000).
+- Build: Outputs to `dist` (consumed by Azure Static Web Apps on deploy).
+- API Proxy (dev): `/chat` proxied to `http://127.0.0.1:3000` via `vite.config.ts`.
+- Runtime backend base URL injected at build through env var `BACKEND_API_URI` -> `VITE_BACKEND_API_URI`.
+
+## Key Dependencies
+- `lit` (web components).
+- `@microsoft/ai-chat-protocol` for standardized chat payloads.
+
+## Scripts
+```
+npm run dev     # Start Vite dev server on :8000
+npm run build   # Production build (with code splitting and vendor chunk)
+npm run watch   # Rebuild on changes (non-minified)
+npm run lint    # lit-analyzer
+npm run clean   # Remove dist
+```
+
+## Coding Guidelines
+- Use Lit reactive properties & templates; keep components small and cohesive.
+- Avoid introducing global state libraries unless necessary; prefer context via custom elements.
+- Keep environment-specific values behind `import.meta.env` (already handled for backend URL).
+
+## Performance
+- Vite config manually chunks vendor modules. When adding new large deps, confirm chunking still optimal.
+- Source maps enabled; remove only if size constraints arise.
+
+## Security
+- Do not expose secrets; only pass public endpoints through `VITE_*` env variables.
+- Sanitize any dynamic content rendered from AI responses if adding rich rendering beyond plain text.
+
+## Troubleshooting
+- Wrong API URL: Confirm build hook in root `azure.yaml` sets `BACKEND_API_URI` before `npm run build` for deployment.
+- CORS errors: Ensure backend allowed origins include deployed Static Web App URI.
+
+This file overrides root `AGENTS.md` for context within `src/frontend`.
diff --git a/src/ingestion/AGENTS.md b/src/ingestion/AGENTS.md
@@ -0,0 +1,48 @@
+# Ingestion Service
+Fastify service for document ingestion (PDF upload) and embedding generation into Azure AI Search or Qdrant.
+
+## Overview
+- Port: 3001.
+- Upload Endpoint: `/documents` (multipart form field `file`).
+- Responsibilities: Accept PDF files, parse (pdf-parse), produce embeddings via Azure OpenAI, upsert vectors into selected store.
+
+## Key Dependencies
+- Fastify + plugins (`@fastify/multipart`, `@fastify/cors`, `@fastify/autoload`, `@fastify/sensible`).
+- PDF parsing: `pdf-parse`.
+- LangChain / Vector: `@langchain/community`, `@langchain/qdrant`, `@azure/search-documents`, `@azure/identity`.
+- Env mgmt: `dotenv`.
+
+## Scripts
+```
+npm run dev         # Build + watch + start (debug)
+npm run build       # Compile TypeScript
+npm start           # Production start
+npm run docker:build  # docker build --tag ingestion --file ./Dockerfile ../..
+npm run docker:run    # Run container exposing 3001
+npm run clean       # Remove dist
+```
+
+## Environment Variables
+- AZURE_OPENAI_API_* (endpoint, version, deployment names, model names)
+- AZURE_AISEARCH_ENDPOINT or QDRANT_URL (mutually exclusive usage)
+- AZURE_CLIENT_ID (managed identity for auth)
+
+## Data Flow
+1. Receive PDF via multipart.
+2. Extract text (pdf-parse).
+3. Chunk + embed (LangChain embeddings with specified model).
+4. Upsert to chosen vector DB.
+
+## Coding Guidelines
+- Keep parsing & chunking modular (add new file format handlers as separate utilities rather than modifying core handler heavily).
+- Validate file type (if adding more formats) before processing.
+
+## Security
+- Limit accepted content types to PDFs (enforce if extending) to reduce attack surface.
+- Managed identity for Azure resources.
+
+## Troubleshooting
+- 415 / parsing errors: Ensure uploaded file is a valid PDF.
+- Empty vector store: Check logs for embedding errors (model deployment names env mismatch).
+
+This file overrides root `AGENTS.md` for context within `src/ingestion`.
diff --git a/trainer/AGENTS.md b/trainer/AGENTS.md
@@ -0,0 +1,47 @@
+# Trainer Proxy & Materials
+Support assets and proxy service enabling workshop trainers to share a single Azure OpenAI instance with attendees.
+
+## Overview
+- Proxy service exposes Azure OpenAI-compatible endpoints; attendees point their environment to proxy URL before provisioning (`AZURE_OPENAI_URL`).
+- Slides + workshop content referenced (hosted externally) but source for slides/workshop lives under `docs/` at repo root.
+
+## Key Files
+- `azure.yaml`: Defines single `openai-proxy` Container App service.
+- `Dockerfile`: Multi-stage build for Fastify proxy.
+- `package.json`: Fastify + http proxy dependencies.
+- `README.md`: Deployment & usage instructions for proxy and capacity guidance.
+
+## Scripts
+```
+npm run dev     # Build + watch + start (debug)
+npm run build   # Compile TypeScript
+npm start       # Production fastify start
+npm run docker:build  # docker build --tag proxy .
+npm run docker:run    # Run on :3000
+```
+
+## Deployment (Proxy)
+```
+azd auth login
+azd env new openai-trainer
+azd env set AZURE_OPENAI_LOCATION <location?>   # default swedencentral
+azd env set AZURE_OPENAI_CAPACITY <tokens_per_minutes?>  # default 5 (increase for class size)
+azd up
+```
+Share resulting Container App URL; attendees set:
+```
+azd env set AZURE_OPENAI_URL <proxy_url>
+```
+
+## Constraints / Considerations
+- Low default capacity to avoid quota deployment failures; adjust after deployment for > minimal class sizes (e.g., 200 TPM for ~50 attendees suggested in README).
+- Future TODO (root `TODO`): event key restriction — do not implement unless requested.
+
+## Security
+- Treat proxy endpoint as semi-public once shared; consider adding auth or key gating if extending.
+
+## Troubleshooting
+- Throughput errors: Increase model capacity in Azure OpenAI portal and redeploy or update deployment.
+- Attendee failures: Verify they set `AZURE_OPENAI_URL` before `azd up`.
+
+This file overrides root `AGENTS.md` within `trainer/`.
PATCH

echo "Gold patch applied."
