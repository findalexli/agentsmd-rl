#!/usr/bin/env bash
set -euo pipefail

cd /workspace/fizzy

# Idempotency guard
if grep -qF "Use Chrome MCP tools to interact with the running dev app for UI testing and deb" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -144,7 +144,7 @@ Key recurring tasks (via `config/recurring.yml`):
 URL: `http://fizzy.localhost:3006`
 Login: david@37signals.com (passwordless magic link auth - check rails console for link)
 
-Use Chrome MCP tools to interact with the running dev app for UI testing and debugging.``
+Use Chrome MCP tools to interact with the running dev app for UI testing and debugging.
 
 ## Coding style
 
PATCH

echo "Gold patch applied."
