#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotent: skip if already applied
if grep -q 'dppo_mask_low' src/prime_rl/configs/trainer.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
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
diff --git a/tests/unit/train/rl/test_loss.py b/tests/unit/train/rl/test_loss.py
index f8f4ba7116..419ac85fcb 100644
--- a/tests/unit/train/rl/test_loss.py
+++ b/tests/unit/train/rl/test_loss.py
@@ -14,7 +14,7 @@ def test_grpo_loss():
     advantages = [torch.randn(50).cuda(), torch.randn(30).cuda()]
     loss_mask = [torch.ones(50, dtype=torch.bool).cuda(), torch.ones(30, dtype=torch.bool).cuda()]

-    loss_fn = setup_loss_fn(DefaultLossConfig(ipo_mask_high=10.0))
+    loss_fn = setup_loss_fn(DefaultLossConfig(dppo_mask_high=10.0))
     loss, _ = compute_loss(
         trainer_logprobs,
         inference_logprobs,
@@ -34,7 +34,7 @@ def test_gspo_loss():
     advantages = [torch.randn(40).cuda(), torch.randn(60).cuda()]
     loss_mask = [torch.ones(40, dtype=torch.bool).cuda(), torch.ones(60, dtype=torch.bool).cuda()]

-    loss_fn = setup_loss_fn(DefaultLossConfig(ipo_mask_high=10.0))
+    loss_fn = setup_loss_fn(DefaultLossConfig(dppo_mask_high=10.0))
     loss, _ = compute_loss(
         trainer_logprobs,
         inference_logprobs,

PATCH

echo "Patch applied successfully."
