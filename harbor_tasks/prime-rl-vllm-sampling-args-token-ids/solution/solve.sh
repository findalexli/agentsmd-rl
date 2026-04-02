#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotency: check if already fixed (is_vllm parameter present)
if grep -q 'is_vllm' src/prime_rl/orchestrator/utils.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/prime_rl/orchestrator/orchestrator.py b/src/prime_rl/orchestrator/orchestrator.py
index 0c01bfc246..1da1b547e2 100644
--- a/src/prime_rl/orchestrator/orchestrator.py
+++ b/src/prime_rl/orchestrator/orchestrator.py
@@ -490,9 +490,8 @@ def _cleanup_env_processes():

         # Schedule generating the training batch
         temperature = compute_temperature(progress.step, config.sampling, config.max_steps)
-        sampling_args = get_sampling_args(
-            config.sampling, temperature=temperature, use_token_client=config.use_token_client
-        )
+        is_vllm = config.teacher_rollout_model is None
+        sampling_args = get_sampling_args(config.sampling, temperature=temperature, is_vllm=is_vllm)
         scheduler.set_sampling_args(sampling_args)
         train_task = asyncio.create_task(scheduler.generate_batch(step=progress.step))

diff --git a/src/prime_rl/orchestrator/scheduler.py b/src/prime_rl/orchestrator/scheduler.py
index 98f19fca27..644e1b894a 100644
--- a/src/prime_rl/orchestrator/scheduler.py
+++ b/src/prime_rl/orchestrator/scheduler.py
@@ -88,9 +88,8 @@ def __init__(
         self.enable_policy_updates = enable_policy_updates
         self.lora_name = lora_name
         initial_temp = compute_temperature(step=0, sampling_config=config.sampling, max_steps=config.max_steps)
-        self.sampling_args = get_sampling_args(
-            config.sampling, temperature=initial_temp, use_token_client=config.use_token_client
-        )
+        is_vllm = config.teacher_rollout_model is None
+        self.sampling_args = get_sampling_args(config.sampling, temperature=initial_temp, is_vllm=is_vllm)
         self.model_name = self.config.model.name
         self.json_logging = config.log.json_logging

diff --git a/src/prime_rl/orchestrator/utils.py b/src/prime_rl/orchestrator/utils.py
index 303a86617c..5c6f56a82f 100644
--- a/src/prime_rl/orchestrator/utils.py
+++ b/src/prime_rl/orchestrator/utils.py
@@ -36,13 +36,14 @@ async def get_semaphore() -> AsyncContextManager:
     return SEMAPHORE


-def get_sampling_args(sampling_config: SamplingConfig, temperature: float, use_token_client: bool = True) -> dict:
+def get_sampling_args(sampling_config: SamplingConfig, temperature: float, is_vllm: bool = True) -> dict:
     # Convert SamplingConfig to vLLM OAI sampling args
     # https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html#extra-parameters_2
     sampling_args = dict(sampling_config)
     sampling_args.pop("temp_scheduler", None)
     sampling_args["temperature"] = temperature
     sampling_args["top_p"] = 1.0
+    sampling_args["logprobs"] = True
     extra_body = dict(sampling_config.extra_body)

     min_tokens = sampling_args.pop("min_tokens")
@@ -53,12 +54,9 @@ def get_sampling_args(sampling_config: SamplingConfig, temperature: float, use_t
     if repetition_penalty != 1.0:
         extra_body["repetition_penalty"] = repetition_penalty

-    extra_body["top_k"] = -1
-    extra_body["min_p"] = 0.0
-
-    sampling_args["logprobs"] = True
-
-    if use_token_client:
+    if is_vllm:
+        extra_body["top_k"] = -1
+        extra_body["min_p"] = 0.0
         extra_body["return_token_ids"] = True

     if extra_body:

PATCH

echo "Patch applied successfully."
