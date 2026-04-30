#!/usr/bin/env bash
set -euo pipefail

cd /workspace/meshmonitor

# Idempotency guard
if grep -qF "- Always use context7 when I need code generation, setup or configuration steps," "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,9 +1,10 @@
-- Always use context7 when I need code generation, setup or configuration steps, or
-library/API documentation. This means you should automatically use the Context7 MCP
-tools to resolve library id and get library docs without me having to explicitly ask.
+- Always use context7 when I need code generation, setup or configuration steps, or library/API documentation. This means you should automatically use the Context7 MCP tools to resolve library id and get library docs without me having to explicitly ask.
+- Default admin account is username 'admin' and password 'changeme' . Sometime the password is 'changeme1'
+- use serena MCP for code search and analysis without me explicitly having to ask.
+- use superpowers for planning and workflow management without me having to ask
 - IMPORTANT: Review docs/ARCHITECTURE_LESSONS.md before implementing node communication, state management, backup/restore, asynchronous operations, or database changes. These patterns prevent common mistakes.
 - Only the backend talks to the Node. the Frontend never talks directly to the node.
-- Default admin account is username 'admin' and password 'changeme' . Sometime the password is 'changeme1'
+
 
 ## Multi-Database Architecture (SQLite/PostgreSQL/MySQL)
 
PATCH

echo "Gold patch applied."
