#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vllm

# Idempotent: skip if already applied
if grep -q 'from vllm.v1.worker.encoder_cudagraph_defs import' vllm/v1/worker/encoder_cudagraph.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/tests/v1/cudagraph/test_encoder_cudagraph.py b/tests/v1/cudagraph/test_encoder_cudagraph.py
index 322fcb3caa14..543dfc8bb316 100644
--- a/tests/v1/cudagraph/test_encoder_cudagraph.py
+++ b/tests/v1/cudagraph/test_encoder_cudagraph.py
@@ -14,17 +14,17 @@

 import pytest
 import torch
-from vllm.v1.worker.gpu.mm.encoder_cudagraph import (
+
+from vllm.platforms import current_platform
+from vllm.v1.worker.encoder_cudagraph import (
     EncoderCudaGraphManager,
 )
-from vllm.v1.worker.gpu.mm.encoder_cudagraph_defs import (
+from vllm.v1.worker.encoder_cudagraph_defs import (
     EncoderCudaGraphCaptureInputs,
     EncoderCudaGraphConfig,
     EncoderCudaGraphReplayBuffers,
 )

-from vllm.platforms import current_platform
-
 # ---------------------------------------------------------------------------
 # Helpers
 # ---------------------------------------------------------------------------
diff --git a/vllm/model_executor/models/interfaces.py b/vllm/model_executor/models/interfaces.py
index df7170aab34f..1f1d57493c02 100644
--- a/vllm/model_executor/models/interfaces.py
+++ b/vllm/model_executor/models/interfaces.py
@@ -46,7 +46,7 @@
     from vllm.multimodal.inputs import MultiModalFeatureSpec
     from vllm.multimodal.registry import _ProcessorFactories
     from vllm.sequence import IntermediateTensors
-    from vllm.v1.worker.gpu.mm.encoder_cudagraph_defs import (
+    from vllm.v1.worker.encoder_cudagraph_defs import (
         EncoderCudaGraphCaptureInputs,
         EncoderCudaGraphConfig,
         EncoderCudaGraphReplayBuffers,
diff --git a/vllm/model_executor/models/qwen3_vl.py b/vllm/model_executor/models/qwen3_vl.py
index cb48ceb0c77b..1aa5dec5390b 100644
--- a/vllm/model_executor/models/qwen3_vl.py
+++ b/vllm/model_executor/models/qwen3_vl.py
@@ -1733,7 +1733,7 @@ def _clear_deepstack_input_embeds(self, num_tokens: int) -> None:
     # -- SupportsEncoderCudaGraph protocol methods --

     def get_encoder_cudagraph_config(self):
-        from vllm.v1.worker.gpu.mm.encoder_cudagraph_defs import (
+        from vllm.v1.worker.encoder_cudagraph_defs import (
             EncoderCudaGraphConfig,
         )

@@ -1818,7 +1818,7 @@ def prepare_encoder_cudagraph_capture_inputs(
         device: torch.device,
         dtype: torch.dtype,
     ):
-        from vllm.v1.worker.gpu.mm.encoder_cudagraph_defs import (
+        from vllm.v1.worker.encoder_cudagraph_defs import (
             EncoderCudaGraphCaptureInputs,
         )

@@ -1872,7 +1872,7 @@ def prepare_encoder_cudagraph_replay_buffers(
         mm_kwargs: dict[str, Any],
         max_batch_size: int,
     ):
-        from vllm.v1.worker.gpu.mm.encoder_cudagraph_defs import (
+        from vllm.v1.worker.encoder_cudagraph_defs import (
             EncoderCudaGraphReplayBuffers,
         )

diff --git a/vllm/v1/worker/encoder_cudagraph.py b/vllm/v1/worker/encoder_cudagraph.py
index b2930a23474e..0fabbc77c07a 100644
--- a/vllm/v1/worker/encoder_cudagraph.py
+++ b/vllm/v1/worker/encoder_cudagraph.py
@@ -16,7 +16,7 @@
 from vllm.logger import init_logger
 from vllm.model_executor.models.interfaces import SupportsEncoderCudaGraph
 from vllm.model_executor.models.vision import get_load_balance_assignment
-from vllm.v1.worker.gpu.mm.encoder_cudagraph_defs import (
+from vllm.v1.worker.encoder_cudagraph_defs import (
     EncoderCudaGraphConfig,
 )

diff --git a/vllm/v1/worker/gpu_model_runner.py b/vllm/v1/worker/gpu_model_runner.py
index 7a21117fb64c..8dfa65da1368 100644
--- a/vllm/v1/worker/gpu_model_runner.py
+++ b/vllm/v1/worker/gpu_model_runner.py
@@ -211,7 +211,7 @@
 if TYPE_CHECKING:
     from vllm.v1.core.sched.output import GrammarOutput, SchedulerOutput
     from vllm.v1.spec_decode.ngram_proposer import NgramProposer
-    from vllm.v1.worker.gpu.mm.encoder_cudagraph import EncoderCudaGraphManager
+    from vllm.v1.worker.encoder_cudagraph import EncoderCudaGraphManager

 logger = init_logger(__name__)

@@ -5988,7 +5988,7 @@ def capture_model(self) -> int:
                 SupportsEncoderCudaGraph,
                 supports_encoder_cudagraph,
             )
-            from vllm.v1.worker.gpu.mm.encoder_cudagraph import (
+            from vllm.v1.worker.encoder_cudagraph import (
                 EncoderCudaGraphManager,
             )

PATCH

echo "Patch applied successfully."
