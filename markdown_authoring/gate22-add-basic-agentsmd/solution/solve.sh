#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gate22

# Idempotency guard
if grep -qF "This document provides coding agents with detailed context about the Gate22 repo" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,40 @@
+# AGENTS.md
+
+This document provides coding agents with detailed context about the Gate22 repository structure, build processes, testing procedures, and conventions.
+
+## Project Overview
+
+Gate22 is an open-source MCP (Model Context Protocol) Gateway and Control Plane for AI governance.
+
+- **Backend**: Python/FastAPI-based service that powers the control plane, MCP hosting, and Virtual MCP servers
+- **Frontend**: Next.js 15 TypeScript application for the management portal
+
+## Repository Structure
+
+```
+gate22/
+├── backend/          # Python backend services
+│   ├── aci/         # Main application package
+│   │   ├── alembic/        # Database migrations
+│   │   ├── cli/            # Internal Admin CLI commands
+│   │   ├── common/         # Shared utilities
+│   │   ├── control_plane/  # FastAPI service for the control plane
+│   │   ├── mcp/            # FastAPI service for the MCP servers (bundle)
+│   │   └── virtual_mcp/    # FastAPI service for the Virtual MCP servers
+│   ├── mcp_servers/         # MCP server definitions
+│   ├── virtual_mcp_servers/ # Virtual MCP server definitions
+│   ├── pyproject.toml       # Python dependencies
+│   └── compose.yml          # Docker Compose configuration
+├── frontend/        # Next.js frontend application
+│   ├── src/
+│   │   ├── app/            # Next.js App Router pages
+│   │   ├── features/       # Feature-based modules
+│   │   ├── components/     # Shared UI components
+│   │   └── lib/            # Utilities and shared logic
+│   └── package.json        # Node.js dependencies
+└── .pre-commit-config.yaml # Pre-commit hooks configuration
+```
+
+## Backend
+
+### Code Style & Quality
PATCH

echo "Gold patch applied."
