#!/usr/bin/env bash
set -euo pipefail

cd /workspace/villa

# Idempotency guard
if grep -qF "This file defines how automated agents (Codex, Claude, chat-based coding agents," "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,6 +1,6 @@
 # AGENTS.md
 
-This file defines how automated agents (Codex, Claude, chat-based coding agents, CI bots, etc.) should operate inside the **`villa/`** monorepo.
+This file defines how automated agents (Codex, Claude, chat-based coding agents, CI bots, etc.) should operate inside this monorepo.
 
 The repo contains multiple subprojects with different languages, runtimes, and constraints. **Do not assume one “global” build/run workflow applies everywhere.** Instead:
 
PATCH

echo "Gold patch applied."
