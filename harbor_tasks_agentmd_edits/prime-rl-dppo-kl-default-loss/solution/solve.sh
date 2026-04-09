#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotent: skip if already applied (check for dppo_invalid_mask which is new)
if grep -q 'dppo_invalid_mask' src/prime_rl/trainer/rl/loss.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.cursor/BUGBOT.md b/.cursor/BUGBOT.md
index 2f452276eb..305b915063 100644
--- a/.cursor/BUGBOT.md
+++ b/.cursor/BUGBOT.md
@@ -2,10 +2,16 @@

 ## Changelog Enforcement

-Any PR that modifies configuration structures or usage patterns must update `CHANGELOG.md`. This includes changes to config fields (added, removed, renamed, moved, or default value changes) in:
+Any PR that introduces **breaking** configuration changes must update `CHANGELOG.md`. Breaking changes are those that require users to update existing configs:

-- `src/prime_rl/*/config.py`
-- `src/prime_rl/rl.py`
-- `src/prime_rl/utils/config.py`
+- **Renamed** config fields (old name no longer accepted)
+- **Removed** config fields (field deleted or moved to a different path)
+- **Moved** config fields (field relocated in the config hierarchy)

-If such changes are detected without a corresponding `CHANGELOG.md` update, request that the author add an entry.
+Additive changes (new fields with defaults, new optional features) and default value changes do **not** require a changelog entry.
+
+Config files live in:
+
+- `src/prime_rl/configs/`
+
+If breaking changes are detected without a corresponding `CHANGELOG.md` update, request that the author add an entry.
diff --git a/src/prime_rl/configs/trainer.py b/src/prime_rl/configs/trainer.py
index 1508a0a683..ccb351a738 100644
--- a/src/prime_rl/configs/trainer.py
+++ b/src/prime_rl/configs/trainer.py
@@ -635,8 +635,8 @@ class DefaultLossConfig(BaseModel):

     type: Literal["default"] = "default"

-    ipo_mask_low: Annotated[float, Field(ge=0, description="The low threshold for masking tokens.")] = 0.2
-    ipo_mask_high: Annotated[float, Field(ge=0, description="The high threshold for masking tokens.")] = 0.2
+    dppo_mask_low: Annotated[float, Field(ge=0, description="The low threshold for masking tokens.")] = 0.2
+    dppo_mask_high: Annotated[float, Field(ge=0, description="The high threshold for masking tokens.")] = 0.2
     adv_tau: Annotated[float, Field(ge=0, description="The tau for advantages.")] = 1.0
     teacher_tau: Annotated[float, Field(ge=0, description="The tau for teacher logprobs.")] = 0.0
     kl_tau: Annotated[float, Field(ge=0, description="The tau for KL divergence.")] = 1e-3
diff --git a/src/prime_rl/trainer/rl/loss.py b/src/prime_rl/trainer/rl/loss.py
index c4d35a8769..7dd8008750 100644
--- a/src/prime_rl/trainer/rl/loss.py
+++ b/src/prime_rl/trainer/rl/loss.py
@@ -106,15 +106,15 @@ def _safe_mean(values: Tensor, mask: Tensor) -> Tensor:

 def default_loss_fn(inputs: LossInputs, loss_config: DefaultLossConfig) -> LossOutputs:
     """
-    We implement IPO (INTELLECT Policy Optimization) loss, which combines:
+    DPPO+KL loss, combining:
     - DPPO-Binary TV Loss (https://arxiv.org/pdf/2602.04879)
     - Kimi-K2.5 KL Loss (https://arxiv.org/pdf/2602.02276)

-    Unlike the DPPO-Bin TV mask, we mask independently of the advantage sign.
-    This is, because in Async RL, we do not take multiple steps on the same
-    data, and so policy updates are not well-predicted by the advantage sign.
-    This shift is similar to the shift from GRPO -> CISPO, but with the trust
-    region being approximated by the probability difference instead of ratio.
+    The mask is conditioned on the advantage sign: for positive advantages,
+    we mask tokens whose probability increased too much (trust region violation
+    in the upweight direction); for negative advantages, we mask tokens whose
+    probability decreased too much (trust region violation in the downweight
+    direction).
     """
     trainer_logprobs = inputs.trainer_logprobs
     inference_logprobs = inputs.inference_logprobs
@@ -125,13 +125,13 @@ def default_loss_fn(inputs: LossInputs, loss_config: DefaultLossConfig) -> LossO
     trainer_probs = torch.exp(trainer_logprobs)
     inference_probs = torch.exp(inference_logprobs)
     probs_diff = trainer_probs - inference_probs
-    ipo_invalid_mask_high = probs_diff > loss_config.ipo_mask_high
-    ipo_invalid_mask_low = probs_diff < -loss_config.ipo_mask_low
-    ipo_invalid_mask = ipo_invalid_mask_high | ipo_invalid_mask_low
+    dppo_invalid_mask_high = probs_diff > loss_config.dppo_mask_high
+    dppo_invalid_mask_low = probs_diff < -loss_config.dppo_mask_low
+    dppo_invalid_mask = torch.where(advantages > 0, dppo_invalid_mask_high, dppo_invalid_mask_low)

-    is_masked = ipo_invalid_mask
-    is_masked_low = ipo_invalid_mask_low
-    is_masked_high = ipo_invalid_mask_high
+    is_masked = dppo_invalid_mask
+    is_masked_high = (advantages > 0) & dppo_invalid_mask_high
+    is_masked_low = (advantages < 0) & dppo_invalid_mask_low
     keep_mask = loss_mask & ~is_masked

     log_importance_ratio = trainer_logprobs - inference_logprobs
PATCH

echo "Patch applied successfully."
