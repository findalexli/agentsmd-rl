#!/usr/bin/env bash
set -euo pipefail

cd /workspace/linux-mcp-server

# Idempotency guard
if grep -qF "- Extend existing tests using parameterized tests rather than adding new test ca" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,5 @@
+# Linux MCP Server
+
+## Development Guidelines
+
+- Extend existing tests using parameterized tests rather than adding new test cases.
PATCH

echo "Gold patch applied."
