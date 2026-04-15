# Bug: SFT trainer crashes during context-parallel initialization

## Summary

The SFT trainer crashes with a `NameError` when context parallelism (CP) is enabled in the config (`cp > 1`). The trainer fails before training begins.

## Reproduction

Run the SFT trainer with context parallelism enabled. The trainer crashes during initialization.

## File

`src/prime_rl/trainer/sft/train.py`

## Relevant symbols

The `train()` function calls `setup_model()` to construct the model and `setup_hybrid_cp()` to configure hybrid DeltaNet/linear-attention modules for context-parallel execution. The `setup_hybrid_cp()` call must be guarded by `if parallel_dims.cp_enabled:` so it only runs when CP is active.

## Expected behavior

When `cp > 1` is set in the config, the trainer should initialize successfully and begin training without crashing.
