# FP8 Blockwise Training Crashes with Tensor Parallelism and MoE Experts

## Problem

FP8 blockwise training has several robustness issues when used with tensor parallelism (TP) and Mixture-of-Experts (MoE) configurations:

1. **Expert shard validation is missing.** `validate_fp8_shard_alignment` in `areal/experimental/models/archon/fp8.py` only checks `nn.Linear` modules for block-alignment. `GroupedExperts` modules (which have 3D weight tensors `w1`, `w2`, `w3`) are silently skipped, causing Triton kernel crashes at runtime when per-expert dimensions aren't 128-aligned after TP/ETP sharding.

2. **DTensor crash in dense FP8 forward.** After tensor parallelism, `nn.Linear.weight` becomes a DTensor, but `_fp8_linear_fwd` passes it directly to `fp8_blockwise_mm.apply()` which expects a local tensor. This crashes the FP8 matmul kernel.

3. **Scattered mode checks.** Multiple files check `fp8_config.mode != "disabled"` independently instead of using a centralized predicate, making the FP8-enabled check fragile and easy to get wrong.

4. **Overly permissive FP8 dtype acceptance.** `dequant_fp8_state_dict` in `fp8_checkpoint.py` accepts 4 FP8 dtypes, but `_prepare_fp8_state_dict` only creates `float8_e4m3fn`. Accepting other types risks silent data corruption if a non-e4m3fn checkpoint were loaded.

5. **Late failure on unsupported shard placements.** Loading FP8 checkpoints with column-sharded (Shard(1)) DTensor weights fails deep inside `_dequant_dtensor`, after expensive DCP I/O has already occurred. There's no early validation.

6. **Expert FP8 patch doesn't set `_fp8_block`.** `_patch_fp8_experts_forward` stores `_fp8_use_triton` but not `_fp8_block`, so `validate_fp8_shard_alignment` (which gates on `hasattr(mod, '_fp8_block')`) never checks expert modules.

## Expected Behavior

- `validate_fp8_shard_alignment` should inspect both `nn.Linear` and `GroupedExperts` modules for 128-block alignment after parallelism
- FP8 linear forward should handle DTensor weights (convert to local before matmul)
- A centralized `enabled` property on `ArchonFP8Config` should replace scattered `mode != "disabled"` checks
- FP8 checkpoint dequantization should only accept `float8_e4m3fn`
- Early validation should reject unsupported shard placements before DCP I/O
- Expert FP8 patching should store `_fp8_block` so alignment validation covers expert modules

## Files to Look At

- `areal/api/cli_args.py` — `ArchonFP8Config` dataclass, where the centralized enabled check belongs
- `areal/experimental/models/archon/fp8.py` — FP8 patching, expert forward, and shard alignment validation
- `areal/experimental/models/archon/fp8_checkpoint.py` — FP8 checkpoint dequantization and dtype handling
- `areal/experimental/engine/archon_checkpoint.py` — HF checkpoint loading, where early shard validation belongs
- `areal/experimental/engine/archon_engine.py` — Engine initialization, uses FP8 config mode checks
- `areal/experimental/engine/archon_utils.py` — Training config preparation, uses FP8 config mode checks
