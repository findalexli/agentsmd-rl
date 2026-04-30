#!/usr/bin/env bash
set -euo pipefail

cd /workspace/stop-slop

# Idempotency guard
if grep -qF "trigger: Writing prose, editing drafts, reviewing content for AI patterns" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -1,8 +1,9 @@
 ---
 name: stop-slop
 description: Remove AI writing patterns from prose. Use when drafting, editing, or reviewing text to eliminate predictable AI tells.
-trigger: Writing prose, editing drafts, reviewing content for AI patterns
-author: Hardik Pandya (https://hvpandya.com)
+metadata:
+  trigger: Writing prose, editing drafts, reviewing content for AI patterns
+  author: Hardik Pandya (https://hvpandya.com)
 ---
 
 # Stop Slop
PATCH

echo "Gold patch applied."
