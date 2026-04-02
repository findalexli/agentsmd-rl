#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency: check if already applied
if grep -q 'capture_error_mode' src/transformers/generation/continuous_batching/continuous_api.py; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/transformers/generation/continuous_batching/continuous_api.py b/src/transformers/generation/continuous_batching/continuous_api.py
index 0019b2df1a7d..08be21022d73 100644
--- a/src/transformers/generation/continuous_batching/continuous_api.py
+++ b/src/transformers/generation/continuous_batching/continuous_api.py
@@ -464,7 +464,15 @@ def _generation_step(self, model: nn.Module, logit_processor: LogitsProcessorLis
                 # torch.cuda.current_stream().wait_stream(compute_stream)
                 # Capture
                 graph = torch.cuda.CUDAGraph()
-                with torch.cuda.graph(graph, stream=compute_stream, pool=self.graph_pool):
+                # Continuous batching can run multiple manager threads concurrently in one process.
+                # PyTorch's default capture mode ("global") errors on CUDA actions from other threads,
+                # which invalidates unrelated captures even when each manager uses a different device.
+                with torch.cuda.graph(
+                    graph,
+                    stream=compute_stream,
+                    pool=self.graph_pool,
+                    capture_error_mode="thread_local",
+                ):
                     forward_fn(
                         model, batch_data, logit_processor, do_sample, carry_over_ids, prev_output_ids, output_ids
                     )

PATCH

echo "Patch applied successfully."
