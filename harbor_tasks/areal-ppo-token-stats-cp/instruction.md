# Fix: PPO token stats inconsistent under context parallelism

## Problem

When using context parallelism (CP), the PPO actor and critic logging paths report incorrect `n_tokens` statistics. The token denominator used for stats logging is derived from local sliced tensors (`loss_mask`) rather than from the full-batch metadata. Under context parallelism, intermediate tensors like `loss_mask` are sliced per-rank, so using them as the `n_tokens` denominator produces per-shard counts instead of full-batch counts.

This affects both the actor (`areal/trainer/ppo/actor.py`) and critic (`areal/trainer/ppo/critic.py`) logging paths.

## Root Cause

In `ppo_update` and `grpo_loss_fn` (actor), `n_tokens` is set to `torch.ones_like(loss_mask, dtype=torch.bool)`, which inherits the local shard shape. Similarly in the critic's `ppo_loss_fn`, `n_tokens` is `torch.ones(value.shape[0], ...)`, also shard-local.

The original micro-batch metadata (`attention_mask`, `cu_seqlens`, or `input_ids`) still describes the full logical sequence, so it should be used to derive `n_tokens` instead of the potentially-sliced intermediate tensors.

## Expected Behavior

Create a helper function that infers the full token mask from micro-batch metadata:
1. Prefer `attention_mask` from `input_data` if available
2. Fall back to `cu_seqlens` (for packed sequences under CP)
3. Fall back to `input_ids` when its shape matches the fallback tensor
4. Otherwise, fall back to `torch.ones_like(fallback)`

Use this helper in both actor and critic logging paths.

## Files to Modify

- `areal/trainer/ppo/actor.py` -- replace `n_tokens` denominator calls
- `areal/trainer/ppo/critic.py` -- replace `n_tokens` denominator call
- Create `areal/trainer/ppo/stats.py` -- new helper `infer_token_denominator`
