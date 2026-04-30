#!/usr/bin/env bash
# Gold solution: apply the upstream fix from openai/openai-agents-js#863.
set -euo pipefail

cd /workspace/openai-agents-js

TARGET=".codex/skills/changeset-validation/scripts/changeset-assign-milestone.mjs"

# Idempotency: if the distinctive line from the gold patch is already
# present, the fix has already been applied — exit cleanly.
if grep -q 'const patchTarget = parsed\[parsed.length - 1\];' "${TARGET}"; then
    echo "Gold patch already applied."
    exit 0
fi

git apply <<'PATCH'
diff --git a/.codex/skills/changeset-validation/scripts/changeset-assign-milestone.mjs b/.codex/skills/changeset-validation/scripts/changeset-assign-milestone.mjs
index c22c958e2..5c23d17ab 100755
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

echo "Gold patch applied."
