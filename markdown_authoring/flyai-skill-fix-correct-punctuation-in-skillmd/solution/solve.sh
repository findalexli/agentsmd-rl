#!/usr/bin/env bash
set -euo pipefail

cd /workspace/flyai-skill

# Idempotency guard
if grep -qF "- **AI search** (`ai-search`): Semantic search for hotels, flights, etc. Underst" "skills/flyai/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/flyai/SKILL.md b/skills/flyai/SKILL.md
@@ -55,7 +55,7 @@ All commands output **single-line JSON** to `stdout`; errors and hints go to `st
 
 ## Quick Start
 
-1. **Install CLI**：`npm i -g @fly-ai/flyai-cli`
+1. **Install CLI**: `npm i -g @fly-ai/flyai-cli`
 2. **Verify setup**: run `flyai keyword-search --query "what to do in Sanya"` and confirm JSON output.
 3. **List commands**: run `flyai --help`.
 4. **Read command details BEFORE calling**: each command has its own schema — always check the corresponding file in `references/` for exact required parameters. Do NOT guess or reuse formats from other commands.
@@ -76,7 +76,7 @@ flyai config set FLYAI_API_KEY "your-key"
 - **Keyword search** (`keyword-search`): one natural-language query across hotels, flights, attraction tickets, performances, sports events, and cultural activities.
   - **Hotel package**: lodging bundled with extra services.
   - **Flight package**: flight bundled with extra services.
-- **AI search** (`ai-search`): Semantic search for hotels, flights, etc. Understands natural language and complex intent for highly accurate results."
+- **AI search** (`ai-search`): Semantic search for hotels, flights, etc. Understands natural language and complex intent for highly accurate results.
 
 ### Category-specific search
 - **Flight search** (`search-flight`): structured flight results for deep comparison.
PATCH

echo "Gold patch applied."
