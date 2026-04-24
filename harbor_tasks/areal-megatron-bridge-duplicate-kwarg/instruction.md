# Bug: MegatronEngine `megatron-bridge` code path is unusable

## Summary

When `bridge_cls` is set to `"megatron-bridge"` in a MegatronEngine configuration, the engine fails immediately during initialization. The `_build_hf_mcore_bridge()` method in `areal/engine/megatron_engine.py` cannot be called at all for this code path — Python rejects the code before runtime.

## Reproduction

Any attempt to instantiate a `MegatronEngine` with `bridge_cls="megatron-bridge"` triggers a Python error before the method body can execute — Python rejects the code due to a pre-runtime error in a function call.

## Where to look

- `areal/engine/megatron_engine.py`, method `_build_hf_mcore_bridge`, inside the branch for `"megatron-bridge"` bridge class.

## Expected behavior

The `megatron-bridge` code path should initialize successfully, creating the bridge object with the model path, remote code trust, and dtype configuration.

## Notes

- The `"mbridge"` code path in the same method works fine.
- This was introduced in the megatron bridge adaptation feature.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
