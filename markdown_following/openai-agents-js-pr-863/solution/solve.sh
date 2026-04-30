#!/usr/bin/env bash
set -euo pipefail

REPO="/workspace/openai-agents-js"
TARGET=".codex/skills/changeset-validation/scripts/changeset-assign-milestone.mjs"

cd "$REPO"

# Idempotency guard: check for the buggy line
grep -q "requiredBump === 'minor' ? (parsed\[1\] ?? parsed\[0\]) : parsed\[0\]" "$TARGET" || {
  echo "Already fixed or unexpected state."
  exit 0
}

git apply <<'PATCH'
diff --git a/.codex/skills/changeset-validation/scripts/changeset-assign-milestone.mjs b/.codex/skills/changeset-validation/scripts/changeset-assign-milestone.mjs
index 8e02f2e..d0f3c7a 100644
--- a/.codex/skills/changeset-validation/scripts/changeset-assign-milestone.mjs
+++ b/.codex/skills/changeset-validation/scripts/changeset-assign-milestone.mjs
@@ -94,8 +94,9 @@ async function assignMilestone(requiredBump) {
     return;
   }

-  const targetEntry =
-    requiredBump === 'minor' ? (parsed[1] ?? parsed[0]) : parsed[0];
+  const patchTarget = parsed[parsed.length - 1];
+  const minorTarget = parsed[1] ?? parsed[0];
+  const targetEntry = requiredBump === 'minor' ? minorTarget : patchTarget;
   if (!targetEntry) {
     console.warn(
       'Milestone assignment skipped (not enough open milestones for selection).',
PATCH

echo "Patch applied successfully."
