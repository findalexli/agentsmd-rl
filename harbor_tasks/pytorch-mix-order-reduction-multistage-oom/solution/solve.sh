#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pytorch

# Check if already applied
if grep -q 'mix_order_reduction_allow_multi_stages' torch/_inductor/config.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/torch/_inductor/codegen/triton.py b/torch/_inductor/codegen/triton.py
index bca5da15e3e22..039b53ee1f2fc 100644
--- a/torch/_inductor/codegen/triton.py
+++ b/torch/_inductor/codegen/triton.py
@@ -5297,6 +5297,7 @@ def inductor_meta_common(cls):
             "store_cubin": config.triton.store_cubin,
             "deterministic": config.deterministic,
             "force_filter_reduction_configs": config.test_configs.force_filter_reduction_configs,
+            "mix_order_reduction_allow_multi_stages": config.triton.mix_order_reduction_allow_multi_stages,
         }

         if config.write_are_deterministic_algorithms_enabled:
diff --git a/torch/_inductor/config.py b/torch/_inductor/config.py
index 9bf1f70fa4c4c..e2fee26f45cc1 100644
--- a/torch/_inductor/config.py
+++ b/torch/_inductor/config.py
@@ -1793,6 +1793,11 @@ class triton:
     # this could be helpful to avoid recompilations in some cases
     mix_order_reduction_non_strict_mode = False

+    # Don't allow multi-stages by default to avoid out of shared memory
+    mix_order_reduction_allow_multi_stages = (
+        os.environ.get("TORCHINDUCTOR_MIX_ORDER_REDUCTION_ALLOW_MULTI_STAGES") == "1"
+    )
+
     enable_tlx_templates: bool = (
         os.environ.get("TORCHINDUCTOR_ENABLE_TLX_TEMPLATES", "0") == "1"
     )
diff --git a/torch/_inductor/runtime/triton_heuristics.py b/torch/_inductor/runtime/triton_heuristics.py
index 61bb640f5a072..2a1447fbf0bda 100644
--- a/torch/_inductor/runtime/triton_heuristics.py
+++ b/torch/_inductor/runtime/triton_heuristics.py
@@ -3776,7 +3776,10 @@ def persistent_reduction(
             # With large rnumel, we have higher chance of out-of-shared memory
             # To avoid adding too much autotuning overhead, we just constrain NUM_STAGES
             # if rnumel is large
-            MAX_NUM_STAGES = 2 if rnumel_hint > 8192 else 3
+            if inductor_meta.get("mix_order_reduction_allow_multi_stages", True):
+                MAX_NUM_STAGES = 2 if rnumel_hint > 8192 else 3
+            else:
+                MAX_NUM_STAGES = 1
             c.kwargs["NUM_STAGES"] = min(max(num_iters // 4, 1), MAX_NUM_STAGES)

             if rnumel_hint <= 1024:

PATCH

echo "Patch applied successfully."
