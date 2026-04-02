#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vllm

# Idempotency check: if the fix is already applied, skip
if grep -q 'if not torch.is_floating_point(param):' \
    vllm/model_executor/model_loader/weight_utils.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/tests/compile/fullgraph/test_basic_correctness.py b/tests/compile/fullgraph/test_basic_correctness.py
index 3b30a0ffc57f..33645699556b 100644
--- a/tests/compile/fullgraph/test_basic_correctness.py
+++ b/tests/compile/fullgraph/test_basic_correctness.py
@@ -137,6 +137,7 @@ def test_compile_correctness(
             all_args.append(
                 final_args + [f"-cc.mode={mode.name}", "-cc.backend=inductor"]
             )
+            all_envs.append({})

         # inductor will change the output, so we only compare if the output
         # is close, not exactly the same.
@@ -157,6 +158,5 @@ def test_compile_correctness(
     ]:
         all_args.append(final_args + [f"-cc.mode={mode.name}", "-cc.backend=eager"])
         all_envs.append({})
-        all_envs.append({})

-    compare_all_settings(model, all_args * 3, all_envs, method=method)
+    compare_all_settings(model, all_args, all_envs, method=method)
diff --git a/vllm/model_executor/model_loader/weight_utils.py b/vllm/model_executor/model_loader/weight_utils.py
index 5986eb01b675..fbaaef59de0b 100644
--- a/vllm/model_executor/model_loader/weight_utils.py
+++ b/vllm/model_executor/model_loader/weight_utils.py
@@ -1348,40 +1348,47 @@ def initialize_single_dummy_weight(
     high: float = 1e-3,
     seed: int = 1234,
 ) -> None:
-    if torch.is_floating_point(param):
-        if current_platform.is_tpu():
-            generator = torch.Generator(device="cpu")
-            generator.manual_seed(seed)
-            # Note: The param.uniform_ function cannot be used in this
-            # context because it demands more TPU HBM than directly copying
-            # from a CPU tensor.
-            # Note: We avoid using torch.rank_like as it doesn't currently
-            # support the generator argument.
-            param.copy_(
-                (high - low)
-                * torch.rand(
-                    param.shape,
-                    generator=generator,
-                    dtype=param.dtype,
-                    layout=param.layout,
-                    requires_grad=param.requires_grad,
-                    device="cpu",
-                )
-                + low
-            )
-            torch._sync(param)
-            return
+    if not torch.is_floating_point(param):
+        if current_platform.is_rocm():
+            # On ROCm, integer params (e.g. GPTQ qweight/qzeros) are left
+            # as torch.empty() by default, giving non-deterministic values
+            # across processes. Zero them for reproducibility.
+            param.zero_()
+        return

-        generator = torch.Generator(device=param.data.device)
+    if current_platform.is_tpu():
+        generator = torch.Generator(device="cpu")
         generator.manual_seed(seed)
-        if torch.finfo(param.data.dtype).bits < 16:
-            # uniform_ doesn't support < 16-bit datatypes (FP8)
-            dtype = param.data.dtype
-            tmp_param = param.data.to(torch.float16)
-            tmp_param = tmp_param.uniform_(low, high, generator=generator).to(dtype)
-            param.data.copy_(tmp_param)
-        else:
-            param.uniform_(low, high, generator=generator)
+        # Note: The param.uniform_ function cannot be used in this
+        # context because it demands more TPU HBM than directly copying
+        # from a CPU tensor.
+        # Note: We avoid using torch.rank_like as it doesn't currently
+        # support the generator argument.
+        param.copy_(
+            (high - low)
+            * torch.rand(
+                param.shape,
+                generator=generator,
+                dtype=param.dtype,
+                layout=param.layout,
+                requires_grad=param.requires_grad,
+                device="cpu",
+            )
+            + low
+        )
+        torch._sync(param)
+        return
+
+    generator = torch.Generator(device=param.data.device)
+    generator.manual_seed(seed)
+    if torch.finfo(param.data.dtype).bits < 16:
+        # uniform_ doesn't support < 16-bit datatypes (FP8)
+        dtype = param.data.dtype
+        tmp_param = param.data.to(torch.float16)
+        tmp_param = tmp_param.uniform_(low, high, generator=generator).to(dtype)
+        param.data.copy_(tmp_param)
+    else:
+        param.uniform_(low, high, generator=generator)


 def maybe_remap_kv_scale_name(name: str, params_dict: dict) -> str | None:

PATCH

echo "Patch applied successfully."
