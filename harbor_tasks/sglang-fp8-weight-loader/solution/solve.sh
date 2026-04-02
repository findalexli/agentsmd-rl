#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

TARGET="python/sglang/srt/models/qwen3_next.py"

# Idempotency: check if fix is already applied
if grep -q '_override_weight_loader' "$TARGET" 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/python/sglang/srt/models/qwen3_next.py b/python/sglang/srt/models/qwen3_next.py
index c0bf8026179b..7e3862a8a61b 100644
--- a/python/sglang/srt/models/qwen3_next.py
+++ b/python/sglang/srt/models/qwen3_next.py
@@ -135,11 +135,11 @@ class Qwen3GatedDeltaNet(nn.Module):

         # Override weight_loader for packed checkpoint format.
         # Must capture original_loader BEFORE overwriting.
-        self.in_proj_qkvz.weight.weight_loader = self._make_packed_weight_loader(
-            self.in_proj_qkvz
+        self._override_weight_loader(
+            self.in_proj_qkvz, self._make_packed_weight_loader(self.in_proj_qkvz)
         )
-        self.in_proj_ba.weight.weight_loader = self._make_packed_weight_loader(
-            self.in_proj_ba
+        self._override_weight_loader(
+            self.in_proj_ba, self._make_packed_weight_loader(self.in_proj_ba)
         )

         # Conv1d weight loader setup
@@ -216,6 +216,19 @@ class Qwen3GatedDeltaNet(nn.Module):
             dt_bias=self.dt_bias,
         )

+    @staticmethod
+    def _override_weight_loader(module, new_loader):
+        """Override weight_loader on a module's weight parameter.
+
+        ModelWeightParameter exposes weight_loader as a read-only property
+        backed by _weight_loader, while plain parameters store it as a
+        regular attribute.  This helper handles both cases."""
+        param = module.weight
+        if hasattr(param, "_weight_loader"):
+            param._weight_loader = new_loader
+        else:
+            param.weight_loader = new_loader
+
     @staticmethod
     def _make_packed_weight_loader(module):
         """Create a weight_loader that does contiguous TP slicing for fused

PATCH

echo "Patch applied successfully."
