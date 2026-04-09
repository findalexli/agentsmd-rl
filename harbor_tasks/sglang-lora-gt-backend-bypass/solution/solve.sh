#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotent: skip if already applied
if grep -q 'def _is_lora_case' python/sglang/multimodal_gen/test/server/test_server_common.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/python/sglang/multimodal_gen/test/server/test_server_common.py b/python/sglang/multimodal_gen/test/server/test_server_common.py
index 61bf4f5730c2..29d985d21100 100644
--- a/python/sglang/multimodal_gen/test/server/test_server_common.py
+++ b/python/sglang/multimodal_gen/test/server/test_server_common.py
@@ -43,6 +43,14 @@
 logger = init_logger(__name__)


+def _is_lora_case(case: DiffusionTestCase) -> bool:
+    return bool(
+        case.server_args.lora_path
+        or case.server_args.dynamic_lora_path
+        or case.server_args.second_lora_path
+    )
+
+
 @pytest.fixture
 def diffusion_server(case: DiffusionTestCase) -> ServerContext:
     """Start a diffusion server for a single case and tear it down afterwards."""
@@ -65,9 +73,9 @@ def diffusion_server(case: DiffusionTestCase) -> ServerContext:
     sampling_params = case.sampling_params
     extra_args = os.environ.get("SGLANG_TEST_SERVE_ARGS", "")

-    # In GT generation mode, force --backend diffusers
+    # Keep LoRA GT on the normal backend path so adapter state matches CI.
     if os.environ.get("SGLANG_GEN_GT", "0") == "1":
-        if "--backend" not in extra_args:
+        if not _is_lora_case(case) and "--backend" not in extra_args:
             extra_args = "--backend diffusers " + extra_args.strip()

     extra_args += f" --num-gpus {server_args.num_gpus}"
@@ -853,9 +861,8 @@ def test_diffusion_generation(
         # Check if we're in GT generation mode
         is_gt_gen_mode = os.environ.get("SGLANG_GEN_GT", "0") == "1"

-        # Dynamic LoRA loading test - tests LayerwiseOffload + set_lora interaction
-        # Server starts WITHOUT lora_path, then set_lora is called after startup
-        if case.run_lora_dynamic_load_check and not is_gt_gen_mode:
+        # GT generation also needs the dynamic set_lora step before generation.
+        if case.run_lora_dynamic_load_check:
             self._test_dynamic_lora_loading(diffusion_server, case)

         generate_fn = get_generate_fn(

PATCH

echo "Patch applied successfully."
