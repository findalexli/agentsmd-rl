#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prisma

# Idempotent: skip if already applied
if [ -f "packages/cli/src/mcp/README.md" ]; then
    echo "Patch already applied."
    exit 0
fi

# Create the mcp subdirectory
mkdir -p packages/cli/src/mcp

# Move MCP.ts into the mcp directory
mv packages/cli/src/MCP.ts packages/cli/src/mcp/MCP.ts

# Fix relative imports in MCP.ts (now one level deeper)
sed -i "s|from '../package.json'|from '../../package.json'|" packages/cli/src/mcp/MCP.ts
sed -i "s|from './platform/_lib/help'|from '../platform/_lib/help'|" packages/cli/src/mcp/MCP.ts

# Remove PDP MCP tools (Prisma-Postgres-account-status, Create-Prisma-Postgres-Database, Prisma-Login)
python3 - <<'PYEOF'
import re
from pathlib import Path

mcp_file = Path("packages/cli/src/mcp/MCP.ts")
content = mcp_file.read_text()

# Remove the three PDP tool blocks
tools_to_remove = [
    "Prisma-Postgres-account-status",
    "Create-Prisma-Postgres-Database",
    "Prisma-Login",
]

for tool_name in tools_to_remove:
    # Match server.tool('ToolName', ...) blocks including trailing whitespace
    pattern = r"\n    server\.tool\(\s*'" + re.escape(tool_name) + r"'.*?\n    \)\n"
    content = re.sub(pattern, "\n", content, flags=re.DOTALL)

mcp_file.write_text(content)
PYEOF

# Update import in bin.ts
sed -i "s|from './MCP'|from './mcp/MCP'|" packages/cli/src/bin.ts

# Add "MCP" keyword to package.json
python3 - <<'PYEOF'
import json
from pathlib import Path

pkg_path = Path("packages/cli/package.json")
pkg = json.loads(pkg_path.read_text())
keywords = pkg.get("keywords", [])
if "MCP" not in keywords:
    keywords.append("MCP")
    pkg["keywords"] = keywords
pkg_path.write_text(json.dumps(pkg, indent=2) + "\n")
PYEOF

# Create the MCP README
cat > packages/cli/src/mcp/README.md <<'README'
# Prisma MCP

MCP or [Model Context Protocol](https://docs.anthropic.com/en/docs/mcp) allows the Prisma ORM to wrap CLI commands into workflows that work well with LLMs and AI code editors.

## Using Prisma MCP

The Prisma ORM and CLI uses a locally run MCP server that wraps CLI commands like `prisma migrate` or `prisma db` and require local file access to run during development.

A list of MCP tools are in `./MCP.ts`.

### Starting The Server

Start the local CLI MCP server using `npx prisma mcp` or follow the [docs](https://www.prisma.io/docs/postgres/integrations/mcp-server) to add the local MCP Server to your code editor, LLM, or Agent.
README

# Run prettier on the modified file
# Enable corepack and run pnpm install to get dependencies for prettier
corepack enable 2>/dev/null || true
corepack prepare pnpm@9.14.4 --activate 2>/dev/null || true
pnpm install --frozen-lockfile >/dev/null 2>&1 || true
# Format the modified MCP.ts file
pnpm exec prettier --write packages/cli/src/mcp/MCP.ts >/dev/null 2>&1 || true

echo "Patch applied successfully."
