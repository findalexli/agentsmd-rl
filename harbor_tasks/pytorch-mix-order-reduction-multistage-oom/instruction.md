# Bug: Mix-order reduction causes out-of-shared-memory errors

## Problem

The PyTorch inductor's mix-order reduction feature can cause "out of shared memory" compilation failures on certain workloads — specifically, models with large reduction dimensions (e.g., Eagle3-style architectures with dual RMSNorm and large attention patterns).

The root cause is in the persistent reduction autotuning heuristics. The autotuning currently allows multiple pipeline stages (`NUM_STAGES` up to 2 or 3 depending on the reduction element hint). Each additional pipeline stage multiplies shared memory usage, which can exceed the GPU's shared memory capacity for certain kernel shapes.

## Expected behavior

There should be a way to control whether multi-stage pipelines are allowed for mix-order reduction, defaulting to a safe single-stage configuration that avoids shared memory issues. The setting must:

- Default to `False` (disallowing multi-stage)
- Be configurable via the environment variable `TORCHINDUCTOR_MIX_ORDER_REDUCTION_ALLOW_MULTI_STAGES` (setting it to `1` enables multi-stage)
- Use an attribute name following the `mix_order_reduction_allow_*` pattern in the `triton` config class
- Propagate the config value through `inductor_meta` so the runtime heuristics respect it at runtime

When multi-stage is disabled, the heuristics must produce `NUM_STAGES=1` regardless of reduction size. When enabled with `rnumel_hint` ≤ 8192, it may produce up to 3 stages. When enabled with `rnumel_hint` > 8192, it must cap at 2 stages.

## Reproduction context

The issue manifests when compiling models that combine:
- Dual RMSNorm layers on concatenated inputs
- Large sequence lengths (16K+)
- Multiple attention heads with GQA (grouped query attention)
- Rotary position embeddings

See https://github.com/pytorch/pytorch/issues/175250 for the original report.