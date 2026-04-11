#!/usr/bin/env bash
set -euo pipefail

cd /workspace/beam

# Idempotent: skip if already applied
if grep -q 'build_vllm_server_kwargs' sdks/python/apache_beam/examples/inference/vllm_text_completion.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/sdks/python/apache_beam/examples/inference/README.md b/sdks/python/apache_beam/examples/inference/README.md
index 4d6c91e3ab6d..5eed659d068c 100644
--- a/sdks/python/apache_beam/examples/inference/README.md
+++ b/sdks/python/apache_beam/examples/inference/README.md
@@ -930,6 +930,12 @@ python -m apache_beam.examples.inference.vllm_text_completion \

 Make sure to enable the 5xx driver since vLLM only works with 5xx drivers, not 4xx.

+On GPUs with about 16GiB of memory (for example NVIDIA T4), vLLM's defaults can fail
+during engine startup with CUDA out of memory. The example therefore passes conservative
+``--max-num-seqs`` and ``--gpu-memory-utilization`` values by default (overridable with
+``--vllm_max_num_seqs`` and ``--vllm_gpu_memory_utilization``) via
+`vllm_server_kwargs`, matching the pattern used in other vLLM examples.
+
 This writes the output to the output file location with contents like:

 ```
diff --git a/sdks/python/apache_beam/examples/inference/vllm_text_completion.py b/sdks/python/apache_beam/examples/inference/vllm_text_completion.py
index 2708c0f3d1a1..00fe3c319dd2 100644
--- a/sdks/python/apache_beam/examples/inference/vllm_text_completion.py
+++ b/sdks/python/apache_beam/examples/inference/vllm_text_completion.py
@@ -26,6 +26,7 @@
 import argparse
 import logging
 from collections.abc import Iterable
+from typing import Optional

 import apache_beam as beam
 from apache_beam.ml.inference.base import PredictionResult
@@ -37,6 +38,12 @@
 from apache_beam.options.pipeline_options import SetupOptions
 from apache_beam.runners.runner import PipelineResult

+# Defaults avoid CUDA OOM on ~16GB GPUs (e.g. NVIDIA T4) with vLLM V1: the engine
+# warms the sampler with many dummy sequences unless max_num_seqs is reduced, and
+# the default gpu_memory_utilization can leave no free VRAM for that step.
+_DEFAULT_VLLM_MAX_NUM_SEQS = 32
+_DEFAULT_VLLM_GPU_MEMORY_UTILIZATION = 0.72
+
 COMPLETION_EXAMPLES = [
     "Hello, my name is",
     "The president of the United States is",
@@ -112,33 +119,72 @@ def parse_known_args(argv):
       required=False,
       default=None,
       help='Chat template to use for chat example.')
+  parser.add_argument(
+      '--vllm_max_num_seqs',
+      dest='vllm_max_num_seqs',
+      type=int,
+      default=_DEFAULT_VLLM_MAX_NUM_SEQS,
+      help=(
+          'Passed to the vLLM OpenAI server as --max-num-seqs. '
+          'Lower values use less GPU memory during startup and inference; '
+          'required for many ~16GB GPUs (see --vllm_gpu_memory_utilization).'))
+  parser.add_argument(
+      '--vllm_gpu_memory_utilization',
+      dest='vllm_gpu_memory_utilization',
+      type=float,
+      default=_DEFAULT_VLLM_GPU_MEMORY_UTILIZATION,
+      help=(
+          'Passed to the vLLM OpenAI server as --gpu-memory-utilization '
+          '(fraction of total GPU memory for KV cache). Lower this if the '
+          'engine fails to start with CUDA out of memory.'))
   return parser.parse_known_args(argv)


+def build_vllm_server_kwargs(known_args) -> dict[str, str]:
+  """Returns CLI flags for ``VLLMCompletionsModelHandler(..., vllm_server_kwargs=...)``."""
+  return {
+      'max-num-seqs': str(known_args.vllm_max_num_seqs),
+      'gpu-memory-utilization': str(known_args.vllm_gpu_memory_utilization),
+  }
+
+
 class PostProcessor(beam.DoFn):
   def process(self, element: PredictionResult) -> Iterable[str]:
     yield str(element.example) + ": " + str(element.inference)


 def run(
-    argv=None, save_main_session=True, test_pipeline=None) -> PipelineResult:
+    argv=None,
+    save_main_session=True,
+    test_pipeline=None,
+    vllm_server_kwargs: Optional[dict[str, str]] = None) -> PipelineResult:
   """
   Args:
     argv: Command line arguments defined for this example.
     save_main_session: Used for internal testing.
     test_pipeline: Used for internal testing.
+    vllm_server_kwargs: Optional override for vLLM server options. When None,
+      options are taken from argv (``--vllm_max_num_seqs``,
+      ``--vllm_gpu_memory_utilization``). When set, argv tuning flags for the
+      server are ignored in favor of this dict (e.g. for programmatic use).
   """
   known_args, pipeline_args = parse_known_args(argv)
   pipeline_options = PipelineOptions(pipeline_args)
   pipeline_options.view_as(SetupOptions).save_main_session = save_main_session

-  model_handler = VLLMCompletionsModelHandler(model_name=known_args.model)
+  effective_vllm_kwargs = (
+      vllm_server_kwargs if vllm_server_kwargs is not None else
+      build_vllm_server_kwargs(known_args))
+
+  model_handler = VLLMCompletionsModelHandler(
+      model_name=known_args.model, vllm_server_kwargs=effective_vllm_kwargs)
   input_examples = COMPLETION_EXAMPLES

   if known_args.chat:
     model_handler = VLLMChatModelHandler(
         model_name=known_args.model,
-        chat_template_path=known_args.chat_template)
+        chat_template_path=known_args.chat_template,
+        vllm_server_kwargs=dict(effective_vllm_kwargs))
     input_examples = CHAT_EXAMPLES

   pipeline = test_pipeline
diff --git a/sdks/python/apache_beam/ml/inference/vllm_inference.py b/sdks/python/apache_beam/ml/inference/vllm_inference.py
index 918b49155606..b5db6298f472 100644
--- a/sdks/python/apache_beam/ml/inference/vllm_inference.py
+++ b/sdks/python/apache_beam/ml/inference/vllm_inference.py
@@ -199,6 +199,8 @@ def __init__(
         `python -m vllm.entrypoints.openai.api_serverv <beam provided args>
         <vllm_server_kwargs>`. For example, you could pass
         `{'echo': 'true'}` to prepend new messages with the previous message.
+        On ~16GB GPUs, pass lower ``max-num-seqs`` and ``gpu-memory-utilization``
+        values (see ``apache_beam.examples.inference.vllm_text_completion``).
         For a list of possible kwargs, see
         https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html#extra-parameters-for-completions-api
       min_batch_size: optional. the minimum batch size to use when batching

PATCH

echo "Patch applied successfully."
