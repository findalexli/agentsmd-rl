# Bug: MegatronEngine `megatron-bridge` code path is unusable

## Summary

When `bridge_cls` is set to `"megatron-bridge"` in a MegatronEngine configuration, the engine fails immediately during initialization. The `_build_hf_mcore_bridge()` method in `areal/engine/megatron_engine.py` cannot be called at all for this code path — Python rejects the code before runtime.

## Reproduction

Any attempt to instantiate a `MegatronEngine` with `bridge_cls="megatron-bridge"` triggers a Python error before the method body can execute. The error originates in the function call to `MegatronBridgeAutoBridge.from_hf_pretrained()` around line 377.

## Where to look

- `areal/engine/megatron_engine.py`, method `_build_hf_mcore_bridge`, specifically the `elif self.bridge_cls == "megatron-bridge"` branch.

## Expected behavior

The `megatron-bridge` code path should initialize successfully, creating the bridge object with the model path, remote code trust, and dtype configuration.

## Notes

- The `"mbridge"` code path in the same method works fine.
- This was introduced in the megatron bridge adaptation feature.
