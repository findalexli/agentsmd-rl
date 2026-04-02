#!/usr/bin/env bash
set -euo pipefail

FILE="areal/engine/fsdp_utils/optimizer.py"

# Idempotency check: if current_platform is already imported, patch was applied
if grep -q 'from areal.infra.platforms import current_platform' "$FILE"; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/areal/engine/fsdp_utils/optimizer.py b/areal/engine/fsdp_utils/optimizer.py
index 537712e14..0b1c77a04 100644
--- a/areal/engine/fsdp_utils/optimizer.py
+++ b/areal/engine/fsdp_utils/optimizer.py
@@ -11,6 +11,8 @@
 from torch.nn import Parameter
 from torch.optim.adam import adam as _adam_fn

+from areal.infra.platforms import current_platform
+

 def to_precision_dtype(dtype_str: str) -> torch.dtype:
     """
@@ -476,12 +478,11 @@ def refresh_states(self) -> None:

     def _init_streams_and_events(self) -> None:
         """Pre-allocate streams and events for pipeline synchronization."""
-        # TODO: abstract via current_platform for non-CUDA devices
         num_groups = len(self._layer_param_groups)
-        self._h2d_stream = torch.cuda.Stream(device=self.device)
-        self._d2h_stream = torch.cuda.Stream(device=self.device)
-        self._compute_end_events = [torch.cuda.Event() for _ in range(num_groups)]
-        self._h2d_end_events = [torch.cuda.Event() for _ in range(num_groups)]
+        self._h2d_stream = current_platform.Stream(device=self.device)
+        self._d2h_stream = current_platform.Stream(device=self.device)
+        self._compute_end_events = [current_platform.Event() for _ in range(num_groups)]
+        self._h2d_end_events = [current_platform.Event() for _ in range(num_groups)]

     # ------------------------------------------------------------------
     # Per-layer transfer helpers
@@ -583,8 +584,7 @@ def step(self) -> None:
         """Per-layer optimizer step with async prefetch pipeline."""
         h2d_stream = self._h2d_stream
         d2h_stream = self._d2h_stream
-        # TODO: abstract via current_platform for non-CUDA devices
-        compute_stream = torch.cuda.current_stream(self.device)
+        compute_stream = current_platform.current_stream(self.device)
         num_groups = len(self._layer_param_groups)
         layer_states: list[dict[int, ParamTransferState] | None] = [None] * num_groups

@@ -593,7 +593,7 @@ def step(self) -> None:

         # Prefetch initial layers
         for i in range(min(self.prefetch_layers + 1, num_groups)):
-            with torch.cuda.stream(h2d_stream):
+            with current_platform.stream(h2d_stream):
                 layer_states[i] = self._prefetch_layer(i)
                 h2d_stream.record_event(h2d_end_events[i])

@@ -609,13 +609,13 @@ def step(self) -> None:
             # Prefetch next layer (overlaps with D2H below)
             next_idx = i + self.prefetch_layers + 1
             if next_idx < num_groups:
-                with torch.cuda.stream(h2d_stream):
+                with current_platform.stream(h2d_stream):
                     layer_states[next_idx] = self._prefetch_layer(next_idx)
                     h2d_stream.record_event(h2d_end_events[next_idx])

             # Offload current layer (waits only for this layer's compute)
             d2h_stream.wait_event(compute_end_events[i])
-            with torch.cuda.stream(d2h_stream):
+            with current_platform.stream(d2h_stream):
                 cur_states_offload = layer_states[i]
                 assert cur_states_offload is not None, f"Layer {i} already freed"
                 self._offload_layer(cur_states_offload)
@@ -628,4 +628,4 @@ def step(self) -> None:

         # Prevent cross-phase cache pollution: return freed optimizer state
         # blocks to driver so forward/backward can't repurpose them.
-        torch.cuda.empty_cache()
+        current_platform.empty_cache()

PATCH

echo "Patch applied successfully."
