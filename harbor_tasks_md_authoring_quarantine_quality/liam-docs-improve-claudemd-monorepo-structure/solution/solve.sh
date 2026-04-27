#!/usr/bin/env bash
set -euo pipefail

cd /workspace/liam

# Idempotency guard
if grep -qF "- **frontend/internal-packages/mcp-server** - MCP server implementation (`@liam-" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -28,13 +28,21 @@ pnpm --filter @liam-hq/agent test
 
 ### Monorepo Structure
 
+#### Applications
 - **frontend/apps/app** - Main Next.js web application (`@liam-hq/app`)
 - **frontend/apps/docs** - Documentation site (`@liam-hq/docs`)
+
+#### Public Packages
 - **frontend/packages/cli** - Command-line tool (`@liam-hq/cli`)
 - **frontend/packages/erd-core** - Core ERD visualization (`@liam-hq/erd-core`)
 - **frontend/packages/schema** - Database schema parser (`@liam-hq/schema`)
 - **frontend/packages/ui** - UI component library (`@liam-hq/ui`)
-- **frontend/packages/github** - GitHub API integration (`@liam-hq/github`)
+
+#### Internal Packages
+- **frontend/internal-packages/agent** - AI agent system using LangGraph (`@liam-hq/agent`)
+- **frontend/internal-packages/db** - Database utilities (`@liam-hq/db`)
+- **frontend/internal-packages/mcp-server** - MCP server implementation (`@liam-hq/mcp-server`)
+
 
 ### Key Technologies
 
PATCH

echo "Gold patch applied."
