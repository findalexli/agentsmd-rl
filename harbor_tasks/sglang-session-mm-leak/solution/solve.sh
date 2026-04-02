#!/usr/bin/env bash
set -euo pipefail

cd /workspace

# Check if already applied (the release_features method is the distinctive marker)
if grep -q 'def release_features' python/sglang/srt/managers/schedule_batch.py; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/python/sglang/srt/managers/schedule_batch.py b/python/sglang/srt/managers/schedule_batch.py
index 9657a72b12e5..6a019496aeb5 100644
--- a/python/sglang/srt/managers/schedule_batch.py
+++ b/python/sglang/srt/managers/schedule_batch.py
@@ -366,6 +366,11 @@ class MultimodalInputs:
     mrope_position_delta: Optional[torch.Tensor] = None
     mrope_position_delta_repeated_cache: Optional[torch.Tensor] = None

+    def release_features(self):
+        """Release feature tensors to free GPU memory."""
+        for item in self.mm_items:
+            item.feature = None
+
     @staticmethod
     def from_dict(obj: dict):
         # Check if MM splitting is enabled
diff --git a/python/sglang/srt/managers/scheduler.py b/python/sglang/srt/managers/scheduler.py
index 8c1e33c19d9b..3e6924807ce1 100644
--- a/python/sglang/srt/managers/scheduler.py
+++ b/python/sglang/srt/managers/scheduler.py
@@ -1674,8 +1674,7 @@ def _maybe_clear_mm_inputs(self, batch: ScheduleBatch) -> None:
             if req.session:
                 continue
             # For non-session requests, clear features and mm_inputs
-            for item in mm_inputs.mm_items:
-                item.feature = None
+            mm_inputs.release_features()
             req.multimodal_inputs = None

     def handle_generate_request(
diff --git a/python/sglang/srt/managers/scheduler_output_processor_mixin.py b/python/sglang/srt/managers/scheduler_output_processor_mixin.py
index 8b6864427faf..864acfcc9b1b 100644
--- a/python/sglang/srt/managers/scheduler_output_processor_mixin.py
+++ b/python/sglang/srt/managers/scheduler_output_processor_mixin.py
@@ -438,11 +438,7 @@ def process_batch_result_decode(
             if req.finished():
                 # delete feature to save memory
                 if req.multimodal_inputs is not None and req.session is None:
-                    for mm_item in req.multimodal_inputs.mm_items:
-                        pixel_values = mm_item.feature
-                        if isinstance(pixel_values, torch.Tensor):
-                            mm_item.feature = None
-                            del pixel_values
+                    req.multimodal_inputs.release_features()
                 self.maybe_collect_routed_experts(req)

                 if self.server_args.disaggregation_decode_enable_offload_kvcache:
diff --git a/python/sglang/srt/managers/session_controller.py b/python/sglang/srt/managers/session_controller.py
index 6b9103027268..836feacb26ae 100644
--- a/python/sglang/srt/managers/session_controller.py
+++ b/python/sglang/srt/managers/session_controller.py
@@ -169,7 +169,14 @@ def create_req(
                 if req.mm_inputs:
                     for item in req.mm_inputs.get("mm_items", []):
                         if item.offsets:
-                            item.offsets = [(s - 1, e - 1) for s, e in item.offsets]
+                            if any(s == 0 for s, _ in item.offsets):
+                                logging.warning(
+                                    "mm_item offset starts at 0 (BOS position), "
+                                    "clamping to 0 after BOS strip"
+                                )
+                            item.offsets = [
+                                (max(0, s - 1), max(0, e - 1)) for s, e in item.offsets
+                            ]

             input_ids = (
                 last_req.origin_input_ids
@@ -284,6 +291,18 @@ def _close(self, session_id: str):
             req = next(iter(session.req_nodes.values())).req
             if not req.finished():
                 req.session = None
+
+        # Release multimodal features held by session requests.
+        # Session reqs skip the normal mm cleanup path (scheduler and
+        # output_processor) so features stay alive until the session closes.
+        seen_mm = set()
+        for node in session.req_nodes.values():
+            mm = node.req.multimodal_inputs
+            if mm is not None and id(mm) not in seen_mm:
+                seen_mm.add(id(mm))
+                mm.release_features()
+            node.req.multimodal_inputs = None
+
         if isinstance(self.tree_cache, SessionAwareCache):
             self.tree_cache.release_session(session_id)
         del self.sessions[session_id]

PATCH

echo "Patch applied successfully."
