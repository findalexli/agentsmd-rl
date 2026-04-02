# Integrate quack-kernels for SFT fused loss and RMSNorm acceleration

The prime-rl project currently supports Liger kernels for fused cross-entropy loss during SFT training (`loss_impl = "liger_fused"`), which fuses the LM head projection with the cross-entropy loss to avoid materializing full logits. We need to add an analogous integration with quack-kernels, which provides chunked linear + cross-entropy computation using CuTe DSL CUDA kernels.

## What needs to change

### 1. SFT Config — new `loss_impl` option
The `loss_impl` field in `SFTConfig` (`src/prime_rl/configs/sft.py`) currently accepts `"liger"`, `"torch"`, and `"liger_fused"`. Add a new option that uses quack-kernels for fused loss computation.

### 2. LM Head — new fused output linear class
In `src/prime_rl/trainer/models/layers/lm_head.py`, there is an existing `FusedCrossEntropyOutputLinear` class that implements Liger-based fused loss. A similar class is needed for quack-kernels that:
- Chunks the linear projection and cross-entropy computation
- Uses `quack.linear_cross_entropy.chunked_linear_cross_entropy` when labels are provided
- Falls back to a standard linear forward when labels are `None`
- Uses the same ignore index convention as the existing fused class

### 3. LM Head injection — dispatch multiple implementations
The `inject_prime_lm_head` function currently treats `fused_cross_entropy` as a boolean. It needs to support dispatching to different fused implementations based on which backend is requested. The function signature and dispatch logic need updating.

Quack-kernels do **not** support Gemma logit softcapping — attempting to use quack fusion with a Gemma model should raise a clear error.

### 4. RMSNorm — optional quack acceleration
The `RMSNorm` class in `src/prime_rl/trainer/models/layers/norms.py` should optionally use quack-kernels for acceleration on CUDA (Hopper architecture / compute capability 9.0+). Requirements:
- Lazy-load the quack rmsnorm function, returning `None` if unavailable or on incompatible hardware
- Only use quack on CUDA tensors; CPU tensors should use the existing torch path
- Handle the fact that quack's RMSNorm backward kernel requires contiguous gradients, while upstream ops like attention permute can produce non-contiguous ones

### 5. SFT training loop wiring
In `src/prime_rl/trainer/sft/train.py`, the training loop needs to:
- Map the new config option to the appropriate `fused_cross_entropy` value for `setup_model()`
- Handle the new fused loss case alongside the existing one in the loss computation and forward pass

### 6. Packaging
Add a `quack` optional extra to `pyproject.toml` depending on `quack-kernels>=0.3.3`.

## Relevant files
- `src/prime_rl/configs/sft.py`
- `src/prime_rl/trainer/model.py` — `setup_model()` signature
- `src/prime_rl/trainer/models/layers/lm_head.py`
- `src/prime_rl/trainer/models/layers/norms.py`
- `src/prime_rl/trainer/sft/train.py`
- `pyproject.toml`
