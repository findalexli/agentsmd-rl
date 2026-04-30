#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ente

# Idempotency guard
if grep -qF "mobile/apps/photos/AGENTS.md" "mobile/apps/photos/AGENTS.md" && grep -qF "This file provides guidance to Claude, Codex, and any other agent when working w" "mobile/apps/photos/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/mobile/apps/photos/AGENTS.md b/mobile/apps/photos/AGENTS.md
@@ -0,0 +1 @@
+CLAUDE.md
\ No newline at end of file
diff --git a/mobile/apps/photos/CLAUDE.md b/mobile/apps/photos/CLAUDE.md
@@ -1,6 +1,6 @@
 # CLAUDE.md
 
-This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
+This file provides guidance to Claude, Codex, and any other agent when working with code in this repository.
 
 ## Project Philosophy
 
PATCH

echo "Gold patch applied."
