#!/usr/bin/env bash
set -euo pipefail

SCHEDULER="/workspace/torch/_inductor/scheduler.py"

# Idempotency: check if the fix is already applied
if grep -q 'and not MixOrderReduction.is_contiguous_node(node2)' "$SCHEDULER" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

cd /workspace
git apply - <<'PATCH'
diff --git a/torch/_inductor/scheduler.py b/torch/_inductor/scheduler.py
index 6e1323ca942a3..55e55a6eda421 100644
--- a/torch/_inductor/scheduler.py
+++ b/torch/_inductor/scheduler.py
@@ -2153,6 +2153,13 @@ def sub_node_can_fuse(
         if not self.scheduler.can_fuse(node1, node2, allow_mix_order_reduction=False):
             return False

+        # Since node1 is from the current mix order reduction, if node1 is
+        # contiguous, the fused node should also be contiguous.
+        if MixOrderReduction.is_contiguous_node(
+            node1
+        ) and not MixOrderReduction.is_contiguous_node(node2):
+            return False
+
         def _get_ancestors(nodes: tuple[BaseSchedulerNode, ...]) -> OrderedSet[str]:
             out = OrderedSet()
             return out.union(*(n.ancestors for n in nodes))

PATCH

echo "Patch applied successfully."
