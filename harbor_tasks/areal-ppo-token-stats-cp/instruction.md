# Fix: PPO token stats incorrect under context parallelism

## Problem

When using context parallelism (CP), the PPO actor and critic logging paths report incorrect `n_tokens` statistics. The token denominator used for stats logging is derived from local sliced tensors rather than from the full-batch metadata. Under context parallelism, intermediate tensors are per-rank, so using them produces per-shard counts instead of full-batch counts.

## Expected Behavior

The `n_tokens` denominator should reflect the full logical sequence length from the original micro-batch metadata, not from potentially-sliced intermediate tensors. When micro-batch metadata (`attention_mask`, `cu_seqlens`, `input_ids`) describes the full sequence, use that to derive the correct token denominator.

The corrected token denominator should:
- Be a boolean tensor with shape matching the full logical sequence
- Be derived from the micro-batch metadata that describes the complete sequence
- Prefer `attention_mask` over other metadata keys
- Fall back to `cu_seqlens` for packed sequences when `attention_mask` is absent
- Fall back to `input_ids` when its shape matches the fallback tensor shape
- Fall back to `torch.ones_like(fallback)` when no recognized metadata is available

## Implementation Requirements

Create a helper function `infer_token_denominator` in `areal/trainer/ppo/stats.py` that:
- Accepts `input_data: dict[str, Any]` (containing micro-batch metadata) and `fallback: torch.Tensor`
- Returns a `torch.Tensor` of boolean dtype
- Has type annotations on all parameters and on the return type
- Contains conditional fallback logic with at least 3 non-docstring statements

Both `areal/trainer/ppo/actor.py` and `areal/trainer/ppo/critic.py` must import and use this helper. The old per-rank token patterns must be replaced with calls to `infer_token_denominator`.

## Notes

- Both actor and critic logging paths are affected
- The fix must work correctly under context parallelism where intermediate tensors are sliced per-rank
- The function must handle these metadata keys: `attention_mask`, `cu_seqlens`, `input_ids`
- No wildcard imports, no bare print() calls, no hardcoded paths