#!/usr/bin/env bash
set -euo pipefail

cd /workspace/infrahub

# Idempotency guard
if grep -qF "Responses must be direct and substantive. Do not use filler phrases, compliments" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -2,12 +2,30 @@
 
 Infrahub is a graph-based infrastructure data management platform by OpsMill. It combines Git-like branching and version control with a flexible graph database (Neo4j) and a modern UI/API layer.
 
+## Conversation Style
+
+Responses must be direct and substantive. Do not use filler phrases, compliments, or social pleasantries.
+
+**Prohibited phrases** (including variations):
+
+- "You're right", "You're absolutely right", "Great question", "Good idea"
+- "I apologize", "I'm sorry", "Sorry about that"
+- "Let me explain", "Let me walk you through", "I'd be happy to"
+
+**Required behavior:**
+
+- Do not use introductory or transitional filler of any kind
+- Get to the point immediately — no preamble
+- Challenge ideas and assumptions when warranted
+- Ask clarifying questions rather than guessing intent
+- Offer direct criticism when an approach has flaws
+
 ## Tech Stack
 
 - **Backend:** Python 3.12, FastAPI 0.121.1, Neo4j 5.28, Pydantic 2.10
-- **Frontend:** TypeScript 5.9, React 19.2, Vite 7.2, Tailwind CSS 4.1
-- **Testing:** pytest 7.4, Vitest 4.0, Playwright 1.56
-- **Linting:** ruff 0.14.5, mypy 1.15, Biome 2.3
+- **Frontend:** TypeScript 5.9, React 19.2, Vite 7.3, Tailwind CSS 4.1
+- **Testing:** pytest 9.0, Vitest 4.0, Playwright 1.56
+- **Linting:** ruff 0.15, mypy 1.15, Biome 2.3
 - **Package Managers:** uv (Python), npm (Frontend)
 - **Task Runner:** Invoke 2.2.0
 
PATCH

echo "Gold patch applied."
