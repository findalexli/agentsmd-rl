#!/bin/bash
# Apply gold patch for PrimeIntellect-ai/prime-rl#2206
set -euo pipefail

cd /workspace/prime-rl

# Idempotency: skip if already applied
if grep -q "max_total_completion_tokens" src/prime_rl/configs/orchestrator.py; then
    echo "Patch already applied"
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/prime_rl/configs/orchestrator.py b/src/prime_rl/configs/orchestrator.py
index f9c126ebac..89127bda11 100644
--- a/src/prime_rl/configs/orchestrator.py
+++ b/src/prime_rl/configs/orchestrator.py
@@ -14,6 +14,7 @@
     WandbWithExtrasConfig,
 )
 from prime_rl.utils.config import BaseConfig
+from prime_rl.utils.logger import get_logger


 class OptimizerConfig(BaseConfig):
@@ -127,9 +128,10 @@ class SamplingConfig(BaseConfig):
         ),
     ] = 1.0

-    max_tokens: Annotated[
+    max_completion_tokens: Annotated[
         int | None,
         Field(
+            validation_alias=AliasChoices("max_completion_tokens", "max_tokens"),
             description="Maximum number of output tokens to generate per turn. If None, will generate until maximum context length or EOS token is hit.",
         ),
     ] = None
@@ -158,6 +160,13 @@ class SamplingConfig(BaseConfig):
         ),
     ] = {}

+    @model_validator(mode="before")
+    @classmethod
+    def _deprecate_max_tokens(cls, data: Any) -> Any:
+        if isinstance(data, dict) and "max_tokens" in data and "max_completion_tokens" not in data:
+            get_logger().warning("'max_tokens' is deprecated, use 'max_completion_tokens' instead.")
+        return data
+

 class EvalSamplingConfig(BaseConfig):
     """Configures how tokens are sampled from the model for evaluation. Largely follows the vLLM sampling parameters."""
@@ -199,9 +208,10 @@ class EvalSamplingConfig(BaseConfig):
         ),
     ] = None

-    max_tokens: Annotated[
+    max_completion_tokens: Annotated[
         int | None,
         Field(
+            validation_alias=AliasChoices("max_completion_tokens", "max_tokens"),
             description="Maximum number of output tokens to generate per turn. If None, will generate until maximum context length or EOS token is hit.",
         ),
     ] = None
@@ -236,6 +246,13 @@ class EvalSamplingConfig(BaseConfig):
         ),
     ] = {}

+    @model_validator(mode="before")
+    @classmethod
+    def _deprecate_max_tokens(cls, data: Any) -> Any:
+        if isinstance(data, dict) and "max_tokens" in data and "max_completion_tokens" not in data:
+            get_logger().warning("'max_tokens' is deprecated, use 'max_completion_tokens' instead.")
+        return data
+

 class EvalSaveHFConfig(BaseConfig):
     """Configures how to save the eval results to HF."""
@@ -283,7 +300,7 @@ class EnvConfig(BaseConfig):
         dict[str, Any],
         Field(
             description=(
-                "Extra kwargs passed to an env (e.g. seq_len, score_rollouts). This field is auto-populated with the seq_len, and score_rollouts for training envs on the orchestrator. It is generally NOT recommended for this field to be overriden by the user. It's main use case is to match the extra_env_kwargs when running an env in an isolated environment server."
+                "Extra kwargs passed to an env (e.g. seq_len, score_rollouts, max_total_completion_tokens). This field is auto-populated with the seq_len, and score_rollouts for training envs on the orchestrator and max_total_completion_tokens for all envs. It is generally NOT recommended for this field to be overriden by the user. It's main use case is to match the extra_env_kwargs when running an env in an isolated environment server."
             ),
         ),
     ] = {}
@@ -305,6 +322,15 @@ class EnvConfig(BaseConfig):
             description="Maximum number of times the environment will retry a failed rollout.",
         ),
     ] = 0
+    max_total_completion_tokens: Annotated[
+        int,
+        Field(
+            description=(
+                "Maximum total completion tokens across all turns in a multi-turn rollout. "
+                "Set to -1 (default) to disable. Auto-populated into extra_env_kwargs."
+            ),
+        ),
+    ] = -1

     @property
     def resolved_name(self) -> str:
@@ -318,6 +344,11 @@ def validate_env_name(self):
             )
         return self

+    @model_validator(mode="after")
+    def resolve_max_total_completion_tokens(self):
+        self.extra_env_kwargs["max_total_completion_tokens"] = self.max_total_completion_tokens
+        return self
+

 class EvalEnvConfig(EnvConfig):
     """Configures an environment for evaluation."""
diff --git a/src/prime_rl/orchestrator/eval_utils.py b/src/prime_rl/orchestrator/eval_utils.py
index 5c66e9ef36..38522d2cd8 100644
--- a/src/prime_rl/orchestrator/eval_utils.py
+++ b/src/prime_rl/orchestrator/eval_utils.py
@@ -47,8 +47,8 @@ def get_eval_sampling_args(sampling_config: EvalSamplingConfig) -> dict[str, Any
     # Apply sampling arguments, if specified
     if sampling_config.temperature is not None:
         sampling_args["temperature"] = sampling_config.temperature
-    if sampling_config.max_tokens is not None:
-        sampling_args["max_tokens"] = sampling_config.max_tokens
+    if sampling_config.max_completion_tokens is not None:
+        sampling_args["max_completion_tokens"] = sampling_config.max_completion_tokens
     if sampling_config.top_p is not None:
         sampling_args["top_p"] = sampling_config.top_p
     if sampling_config.reasoning_effort is not None:
PATCH

echo "Patch applied successfully"
