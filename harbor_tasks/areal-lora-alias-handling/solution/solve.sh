#!/usr/bin/env bash
set -euo pipefail
cd /workspace/AReaL

FILE="areal/engine/vllm_ext/areal_vllm_server.py"

# Idempotent: skip if already applied
grep -q '_register_runtime_lora_name' "$FILE" && exit 0

git apply - <<'PATCH'
diff --git a/areal/engine/vllm_ext/areal_vllm_server.py b/areal/engine/vllm_ext/areal_vllm_server.py
index ba0228126..1cd949c16 100644
--- a/areal/engine/vllm_ext/areal_vllm_server.py
+++ b/areal/engine/vllm_ext/areal_vllm_server.py
@@ -20,6 +20,7 @@
     ErrorResponse,
     OpenAIBaseModel,
 )
+from vllm.lora.request import LoRARequest
 from vllm.entrypoints.utils import cli_env_setup, load_aware_call, with_cancellation
 from vllm.logger import init_logger
 from vllm.utils.argparse_utils import FlexibleArgumentParser
@@ -114,6 +115,61 @@ def build_response(ret_list):
     return to_json_response(success, message)


+def _infer_runtime_lora_path(serving_models, lora_name: str, lora_int_id: int) -> str:
+    existing = serving_models.lora_requests.get(lora_name)
+    if existing is not None and getattr(existing, "lora_path", ""):
+        return existing.lora_path
+    for request in serving_models.lora_requests.values():
+        if getattr(request, "lora_int_id", None) == lora_int_id and getattr(
+            request, "lora_path", ""
+        ):
+            return request.lora_path
+    # Runtime XCCL updates do not come with a filesystem path. Use a stable
+    # synthetic path so vLLM can still construct a LoRARequest for routing.
+    return f"xccl://{lora_name}"
+
+
+def _register_runtime_lora_name(
+    app,
+    *,
+    lora_name: str,
+    lora_int_id: int,
+    base_model_name: str | None,
+) -> None:
+    serving_models = getattr(app.state, "openai_serving_models", None)
+    if serving_models is None:
+        logger.warning(
+            "openai_serving_models missing; skip runtime LoRA registration for %s",
+            lora_name,
+        )
+        return
+
+    requests = serving_models.lora_requests
+    runtime_lora_path = _infer_runtime_lora_path(
+        serving_models, lora_name, lora_int_id
+    )
+
+    # Keep at most one public name per adapter id so /v1/models and request
+    # routing reflect the current versioned adapter name.
+    for name, request in list(requests.items()):
+        if getattr(request, "lora_int_id", None) == lora_int_id and name != lora_name:
+            del requests[name]
+
+    lora_request = LoRARequest(
+        lora_name=lora_name,
+        lora_int_id=lora_int_id,
+        lora_path=runtime_lora_path,
+    )
+    if base_model_name is not None:
+        lora_request.base_model_name = base_model_name
+    requests[lora_name] = lora_request
+    logger.info(
+        "Registered runtime LoRA adapter name '%s' for adapter id %s",
+        lora_name,
+        lora_int_id,
+    )
+
+
 @router.post("/areal_update_weights")
 async def update_weight(request: UpdateWeightsRequest, raw_request: Request):
     logger.info(f"API server starts update_weight, {request.model_path}")
@@ -160,24 +216,12 @@ async def update_weight_lora_xccl(
     ret_list = await llm.engine_core.call_utility_async(
         "areal_injected_update_weight_lora_xccl",
     )
-    # Only touch the registry after weights are actually updated
-    models_obj = raw_request.app.state.openai_serving_models
-    new_name = request.lora_name
-    lora_id = request.lora_int_id
-    for old_name, req in list(models_obj.lora_requests.items()):
-        if req.lora_int_id == lora_id:
-            del models_obj.lora_requests[old_name]
-            req.lora_name = new_name
-            models_obj.lora_requests[new_name] = req
-            logger.info(
-                f"Updated LoRA name of openai_serving_models "
-                f"from {old_name} -> {new_name}"
-            )
-            break
-    else:
-        logger.warning(
-            f"LoRA adapter with int_id={lora_id} not found in "
-            f"openai_serving_models.lora_requests"
+    if all(success for success, _ in ret_list):
+        _register_runtime_lora_name(
+            raw_request.app,
+            lora_name=request.lora_name,
+            lora_int_id=request.lora_int_id,
+            base_model_name=request.base_model_name,
         )
     return build_response(ret_list)

PATCH
