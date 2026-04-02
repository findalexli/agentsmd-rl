#!/usr/bin/env bash
set -euo pipefail

FILE="areal/engine/fsdp_engine.py"

# Idempotency check: if _PendingWeightUpdateBucket already exists, patch was applied
if grep -q '_PendingWeightUpdateBucket' "$FILE"; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/areal/engine/fsdp_engine.py b/areal/engine/fsdp_engine.py
index ba404fa6b..57763e6ab 100644
--- a/areal/engine/fsdp_engine.py
+++ b/areal/engine/fsdp_engine.py
@@ -160,6 +160,14 @@ def to_dict(self) -> dict[str, Any]:
         return {f.name: getattr(self, f.name) for f in dataclasses.fields(self)}


+@dataclasses.dataclass
+class _PendingWeightUpdateBucket:
+    handles: list[Any]
+    fut: Future[None]
+    named_tensors: list[tuple[str, torch.Tensor]]
+    stream: torch.cuda.Stream | None = None
+
+
 class FSDPEngine(TrainEngine):
     def __init__(self, config: TrainEngineConfig):
         self.config = config
@@ -1031,14 +1039,15 @@ def _get_full_tensor(self, param: nn.Parameter) -> torch.Tensor:
                 tensor = tensor.to(current_platform.device_type)
             return tensor

-    def _update_bucket_weights_from_distributed(
+    def _update_bucket_weights_from_distributed_async(
         self,
         meta: WeightUpdateMeta,
         named_tensors: list[tuple[str, nn.Parameter | torch.Tensor]],
-    ):
+        stream: torch.cuda.Stream | None = None,
+    ) -> _PendingWeightUpdateBucket | None:
         # Early exit when chunk size is relatively small
         if not named_tensors:
-            return
+            return None

         param_specs = [
             ParamSpec(
@@ -1067,18 +1076,48 @@ def _update_bucket_weights_from_distributed(
         fut = self.rollout_engine.update_weights_from_distributed(meta, param_specs)

         handles = []
-        for _, tensor in named_tensors:
-            handles.append(
-                dist.broadcast(
-                    tensor, src=0, group=self.weight_update_group, async_op=True
+        if stream is not None:
+            stream.wait_stream(torch.cuda.current_stream())
+            context = torch.cuda.stream(stream)
+        else:
+            context = nullcontext()
+
+        with context:
+            for _, tensor in named_tensors:
+                handles.append(
+                    dist.broadcast(
+                        tensor, src=0, group=self.weight_update_group, async_op=True
+                    )
                 )
-            )
-        for handle in handles:
+
+        return _PendingWeightUpdateBucket(
+            handles=handles,
+            fut=fut,
+            named_tensors=named_tensors,
+            stream=stream,
+        )
+
+    def _wait_pending_weight_update_bucket(
+        self, pending_bucket: _PendingWeightUpdateBucket | None
+    ):
+        if pending_bucket is None:
+            return
+
+        for handle in pending_bucket.handles:
             handle.wait()

-        fut.result()
+        pending_bucket.fut.result()
+        pending_bucket.named_tensors.clear()

-        named_tensors.clear()
+    def _update_bucket_weights_from_distributed(
+        self,
+        meta: WeightUpdateMeta,
+        named_tensors: list[tuple[str, nn.Parameter | torch.Tensor]],
+    ):
+        pending_bucket = self._update_bucket_weights_from_distributed_async(
+            meta, named_tensors
+        )
+        self._wait_pending_weight_update_bucket(pending_bucket)

     def _init_weight_update_from_distributed(self, meta: WeightUpdateMeta):
         assert meta.type == "xccl"
@@ -1116,23 +1155,32 @@ def _init_weight_update_from_distributed(self, meta: WeightUpdateMeta):

     @trace_perf("fsdp_engine.update_weights_from_distributed", category="comm")
     def _update_weights_from_distributed(self, meta: WeightUpdateMeta):
-        """Broadcast parameters (chunked) from rank 0 (FSDP2 compatible)."""
+        """Broadcast parameters with single-pending-bucket pipelining."""

         # Reset weight weight meta with local info
         meta.nccl_master_address = self.weight_update_master_addr
         meta.nccl_master_port = self.weight_update_master_port
         meta.nccl_group_name = self.weight_update_group_name

-        if dist.get_rank() == 0:
+        main_rank = dist.get_rank() == 0
+        if main_rank:
             self.rollout_engine.pause_generation()

         dist.barrier(group=self.cpu_group)

         weight_chunked_mem_size = meta.weight_chunked_mem_mb * 1024 * 1024
-        main_rank = dist.get_rank() == 0
+        broadcast_stream = None
+
+        if (
+            main_rank
+            and current_platform.device_type == "cuda"
+            and torch.cuda.is_available()
+        ):
+            broadcast_stream = torch.cuda.Stream()

         buffer_size = 0
         named_tensors: list[tuple[str, torch.Tensor]] = []
+        pending_bucket: _PendingWeightUpdateBucket | None = None

         if self.config.use_lora:
             # For LoRA, only iterate over trainable LoRA parameters
@@ -1145,29 +1193,50 @@ def _update_weights_from_distributed(self, meta: WeightUpdateMeta):
             # For full model, iterate over all parameters
             param_iterator = self._get_model_name_parameters()

-        for name, param in param_iterator:
-            tensor = self._get_full_tensor(param)
-
-            # Ranks other than 0 only help to get the full tensor
-            if not main_rank:
-                continue
+        try:
+            for name, param in param_iterator:
+                # Ranks other than 0 only help to get the full tensor
+                tensor = self._get_full_tensor(param)
+                if not main_rank:
+                    continue
+
+                tensor_size = tensor.numel() * tensor.element_size()
+                bucket_overflow = (
+                    buffer_size > 0
+                    and tensor_size + buffer_size > weight_chunked_mem_size
+                )
+                if bucket_overflow:
+                    # Only middle buckets need drain+align before the next all-gather.
+                    if pending_bucket is not None:
+                        self._wait_pending_weight_update_bucket(pending_bucket)
+                        pending_bucket = None
+
+                    pending_bucket = self._update_bucket_weights_from_distributed_async(
+                        meta,
+                        named_tensors,
+                        stream=broadcast_stream,
+                    )

-            tensor_size = tensor.numel() * tensor.element_size()
+                    named_tensors = []
+                    buffer_size = 0

-            if tensor_size + buffer_size > weight_chunked_mem_size:
-                self._update_bucket_weights_from_distributed(meta, named_tensors)
-                buffer_size = 0
+                buffer_size += tensor_size
+                named_tensors.append((name, tensor))

-            named_tensors.append((name, tensor))
-            buffer_size += tensor_size
+            if pending_bucket:
+                self._wait_pending_weight_update_bucket(pending_bucket)
+                pending_bucket = None

-        # Process remaining parameters
-        if named_tensors:
-            self._update_bucket_weights_from_distributed(meta, named_tensors)
+            # Process remaining parameters
+            if buffer_size > 0:
+                self._update_bucket_weights_from_distributed(meta, named_tensors)
+        finally:
+            if main_rank and pending_bucket is not None:
+                self._wait_pending_weight_update_bucket(pending_bucket)
+                pending_bucket = None

         dist.barrier(group=self.cpu_group)
-
-        if dist.get_rank() == 0:
+        if main_rank:
             self.rollout_engine.continue_generation()

         current_platform.synchronize()

PATCH

echo "Patch applied successfully."
