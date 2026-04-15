# Fix: PPO token stats incorrect under context parallelism

## Problem

When using context parallelism (CP), the PPO actor and critic logging paths report incorrect `n_tokens` statistics. The token denominator used for stats logging is derived from local sliced tensors rather than from the full-batch metadata. Under context parallelism, intermediate tensors are per-rank, so using them produces per-shard counts instead of full-batch counts.

## Expected Behavior

The `n_tokens` denominator should reflect the full logical sequence length from the original micro-batch metadata, not from potentially-sliced intermediate tensors. When micro-batch metadata (`attention_mask`, `cu_seqlens`, `input_ids`) describes the full sequence, use that to derive the correct token denominator.

The corrected token denominator should:
- Be a boolean tensor with shape matching the full logical sequence
- Be derived from the micro-batch metadata that describes the complete sequence

## Notes

- Both actor and critic logging paths are affected
- The fix must work correctly under context parallelism where intermediate tensors are sliced per-rank
