#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ente

# Idempotency guard
if grep -qF "- @~/.claude/ente-photos-instructions.md" "mobile/apps/photos/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/mobile/apps/photos/CLAUDE.md b/mobile/apps/photos/CLAUDE.md
@@ -208,4 +208,4 @@ lib/
 - Always follow existing code conventions and patterns in neighboring files
 
 # Individual Preferences
-- @~/.claude/my-project-instructions.md
+- @~/.claude/ente-photos-instructions.md
PATCH

echo "Gold patch applied."
