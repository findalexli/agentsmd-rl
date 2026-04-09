#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vllm

# Idempotent: skip if already applied
if ! grep -q 'copy_event: torch.cuda.Event' vllm/v1/worker/gpu/async_utils.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/vllm/v1/worker/gpu/async_utils.py b/vllm/v1/worker/gpu/async_utils.py
index 7f270c2b8c95..b3d6f5e4d901 100644
--- a/vllm/v1/worker/gpu/async_utils.py
+++ b/vllm/v1/worker/gpu/async_utils.py
@@ -17,7 +17,6 @@ def __init__(
         num_sampled_tokens: torch.Tensor,
         main_stream: torch.cuda.Stream,
         copy_stream: torch.cuda.Stream,
-        copy_event: torch.cuda.Event,
     ):
         # NOTE(woosuk): We must retain references to the GPU tensors,
         # as the copy operations are performed on a different CUDA stream than
@@ -25,7 +24,7 @@ def __init__(
         self.model_runner_output = model_runner_output
         self.sampler_output = sampler_output
         self.num_sampled_tokens = num_sampled_tokens
-        self.copy_event = copy_event
+        self.copy_event = torch.cuda.Event()

         with stream(copy_stream, main_stream):
             copy_stream.wait_stream(main_stream)
@@ -78,12 +77,11 @@ def __init__(
         is_valid: torch.Tensor | None,
         main_stream: torch.cuda.Stream,
         copy_stream: torch.cuda.Stream,
-        copy_event: torch.cuda.Event,
     ):
         self.model_runner_output = model_runner_output
         self.pooler_output = pooler_output
         self.is_valid = is_valid
-        self.copy_event = copy_event
+        self.copy_event = torch.cuda.Event()

         with stream(copy_stream, main_stream):
             copy_stream.wait_stream(main_stream)
diff --git a/vllm/v1/worker/gpu/model_runner.py b/vllm/v1/worker/gpu/model_runner.py
index 56df70fc0c9c..f188b061a6ce 100644
--- a/vllm/v1/worker/gpu/model_runner.py
+++ b/vllm/v1/worker/gpu/model_runner.py
@@ -130,7 +130,6 @@ def __init__(self, vllm_config: VllmConfig, device: torch.device):

         self.use_async_scheduling = self.scheduler_config.async_scheduling
         self.output_copy_stream = torch.cuda.Stream(self.device)
-        self.output_copy_event = torch.cuda.Event()

         # Pipeline parallelism.
         self.use_pp = self.parallel_config.pipeline_parallel_size > 1
@@ -1180,7 +1179,6 @@ def sample_tokens(
             num_sampled_tokens=num_sampled,
             main_stream=self.main_stream,
             copy_stream=self.output_copy_stream,
-            copy_event=self.output_copy_event,
         )

         mm_inputs: tuple[list[torch.Tensor], torch.Tensor] | None = None
@@ -1270,7 +1268,6 @@ def pool(self) -> AsyncPoolingOutput | ModelRunnerOutput | None:
             is_valid=is_valid,
             main_stream=self.main_stream,
             copy_stream=self.output_copy_stream,
-            copy_event=self.output_copy_event,
         )

         self.postprocess_pool(input_batch)

PATCH

echo "Patch applied successfully."
