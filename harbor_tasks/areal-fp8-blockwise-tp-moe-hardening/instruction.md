# FP8 Blockwise Training Hardening for Tensor Parallelism and MoE

## Context

AReaL supports FP8 blockwise training via torchao's blockwise quantization
(`mode: blockwise`).  The implementation has correctness gaps that cause
runtime crashes in common TP (tensor parallelism) and MoE (mixture-of-experts)
configurations.  This task requires hardening the FP8 code paths.

## Symptom Summary

When FP8 blockwise mode is enabled with tensor parallelism or MoE experts,
you may observe:

- Triton kernel crashes at runtime due to tensor dimension misalignment
- DTensor-related crashes inside FP8 matmul kernels
- Fragile mode checks that break when FP8 config fields are accessed inconsistently
- Silent data corruption risk if a checkpoint was saved with an unexpected FP8 dtype
- Wasted I/O when a checkpoint has an unsupported shard placement, failing only deep inside dequantization
- Expert modules not being checked for shard alignment, because alignment validation skips them

## Detailed Symptom Descriptions

### 1. Expert Shard Alignment Not Validated

When a model uses MoE (`GroupedExperts` modules with 3D weight tensors `w1`,
`w2`, `w3`) and FP8 blockwise mode with TP/ETP parallelism, the per-expert
weight dimensions may not be 128-aligned.  This causes a Triton kernel crash at
runtime.  The crash occurs deep inside the FP8 matmul; there is no early
validation that surfaces the alignment requirement before the kernel fires.

The relevant function is in
`areal/experimental/models/archon/fp8.py` and is called during model
initialization.

### 2. DTensor Crash in Dense FP8 Forward

After tensor parallelism, `nn.Linear.weight` becomes a `DTensor`.  The FP8
forward path in `areal/experimental/models/archon/fp8.py` passes the weight
directly to the blockwise matmul kernel.  Because the kernel expects a local
tensor, this causes a crash when the code is run with TP > 1.

### 3. Scattered FP8 Mode Checks

Several locations in the codebase check `fp8_config.mode != "disabled"` to
determine whether FP8 is active.  These checks are inconsistent in style and
easy to get wrong (e.g., negating the condition, or missing a branch).  The
check appears in engine initialization, config preparation, and shard
validation.

The relevant files include:
- `areal/api/cli_args.py` — `ArchonFP8Config` dataclass
- `areal/experimental/engine/archon_engine.py` — engine initialization
- `areal/experimental/engine/archon_utils.py` — training config preparation

### 4. Overly Permissive FP8 Checkpoint Dtype

When loading an FP8 checkpoint, the dequantization function accepts multiple
FP8 dtypes.  However, the FP8 state-dict preparation code only produces
`float8_e4m3fn`.  Accepting other dtypes risks silent data corruption if a
checkpoint was saved with an unexpected format.

The relevant function is `dequant_fp8_state_dict` in
`areal/experimental/models/archon/fp8_checkpoint.py`.

### 5. Late Failure on Unsupported Shard Placements

Loading an FP8 checkpoint with column-sharded (`Shard(1)`) DTensor weights fails
deep inside `_dequant_dtensor`, after expensive DCP I/O has already occurred.
There is no early validation before the I/O.

The relevant file is `areal/experimental/engine/archon_checkpoint.py`.

### 6. Expert Modules Not Checked by Shard Alignment Validation

The shard alignment validation function uses `hasattr(mod, '_fp8_block')` as
the gate for whether to validate a module.  The expert forward patch stores
`_fp8_use_triton` on expert modules but not `_fp8_block`.  As a result, expert
modules are silently skipped during alignment validation.

The relevant functions are in `areal/experimental/models/archon/fp8.py`.

## Expected Correct Behavior

- FP8 shard alignment validation must inspect **both** `nn.Linear` and
  `GroupedExperts` modules and raise a `ValueError` for misaligned weights
  (including per-expert `w1`/`w2`/`w3` tensors)
- The FP8 linear forward path must handle `DTensor` weights gracefully
- All FP8-active checks should use a consistent predicate rather than raw
  `mode != "disabled"` comparisons
- FP8 checkpoint dequantization should only accept `float8_e4m3fn` dtype
- Checkpoint loading should validate shard placements **before** DCP I/O,
  raising `ValueError` for unsupported placements
- Expert forward patching must mark expert modules with the `_fp8_block`
  attribute so alignment validation covers them

## Files to Examine

- `areal/api/cli_args.py` — `ArchonFP8Config` dataclass, mode validation, `__post_init__`
- `areal/experimental/models/archon/fp8.py` — FP8 patching, expert forward, shard alignment validation
- `areal/experimental/models/archon/fp8_checkpoint.py` — FP8 checkpoint dequantization and dtype handling
- `areal/experimental/engine/archon_checkpoint.py` — HF checkpoint loading, shard placement validation
- `areal/experimental/engine/archon_engine.py` — engine initialization, FP8 mode checks
- `areal/experimental/engine/archon_utils.py` — training config preparation, FP8 mode checks

## Key Types and Names

- **Dataclass:** `ArchonFP8Config` (`areal/api/cli_args.py`)
- **Module type:** `GroupedExperts` (with 3D weights `w1`, `w2`, `w3`)
- **Config attribute:** `mode` (values: `"blockwise"`, `"disabled"`), `use_triton`
- **Module attributes:** `_fp8_block`, `_fp8_use_triton`
- **DTensor method:** `to_local()`
- **Function:** `validate_fp8_shard_alignment` (`areal/experimental/models/archon/fp8.py`)
- **Function:** `_patch_fp8_experts_forward` (`areal/experimental/models/archon/fp8.py`)
- **Function:** `_fp8_linear_fwd` (`areal/experimental/models/archon/fp8.py`)
- **Function:** `dequant_fp8_state_dict` (`areal/experimental/models/archon/fp8_checkpoint.py`)
- **Function:** `_check_fp8_shard_compatibility` (`areal/experimental/engine/archon_checkpoint.py`)
- **Shard type:** `Shard` (`torch.distributed.tensor.placement_types`)
- **Valid FP8 dtype:** `torch.float8_e4m3fn`
- **Invalid FP8 dtypes (must reject):** `torch.float8_e5m2`, `torch.float8_e4m3fnuz`, `torch.float8_e5m2fnuz`

## Error Messages

When misaligned weights are detected, `ValueError` is raised with a message
that includes the module name and the non-aligned shape.  When unsupported
shard placements are detected, `ValueError` is raised describing the
`Shard(1)` incompatibility with FP8 checkpoint loading.

When `mode="blockwise"` but `use_triton=False`, `ArchonFP8Config.__post_init__`
raises `ValueError` with a message about `use_triton` being required for FP8.

## Acceptance Criteria

Your fix is correct when:

1. `validate_fp8_shard_alignment` checks both `nn.Linear` and `GroupedExperts`
   modules, inspecting `w1`/`w2`/`w3` for the 3D expert tensors, and raises
   `ValueError` for misaligned expert weights
2. The FP8 linear forward path calls `to_local()` on the weight when it is a
   `DTensor`
3. All code paths that gate on FP8 being active use a consistent predicate
   (not raw `mode != "disabled"`)
4. `dequant_fp8_state_dict` only accepts `torch.float8_e4m3fn`; the other
   three FP8 dtypes are rejected
5. `_check_fp8_shard_compatibility` validates shard placements before DCP I/O
   and raises `ValueError` for `Shard(1)` weights
6. Expert modules are marked with `_fp8_block` so alignment validation covers
   them
