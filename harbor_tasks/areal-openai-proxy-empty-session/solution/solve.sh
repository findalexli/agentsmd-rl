#!/usr/bin/env bash
set -euo pipefail

cd /workspace/AReaL

# Idempotency check: if the fix is already applied, skip
if grep -q 'has no interactions' areal/experimental/openai/proxy/workflow.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/areal/experimental/openai/proxy/workflow.py b/areal/experimental/openai/proxy/workflow.py
index c51b489d9..e1aabcd96 100644
--- a/areal/experimental/openai/proxy/workflow.py
+++ b/areal/experimental/openai/proxy/workflow.py
@@ -196,13 +196,18 @@ async def arun_episode(
                 style=self.export_style,
             )

-            # Record stats
-            last_id = list(interactions.keys())[-1] if interactions else None
-            if last_id and interactions:
-                last_reward = interactions[last_id].reward
-                stats_tracker.get(workflow_context.stat_scope()).scalar(
-                    reward=last_reward
+            # Return None if no interactions (empty session — user never sent chat/completions)
+            if not interactions:
+                logger.warning(
+                    f"Session {session_info.session_id} has no interactions, "
+                    "trajectory will be rejected."
                 )
+                return None
+
+            # Record stats
+            last_id = next(reversed(interactions))
+            last_reward = interactions[last_id].reward
+            stats_tracker.get(workflow_context.stat_scope()).scalar(reward=last_reward)
             return interactions

         # ---- Normal mode (inline / subproc) ----

PATCH

echo "Patch applied successfully."
