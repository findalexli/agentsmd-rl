#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency check: if QuackFusedCrossEntropyOutputLinear already exists, patch is applied
if grep -q 'QuackFusedCrossEntropyOutputLinear' src/prime_rl/trainer/models/layers/lm_head.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 28c486e015..0f85c8592b 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -2,6 +2,7 @@

 Documenting changes which affect configuration usage patterns (added/moved/removed/renamed fields, notable logic changes).

+- **`loss_impl = "quack_fused"` (SFT)**: Added `quack_fused` option for the SFT `loss_impl` field. Uses quack-kernels for chunked linear + cross-entropy with CuTe DSL CUDA kernels, avoiding full logits materialization. Requires `quack-kernels` package. Does not support Gemma logit softcapping. Custom model impl (`model.impl = "custom"`) also gains quack RMSNorm acceleration on CUDA automatically. (2026-03-26)
 - **`model.tp` (trainer `ModelConfig`)**: Removed from the trainer model config. Existing trainer configs must delete this field; it is no longer accepted. (2026-03-26)
 - **`orchestrator.env[].num_workers`**: Added configurable env server worker count (`int | "auto"`, default: `"auto"`). When `"auto"`, scales based on concurrency (1 worker per 256 concurrent rollouts). Only used when the orchestrator spawns the env server (i.e. `address` is not set). (2026-03-25)
 - **`[model.vlm]` (NEW — replaces auto-detection)**: VLM mode is now opt-in via a `[model.vlm]` sub-config with required `vision_encoder_attr` and `language_model_attr` fields. There is no auto-detection — if you train a VLM, you must add `[model.vlm]`. Existing multimodal configs need the new section. See `docs/multimodal.md` for the table of known model attrs. (2026-03-24)
diff --git a/pyproject.toml b/pyproject.toml
index 93df3c11dc..adc4049bb6 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -55,7 +55,7 @@ flash-attn-3 = [
     "flash_attn_3 @ https://github.com/samsja/flash-attn-builds/releases/download/v0.1/flash_attn_3-3.0.0b1-cp39-abi3-linux_x86_64.whl ; platform_machine == 'x86_64'",
 ]
 flash-attn-cute = [
-    "flash-attn-cute",
+    "flash-attn-4",
 ]
 envs = [
     "reverse-text",
@@ -78,6 +78,9 @@ disagg = [
     "nixl-cu12 ; platform_machine == 'x86_64'",
     "vllm-router ; platform_machine == 'x86_64'",
 ]
+quack = [
+    "quack-kernels>=0.3.3",
+]

 [dependency-groups]
 mamba-ssm = [
@@ -105,7 +108,6 @@ override-dependencies = [
     "nvidia-cudnn-cu12>=9.15",
     "nvidia-cutlass-dsl>=4.4.1",
     "transformers>=5.1.0.dev0",
-    "quack-kernels>=0.2.7",
 ]

 [tool.uv.sources]
@@ -114,7 +116,7 @@ verifiers = { git = "https://github.com/PrimeIntellect-ai/verifiers.git", rev =
 torchtitan = { git = "https://github.com/pytorch/torchtitan", rev = "a1fdd7e" }
 dion = { git = "https://github.com/samsja/dion.git", rev = "d891eeb" }
 transformers = { git = "https://github.com/huggingface/transformers.git", rev = "5c1c72b" }
-flash-attn-cute = { git = "https://github.com/Dao-AILab/flash-attention.git", subdirectory = "flash_attn/cute", rev = "e2743ab5" }
+flash-attn-4 = { git = "https://github.com/Dao-AILab/flash-attention.git", subdirectory = "flash_attn/cute", rev = "abd9943b" }
 pydantic-config = { git = "https://github.com/samsja/pydantic_config.git", branch = "main" }
 vllm-router = { url = "https://github.com/samsja/flash-attn-builds/releases/download/v0.3/vllm_router-0.1.11-cp38-abi3-linux_x86_64.whl" }
 reverse-text = { index = "primeintellect" }
diff --git a/src/prime_rl/configs/sft.py b/src/prime_rl/configs/sft.py
index b66b38686f..348de5b537 100644
--- a/src/prime_rl/configs/sft.py
+++ b/src/prime_rl/configs/sft.py
@@ -225,10 +225,11 @@ class SFTConfig(BaseConfig):
     ] = 600

     loss_impl: Annotated[
-        Literal["liger", "torch", "liger_fused"],
+        Literal["liger", "torch", "liger_fused", "quack_fused"],
         Field(
             description="Implementation of the cross entropy loss function to use. "
-            "'liger_fused' fuses the lm_head projection with the CE loss to avoid materializing full logits."
+            "'liger_fused' fuses the lm_head projection with the CE loss to avoid materializing full logits. "
+            "'quack_fused' uses quack-kernels for chunked linear + CE with CuTe DSL CUDA kernels."
         ),
     ] = "torch"

diff --git a/src/prime_rl/trainer/model.py b/src/prime_rl/trainer/model.py
index 3fefc7aa2a..e8136f3f23 100644
--- a/src/prime_rl/trainer/model.py
+++ b/src/prime_rl/trainer/model.py
@@ -726,7 +726,7 @@ def setup_model(
     config: ModelConfig,
     parallel_dims: ParallelDims,
     loading_from_checkpoint_later: bool = False,
-    fused_cross_entropy: bool = False,
+    fused_cross_entropy: bool | str = False,
 ) -> nn.Module:
     if config.attn == "flash_attention_3" and not is_flash_attn_3_available():
         raise ValueError(
diff --git a/src/prime_rl/trainer/models/layers/lm_head.py b/src/prime_rl/trainer/models/layers/lm_head.py
index 43f1845be6..84556425a3 100644
--- a/src/prime_rl/trainer/models/layers/lm_head.py
+++ b/src/prime_rl/trainer/models/layers/lm_head.py
@@ -9,6 +9,8 @@

 from prime_rl.utils.logger import get_logger

+FUSED_CE_IGNORE_INDEX = -100
+

 class PrimeLmOutput(TypedDict, total=False):
     """Output from LM head - a TypedDict so pytree can find tensors for FSDP2 hooks."""
@@ -79,7 +81,7 @@ class FusedCrossEntropyOutputLinear(torch.nn.Linear):
     projection with the cross-entropy loss computation.
     """

-    IGNORE_INDEX = -100
+    IGNORE_INDEX = FUSED_CE_IGNORE_INDEX

     def __init__(self, in_features: int, out_features: int, softcap: float | None = None):
         super().__init__(in_features, out_features, bias=False)
@@ -105,6 +107,45 @@ def forward(
         return PrimeLmOutput(loss=loss)


+class QuackFusedCrossEntropyOutputLinear(torch.nn.Linear):
+    """Fused lm_head + cross-entropy loss using quack-kernels.
+
+    Chunks the linear projection and cross-entropy computation to avoid
+    materializing the full [N, V] logits tensor, using quack's optimized
+    CuTe DSL kernels for CE and GEMM.
+    """
+
+    IGNORE_INDEX = FUSED_CE_IGNORE_INDEX
+
+    def __init__(self, in_features: int, out_features: int, chunk_size: int = 4096):
+        super().__init__(in_features, out_features, bias=False)
+        self.chunk_size = chunk_size
+
+    def forward(
+        self,
+        hidden_states: torch.Tensor,
+        labels: torch.Tensor | None = None,
+        temperature: Tensor | None = None,
+    ) -> PrimeLmOutput:
+        if labels is None:
+            return PrimeLmOutput(logits=super().forward(hidden_states))
+
+        from quack.linear_cross_entropy import chunked_linear_cross_entropy
+
+        b, s, h = hidden_states.shape
+        hidden_flat = hidden_states.reshape(b * s, h).contiguous()
+        labels_flat = labels.reshape(b * s).contiguous()
+        loss = chunked_linear_cross_entropy(
+            hidden_flat,
+            self.weight,
+            labels_flat,
+            chunk_size=self.chunk_size,
+            ignore_index=self.IGNORE_INDEX,
+            reduction="mean",
+        )
+        return PrimeLmOutput(loss=loss)
+
+
 def _online_logsumexp_and_weighted_update(
     m: torch.Tensor, s: torch.Tensor, t: torch.Tensor, chunk_logits: torch.Tensor
 ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
@@ -227,7 +268,11 @@ def backward(ctx, grad_logprobs: torch.Tensor, grad_entropy: torch.Tensor | None
         return grad_hidden, grad_weight, None, None, None


-def inject_prime_lm_head(model: nn.Module, chunk_size: int | None = None, fused_cross_entropy: bool = False) -> None:
+def inject_prime_lm_head(
+    model: nn.Module,
+    chunk_size: int | None = None,
+    fused_cross_entropy: bool | str = False,
+) -> None:
     """
     Inject a PrimeRL LM head into a model.

@@ -238,8 +283,10 @@ def inject_prime_lm_head(model: nn.Module, chunk_size: int | None = None, fused_
         model: The model to wrap.
         chunk_size: When set to an int, uses FusedOutputLinear with sequence-token chunked
             logprob/entropy computation (for RL).
-        fused_cross_entropy: When True, uses FusedCrossEntropyOutputLinear which fuses the lm_head
-            projection with cross-entropy loss to avoid materializing full logits (for SFT).
+        fused_cross_entropy: Controls fused lm_head + CE loss. Accepts:
+            - False: no fusion
+            - True or "liger": Liger kernel fusion
+            - "quack": quack-kernels fusion (chunked linear + CE with CuTe DSL kernels)
     """
     # Guards so we have nicer error messages when a non-standard model is used
     assert hasattr(model, "model"), f"model doesnt have backbone in model.model:\n{model}"
@@ -254,15 +301,27 @@ def inject_prime_lm_head(model: nn.Module, chunk_size: int | None = None, fused_

     # Check for Gemma-style softcapping - dispatch to specialized implementation
     final_logit_softcapping = getattr(model.config, "final_logit_softcapping", None)
-    if final_logit_softcapping and not fused_cross_entropy:
-        from prime_rl.trainer.models.layers.lm_head_gemma import inject_gemma_lm_head
-
-        inject_gemma_lm_head(model, chunk_size, final_logit_softcapping)
-        return
+    if final_logit_softcapping:
+        if fused_cross_entropy == "quack":
+            raise ValueError(
+                "quack_fused does not support Gemma logit softcapping. "
+                "Use loss_impl='liger_fused' or loss_impl='torch' instead."
+            )
+        if not fused_cross_entropy:
+            from prime_rl.trainer.models.layers.lm_head_gemma import inject_gemma_lm_head
+
+            inject_gemma_lm_head(model, chunk_size, final_logit_softcapping)
+            return

     # Replace the lm_head with the appropriate wrapper
     old_lm_head = model.lm_head
-    if fused_cross_entropy:
+    if fused_cross_entropy == "quack":
+        logger.info("Injecting fused cross-entropy LM head (quack-kernels)")
+        model.lm_head = QuackFusedCrossEntropyOutputLinear(
+            in_features=old_lm_head.in_features,
+            out_features=old_lm_head.out_features,
+        )
+    elif fused_cross_entropy:
         logger.info("Injecting fused cross-entropy LM head (Liger kernel)")
         model.lm_head = FusedCrossEntropyOutputLinear(
             in_features=old_lm_head.in_features,
diff --git a/src/prime_rl/trainer/models/layers/norms.py b/src/prime_rl/trainer/models/layers/norms.py
index 349b6175b4..6bd63c6bdf 100644
--- a/src/prime_rl/trainer/models/layers/norms.py
+++ b/src/prime_rl/trainer/models/layers/norms.py
@@ -1,4 +1,5 @@
 from dataclasses import dataclass
+from functools import lru_cache

 import torch
 import torch.nn.functional as F
@@ -6,6 +7,38 @@
 from transformers.integrations import use_kernel_forward_from_hub


+@lru_cache(maxsize=1)
+def _get_quack_rmsnorm():
+    """Lazy-load quack rmsnorm. Returns None if unavailable or GPU is pre-Hopper."""
+    if not torch.cuda.is_available() or torch.cuda.get_device_capability()[0] < 9:
+        return None
+    try:
+        from quack import rmsnorm
+
+        return rmsnorm
+    except ImportError:
+        return None
+
+
+class _ContiguousGrad(torch.autograd.Function):
+    @staticmethod
+    def forward(ctx, x):
+        return x
+
+    @staticmethod
+    def backward(ctx, grad):
+        return grad.contiguous()
+
+
+def _contiguous_grad(x: torch.Tensor) -> torch.Tensor:
+    """Identity in forward, makes gradient contiguous in backward.
+
+    Quack's RMSNorm backward kernel requires contiguous gradients (stride[-1]==1)
+    but upstream ops like attention permute can produce non-contiguous ones.
+    """
+    return _ContiguousGrad.apply(x) if x.requires_grad else x
+
+
 @dataclass
 class RMSNormConfig:
     hidden_size: int
@@ -15,14 +48,15 @@ class RMSNormConfig:
 @use_kernel_forward_from_hub("RMSNorm")
 class RMSNorm(nn.Module):
     def __init__(self, config: RMSNormConfig) -> None:
-        """
-        Glm4MoeRMSNorm is equivalent to T5LayerNorm
-        """
         super().__init__()
         self.weight = nn.Parameter(torch.ones(config.hidden_size))
         self.variance_epsilon = config.eps

     def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
+        quack_fn = _get_quack_rmsnorm() if hidden_states.is_cuda else None
+        if quack_fn is not None:
+            out = quack_fn(hidden_states, self.weight, eps=self.variance_epsilon)
+            return _contiguous_grad(out)
         input_dtype = hidden_states.dtype
         hidden_states = hidden_states.to(torch.float32)
         variance = hidden_states.pow(2).mean(-1, keepdim=True)
diff --git a/src/prime_rl/trainer/sft/train.py b/src/prime_rl/trainer/sft/train.py
index 67e27b74b9..7df08f40cf 100644
--- a/src/prime_rl/trainer/sft/train.py
+++ b/src/prime_rl/trainer/sft/train.py
@@ -47,7 +47,7 @@
 from prime_rl.utils.utils import clean_exit, to_col_format
 import torch.distributed as dist
 from liger_kernel.transformers.cross_entropy import LigerCrossEntropyLoss
-from prime_rl.trainer.models.layers.lm_head import FusedCrossEntropyOutputLinear
+from prime_rl.trainer.models.layers.lm_head import FUSED_CE_IGNORE_INDEX

 from torchtitan.distributed.utils import clip_grad_norm_

@@ -119,9 +119,8 @@ def train(config: SFTConfig):
     # Initialize the model and tokenizer
     logger.info(f"Initializing model ({config.model})")
     loading_from_ckpt_later = config.ckpt and checkpoint_step is not None
-    model = setup_model(
-        config.model, parallel_dims, loading_from_ckpt_later, fused_cross_entropy=config.loss_impl == "liger_fused"
-    )
+    fused_cross_entropy: bool | str = {"liger_fused": "liger", "quack_fused": "quack"}.get(config.loss_impl, False)
+    model = setup_model(config.model, parallel_dims, loading_from_ckpt_later, fused_cross_entropy=fused_cross_entropy)

     if parallel_dims.cp_enabled:
         setup_hybrid_cp(model, cp_group, cp_rank, parallel_dims.cp)
@@ -193,7 +192,7 @@ def train(config: SFTConfig):
             ce_loss = LigerCrossEntropyLoss(reduction="none")
         case "torch":
             ce_loss = CrossEntropyLoss(reduction="none")
-        case "liger_fused":
+        case "liger_fused" | "quack_fused":
             pass  # loss is computed inside the fused lm_head
         case _:
             raise ValueError(f"Invalid loss implementation: {config.loss_impl}")
@@ -216,9 +215,9 @@ def compute_loss(micro_batch: dict) -> tuple[torch.Tensor, torch.Tensor]:
         token_count = loss_mask.sum(dtype=torch.int64)

         with maybe_activation_offloading(config.model.ac_offloading):
-            if config.loss_impl == "liger_fused":
+            if config.loss_impl in ("liger_fused", "quack_fused"):
                 masked_target_ids = target_ids.clone()
-                masked_target_ids[~loss_mask] = FusedCrossEntropyOutputLinear.IGNORE_INDEX
+                masked_target_ids[~loss_mask] = FUSED_CE_IGNORE_INDEX
                 out = forward(model, input_ids, position_ids, labels=masked_target_ids)
                 loss_sum = out["loss"] * token_count
             else:

PATCH

echo "Patch applied successfully."
