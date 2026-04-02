#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Check if already applied (look for the renamed method)
if grep -q '_validate_rid_not_in_flight' python/sglang/srt/managers/tokenizer_manager.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/python/sglang/srt/entrypoints/http_server.py b/python/sglang/srt/entrypoints/http_server.py
index 44f8bf72a14e..4dd3b414e7d0 100644
--- a/python/sglang/srt/entrypoints/http_server.py
+++ b/python/sglang/srt/entrypoints/http_server.py
@@ -512,11 +512,7 @@ async def health_generate(request: Request) -> Response:
     sampling_params = {"max_new_tokens": 1, "temperature": 0.0}
     rid = f"{HEALTH_CHECK_RID_PREFIX}_{time.time()}"

-    if _global_state.tokenizer_manager.is_image_gen:
-        gri = _global_state.tokenizer_manager.get_image_gen_health_check_request(
-            rid, sampling_params
-        )
-    elif _global_state.tokenizer_manager.is_generation:
+    if _global_state.tokenizer_manager.is_generation:
         gri = GenerateReqInput(
             rid=rid,
             input_ids=[0],
diff --git a/python/sglang/srt/managers/io_struct.py b/python/sglang/srt/managers/io_struct.py
index 139a588aeebf..0aa25ea92504 100644
--- a/python/sglang/srt/managers/io_struct.py
+++ b/python/sglang/srt/managers/io_struct.py
@@ -21,6 +21,7 @@
 import copy
 import uuid
 from abc import ABC
+from collections import Counter
 from dataclasses import dataclass, field
 from enum import Enum
 from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union
@@ -58,6 +59,15 @@ def regenerate_rid(self):
             self.rid = uuid.uuid4().hex
         return self.rid

+    def _validate_rid_uniqueness(self):
+        """Validate that request IDs within a batch are unique."""
+        if isinstance(self.rid, list) and len(set(self.rid)) != len(self.rid):
+            counts = Counter(self.rid)
+            duplicates = [rid for rid, count in counts.items() if count > 1]
+            raise ValueError(
+                f"Duplicate request IDs detected within the request: {duplicates}"
+            )
+

 @dataclass
 class BaseBatchReq(ABC):
@@ -276,6 +286,8 @@ def normalize_batch_and_arguments(self):
         else:
             self._normalize_batch_inputs()

+        self._validate_rid_uniqueness()
+
     def _validate_inputs(self):
         """Validate that the input configuration is valid."""
         if (
@@ -853,6 +865,8 @@ def normalize_batch_and_arguments(self):

             self._normalize_lora_paths(self.batch_size)

+        self._validate_rid_uniqueness()
+
     def _normalize_lora_paths(self, num):
         """Normalize LoRA paths for batch processing."""
         if self.lora_path is not None:
diff --git a/python/sglang/srt/managers/tokenizer_manager.py b/python/sglang/srt/managers/tokenizer_manager.py
index 1d52c9013cf2..871a89c49a73 100644
--- a/python/sglang/srt/managers/tokenizer_manager.py
+++ b/python/sglang/srt/managers/tokenizer_manager.py
@@ -132,6 +132,8 @@ class ReqState:
     finished: bool
     event: asyncio.Event
     obj: Union[GenerateReqInput, EmbeddingReqInput]
+
+    # For performance metrics
     time_stats: APIServerReqTimeStats
     last_completion_tokens: int = 1
     ttft_observed: bool = False
@@ -216,9 +218,6 @@ def __init__(
         # Init metric collector and watchdog
         self.init_metric_collector_watchdog()

-        if self.enable_metrics:
-            start_cpu_monitor_thread("tokenizer")
-
         # Init request dispatcher
         self.init_request_dispatcher()

@@ -231,7 +230,6 @@ def init_model_config(self):
         self.served_model_name = server_args.served_model_name
         self.model_config = model_config_class.from_server_args(server_args)
         self.is_generation = self.model_config.is_generation
-        self.is_image_gen = getattr(self.model_config, "is_image_gen", False)
         self.context_len = self.model_config.context_len
         self.image_token_id = self.model_config.image_token_id
         self.max_req_input_len = None  # Will be set later in engine.py
@@ -339,10 +337,6 @@ def init_running_status(self):
         self.gracefully_exit = False
         self.last_receive_tstamp = real_time()

-        # For load balancing
-        self.current_load = 0
-        self.current_load_lock = asyncio.Lock()
-
         # Session
         self.session_futures = {}  # session_id -> asyncio event

@@ -441,6 +435,8 @@ def init_metric_collector_watchdog(self):
                 collect_tokens_histogram=self.server_args.collect_tokens_histogram,
             )

+            start_cpu_monitor_thread("tokenizer")
+
         if self.server_args.gc_warning_threshold_secs > 0.0:
             configure_gc_warning(self.server_args.gc_warning_threshold_secs)
         self.soft_watchdog = Watchdog.create(
@@ -489,7 +485,7 @@ async def generate_request(
         # Normalize the request
         obj.normalize_batch_and_arguments()
         self._set_default_priority(obj)
-        self._validate_rid(obj)
+        self._validate_rid_not_in_flight(obj)

         if isinstance(obj, GenerateReqInput) and obj.routed_dp_rank is not None:
             dp_size = self.server_args.dp_size
@@ -771,20 +767,16 @@ async def _tokenize_one_request(
             obj, input_text, input_ids, input_embeds, mm_inputs, token_type_ids
         )

-    def _validate_rid(self, obj: Union[GenerateReqInput, EmbeddingReqInput]) -> None:
-        """Validate the request ID (rid) uniqueness."""
-        rid = obj.rid
-        if rid is None:
+    def _validate_rid_not_in_flight(
+        self, obj: Union[GenerateReqInput, EmbeddingReqInput]
+    ) -> None:
+        """Validate that request IDs are not already in flight."""
+        if obj.rid is None:
             return
-        ids = rid if isinstance(rid, list) else [rid]
-        if len(ids) != len(set(ids)):
-            raise ValueError(
-                f"Duplicate request IDs detected within the request: {ids}"
-            )
-
-        for i in ids:
-            if i in self.rid_to_state:
-                raise ValueError(f"Duplicate request ID detected: {i}")
+        rids = obj.rid if isinstance(obj.rid, list) else [obj.rid]
+        conflicts = set(rids) & self.rid_to_state.keys()
+        if conflicts:
+            raise ValueError(f"Duplicate request IDs detected: {list(conflicts)}")

     def _validate_one_request(
         self, obj: Union[GenerateReqInput, EmbeddingReqInput], input_ids: List[int]
@@ -2312,14 +2304,14 @@ def _req_stats_init(

         external_trace_header = None
         if self.server_args.enable_trace:
-            if request:
-                external_trace_header = extract_trace_headers(request.headers)
-                obj.external_trace_header = external_trace_header
-            elif obj.external_trace_header:
-                # When the request comes form the rust grpc server or Engine there isn't a
+            if obj.external_trace_header:
+                # When the request comes from the rust grpc server or Engine there isn't a
                 # real request object but we still need to propagate the trace context from
                 # the trace context that is explicitly passed in
                 external_trace_header = obj.external_trace_header
+            elif request:
+                external_trace_header = extract_trace_headers(request.headers)
+                obj.external_trace_header = external_trace_header

         if not hasattr(obj, "is_single") or obj.is_single:
             time_stats = APIServerReqTimeStats(disagg_mode=self.disaggregation_mode)

PATCH

echo "Patch applied successfully."
