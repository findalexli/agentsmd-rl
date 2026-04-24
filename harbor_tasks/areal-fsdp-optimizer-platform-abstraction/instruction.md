# Abstract hardcoded CUDA calls in PerLayerOptimWrapper

## Problem

The `PerLayerOptimWrapper` class in `areal/engine/fsdp_utils/optimizer.py` directly uses
`torch.cuda.Stream`, `torch.cuda.Event`, `torch.cuda.current_stream()`,
`torch.cuda.stream()`, and `torch.cuda.empty_cache()` instead of going through the
project's `current_platform` abstraction layer from `areal.infra.platforms`.

This means the optimizer pipeline synchronization code is hardcoded to NVIDIA CUDA and
cannot run on other accelerator backends (NPU, CPU fallback, etc.) that the platform
abstraction already supports.

There are TODO comments in `_init_streams_and_events()` and `step()` that note this
should be abstracted via `current_platform`.

## Relevant Files

- `areal/engine/fsdp_utils/optimizer.py` — `PerLayerOptimWrapper` class, specifically:
  - `_init_streams_and_events()` method (~line 478)
  - `step()` method (~line 585)
- `areal/infra/platforms/` — the `current_platform` abstraction layer that should be
  used instead of direct `torch.cuda.*` calls

## Expected Behavior

All device-specific stream, event, and cache operations in `PerLayerOptimWrapper` should
go through `current_platform` so the code works on any supported accelerator backend.
The TODO comments requesting this abstraction should be resolved.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
