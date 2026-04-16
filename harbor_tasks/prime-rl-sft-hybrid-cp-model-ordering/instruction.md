# Bug: SFT trainer crashes during context-parallel initialization

## Summary

The SFT trainer crashes with a `NameError` when context parallelism (CP) is enabled in the config (`cp > 1`). The trainer fails before training begins.

## Reproduction

Run the SFT trainer with context parallelism enabled (`cp > 1`). The trainer crashes during initialization.

## File

`src/prime_rl/trainer/sft/train.py`

## Relevant symbols

- `train()` function in `src/prime_rl/trainer/sft/train.py`
- Calls that must be retained: `setup_model()`, `setup_hybrid_cp()`, `setup_ckpt_managers()`, `substitute_ring_attn()`

## Expected behavior

When `cp > 1` is set in the config, the trainer should initialize successfully and begin training without crashing.

## Constraints

- `train()` must have at least 20 top-level statements
- `setup_hybrid_cp()` must not be wrapped in a try/except block
- The repo must pass ruff lint and format checks (see `pyproject.toml` for configuration)