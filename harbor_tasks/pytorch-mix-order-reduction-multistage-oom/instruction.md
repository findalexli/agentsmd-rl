# Bug: Mix-order reduction causes out-of-shared-memory errors

## Problem

The PyTorch inductor's mix-order reduction feature can cause "out of shared memory" compilation failures on certain workloads — specifically, models with large reduction dimensions (e.g., Eagle3-style architectures with dual RMSNorm and large attention patterns).

The root cause is in the persistent reduction autotuning heuristics in `torch/_inductor/runtime/triton_heuristics.py`. The `persistent_reduction` function generates autotuning configurations for Triton kernels and currently allows multiple pipeline stages (`NUM_STAGES` up to 2 or 3 depending on `rnumel_hint`). Each additional pipeline stage multiplies shared memory usage, which can exceed the GPU's shared memory capacity for certain kernel shapes.

## Relevant files

- `torch/_inductor/runtime/triton_heuristics.py` — the `persistent_reduction` function, specifically the section that computes `MAX_NUM_STAGES` for mix-order reduction configs
- `torch/_inductor/config.py` — the `triton` config class where mix-order reduction settings live
- `torch/_inductor/codegen/triton.py` — the `inductor_meta_common` method that passes config values to runtime heuristics

## Expected behavior

There should be a way to control whether multi-stage pipelines are allowed for mix-order reduction, defaulting to a safe single-stage configuration that avoids shared memory issues. The setting should be configurable via both Python config and an environment variable, following the pattern of other mix-order reduction settings in the config.

## Reproduction context

The issue manifests when compiling models that combine:
- Dual RMSNorm layers on concatenated inputs
- Large sequence lengths (16K+)
- Multiple attention heads with GQA (grouped query attention)
- Rotary position embeddings

See https://github.com/pytorch/pytorch/issues/175250 for the original report.
