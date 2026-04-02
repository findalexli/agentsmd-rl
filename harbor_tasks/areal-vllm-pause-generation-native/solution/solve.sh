#!/usr/bin/env bash
set -euo pipefail

FILE="areal/engine/vllm_ext/areal_vllm_server.py"

# Idempotency check: if llm.pause_generation already appears, patch is applied
if grep -q 'llm\.pause_generation' "$FILE"; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/areal/engine/vllm_ext/areal_vllm_server.py b/areal/engine/vllm_ext/areal_vllm_server.py
index 46f0df37a..50dd06dff 100644
--- a/areal/engine/vllm_ext/areal_vllm_server.py
+++ b/areal/engine/vllm_ext/areal_vllm_server.py
@@ -1,7 +1,6 @@
 import asyncio
 import logging
 from http import HTTPStatus
-from typing import TYPE_CHECKING

 import uvloop
 from fastapi import APIRouter, Depends, Request
@@ -19,16 +18,10 @@
 from vllm.logger import init_logger
 from vllm.lora.request import LoRARequest
 from vllm.utils.argparse_utils import FlexibleArgumentParser
-from vllm.v1.engine import EngineCoreOutput, EngineCoreOutputs, FinishReason
-from vllm.v1.engine.core import EngineCore
-from vllm.v1.metrics.stats import LoRARequestStates
-from vllm.v1.request import RequestStatus

 # AReaL's own router for custom endpoints (replaces vLLM's removed global router)
 router = APIRouter()

-if TYPE_CHECKING:
-    from vllm.v1.engine.output_processor import RequestState

 logger = init_logger("areal_vllm_server")
 logger.setLevel(logging.INFO)
@@ -170,10 +163,14 @@ def _register_runtime_lora_name(
 async def areal_update_weight(request: UpdateWeightsRequest, raw_request: Request):
     logger.info(f"API server starts areal_update_weight, {request.model_path}")
     llm = raw_request.app.state.engine_client
-    ret_list = await llm.engine_core.call_utility_async(
-        "areal_injected_update_weight",
-        request.model_path,
-    )
+    await llm.pause_generation(wait_for_inflight_requests=False, clear_cache=True)
+    try:
+        ret_list = await llm.collective_rpc(
+            "areal_update_weights",
+            args=(request.model_path,),
+        )
+    finally:
+        await llm.resume_generation()
     return build_response(ret_list)


@@ -185,13 +182,21 @@ async def areal_update_weight_lora(
         f"API server starts areal_update_weight_lora, lora_model_path-{request.lora_model_path}, lora_name-{request.lora_name}, lora_int_id-{request.lora_int_id}, base_model_name-{request.base_model_name}"
     )
     llm = raw_request.app.state.engine_client
-    ret_list = await llm.engine_core.call_utility_async(
-        "areal_injected_update_weight_lora",
-        request.lora_model_path,
-        request.lora_name,
-        request.lora_int_id,
-        request.base_model_name,
-    )
+    await llm.pause_generation(wait_for_inflight_requests=False, clear_cache=True)
+
+    try:
+        ret_list = await llm.collective_rpc(
+            "areal_update_weights_lora",
+            args=(
+                request.lora_model_path,
+                request.lora_name,
+                request.lora_int_id,
+                request.base_model_name,
+            ),
+        )
+    finally:
+        await llm.resume_generation()
+
     return build_response(ret_list)


@@ -199,9 +204,11 @@ async def areal_update_weight_lora(
 async def areal_update_weight_xccl(raw_request: Request):
     logger.info("API server starts areal_update_weight_xccl")
     llm = raw_request.app.state.engine_client
-    ret_list = await llm.engine_core.call_utility_async(
-        "areal_injected_update_weight_xccl",
-    )
+    await llm.pause_generation(wait_for_inflight_requests=False, clear_cache=True)
+    try:
+        ret_list = await llm.collective_rpc("areal_update_weight_xccl")
+    finally:
+        await llm.resume_generation()
     return build_response(ret_list)


@@ -211,16 +218,20 @@ async def areal_update_weight_lora_xccl(
 ):
     logger.info("API server starts areal_update_weight_lora_xccl")
     llm = raw_request.app.state.engine_client
-    ret_list = await llm.engine_core.call_utility_async(
-        "areal_injected_update_weight_lora_xccl",
-    )
-    if all(success for success, _ in ret_list):
-        _register_runtime_lora_name(
-            raw_request.app,
-            lora_name=request.lora_name,
-            lora_int_id=request.lora_int_id,
-            base_model_name=request.base_model_name,
-        )
+    await llm.pause_generation(wait_for_inflight_requests=False, clear_cache=True)
+
+    try:
+        ret_list = await llm.collective_rpc("areal_update_weight_lora_xccl")
+        if all(success for success, _ in ret_list):
+            _register_runtime_lora_name(
+                raw_request.app,
+                lora_name=request.lora_name,
+                lora_int_id=request.lora_int_id,
+                base_model_name=request.base_model_name,
+            )
+    finally:
+        await llm.resume_generation()
+
     return build_response(ret_list)


@@ -295,13 +306,19 @@ async def areal_pause_generation(raw_request: Request):
     llm = raw_request.app.state.engine_client
     # Abort all running and waiting requests
     _generation_run_event.clear()
-    await llm.engine_core.call_utility_async("abort_all_reqs")
+    await llm.pause_generation(
+        wait_for_inflight_requests=False,
+        clear_cache=True,
+    )
+
     return to_json_response(True, "Generation paused and all requests aborted")


 @router.post("/areal_continue_generation")
 async def areal_continue_generation(raw_request: Request):
     logger.info("API server starts areal_continue_generation")
+    llm = raw_request.app.state.engine_client
+    await llm.resume_generation()
     _generation_run_event.set()
     return to_json_response(True, "Generation continued")

@@ -335,122 +352,6 @@ async def create_completion(request: CompletionRequest, raw_request: Request):
     return response


-# engine core related hook functions
-def abort_all_reqs(self):
-    """Abort all running and waiting requests and clean up resources."""
-    scheduler = self.scheduler
-    abort_lists = list(scheduler.running) + list(scheduler.waiting)
-
-    if not abort_lists:
-        # No requests to abort
-        success = scheduler.reset_prefix_cache()
-        if not success:
-            raise RuntimeError(
-                f"Prefix cache must be reset to prevent kv cache pollution! Reset: {success}"
-            )
-        return
-
-    client_outputs = {}
-    for req in abort_lists:
-        engine_output = EngineCoreOutput(
-            request_id=req.request_id,
-            new_token_ids=[],
-            finish_reason=FinishReason.ABORT,
-            new_logprobs=None,
-            new_prompt_logprobs_tensors=None,
-            stop_reason=None,
-        )
-        if req.client_index not in client_outputs:
-            client_outputs[req.client_index] = []
-        client_outputs[req.client_index].append(engine_output)
-
-    request_ids = [req.request_id for req in abort_lists]
-    scheduler.finish_requests(request_ids, RequestStatus.FINISHED_ABORTED)
-
-    for client_index, outputs in client_outputs.items():
-        engine_core_outputs = EngineCoreOutputs(outputs=outputs)
-        self.output_queue.put_nowait((client_index, engine_core_outputs))
-
-    success = scheduler.reset_prefix_cache()
-    if not success:
-        raise RuntimeError(
-            f"Prefix cache must be reset to prevent kv cache pollution! Reset: {success}"
-        )
-
-
-def areal_injected_update_weight(self, path):
-    self.abort_all_reqs()
-    return self.collective_rpc("areal_update_weights", args=(path,))
-
-
-def areal_injected_update_weight_lora(
-    self, lora_model_path, lora_name, lora_int_id, base_model_name
-):
-    self.abort_all_reqs()
-    return self.collective_rpc(
-        "areal_update_weights_lora",
-        args=(
-            lora_model_path,
-            lora_name,
-            lora_int_id,
-            base_model_name,
-        ),
-    )
-
-
-def areal_injected_update_weight_xccl(self):
-    self.abort_all_reqs()
-    return self.collective_rpc("areal_update_weight_xccl")
-
-
-def areal_injected_update_weight_lora_xccl(self):
-    self.abort_all_reqs()
-    return self.collective_rpc("areal_update_weight_lora_xccl")
-
-
-def finish_request(self, req_state: "RequestState"):
-    if req_state.lora_name is None:
-        return
-    lora_stats = self.lora_name_to_stats[req_state.lora_name]
-    # Simply added this if-condition
-    if req_state.request_id in lora_stats.running_requests:
-        lora_stats.running_requests.remove(req_state.request_id)
-
-
-def hook():
-    setattr(EngineCore, "abort_all_reqs", abort_all_reqs)
-    setattr(EngineCore, "areal_injected_update_weight", areal_injected_update_weight)
-    setattr(
-        EngineCore,
-        "areal_injected_update_weight_lora",
-        areal_injected_update_weight_lora,
-    )
-    setattr(
-        EngineCore,
-        "areal_injected_update_weight_xccl",
-        areal_injected_update_weight_xccl,
-    )
-    setattr(
-        EngineCore,
-        "areal_injected_update_weight_lora_xccl",
-        areal_injected_update_weight_lora_xccl,
-    )
-
-    # Patch for LoRARequestStates management in vllm < v0.11.0
-    # This may be removed with vllm >= 0.12.x
-    from areal.utils import pkg_version
-
-    if not pkg_version.is_version_greater_or_equal("vllm", "0.12.0"):
-        setattr(
-            LoRARequestStates,
-            "finish_request",
-            finish_request,
-        )
-
-
-hook()
-
-
 if __name__ == "__main__":
     # NOTE(simon):
     # This section should be in sync with vllm/entrypoints/cli/main.py for CLI

PATCH

echo "Patch applied successfully."
