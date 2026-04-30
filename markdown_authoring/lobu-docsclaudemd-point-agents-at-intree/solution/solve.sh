#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lobu

# Idempotency guard
if grep -qF "The live Owletto MCP server, ClientSDK, sandbox, and tool registry are in `packa" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -3,3 +3,7 @@
 ## Local-only references
 
 - `../owletto` (i.e. `/Users/burakemre/Code/owletto`) is the Owletto source repo. The OpenClaw memory plugin published as `@lobu/owletto-openclaw` lives in `packages/openclaw-plugin` there.
+
+## Owletto
+
+The live Owletto MCP server, ClientSDK, sandbox, and tool registry are in `packages/owletto-backend/` of this repo. The prod `summaries-app-owletto-app` image is built from there (`docker/app/Dockerfile`). Any question about Owletto behavior — MCP tools, instructions, sandbox, SDK, auth — is answered from that path.
PATCH

echo "Gold patch applied."
