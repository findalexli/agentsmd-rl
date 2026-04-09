# Fix GLM-4V MoE Megatron Bridge

## Problem

The GLM-4V MoE megatron bridge in `slime_plugins/megatron_bridge/glm4v_moe.py` has two issues that cause incorrect model initialization:

1. **Wrong spec function in `provide()`**: The model provider's `provide()` method calls an outdated layer spec function that doesn't support per-layer MoE configuration (mixing dense and MoE layers). It passes individual MoE parameters instead of the transformer config object, which means the resulting spec doesn't respect the `moe_layer_freq` setting.

2. **Wrong `moe_layer_freq` type in `provider_bridge()`**: The bridge constructs `moe_layer_freq` as a string expression (e.g. `"[0]*1+[1]*39"`) instead of an actual Python list. Downstream megatron-core expects a list of integers indicating which layers are dense (0) vs MoE (1), not a string that would need to be eval'd.

## Expected Behavior

- The `provide()` method should use the correct spec function that accepts the full transformer config and generates per-layer specs respecting `moe_layer_freq`.
- The `provider_bridge()` method should pass `moe_layer_freq` as an actual `list[int]` (e.g. `[0, 1, 1, ..., 1]` for 1 dense + N-1 MoE layers).

## Files to Look At

- `slime_plugins/megatron_bridge/glm4v_moe.py` — GLM-4V MoE bridge: contains the `Glm4vMoeVLModelProvider.provide()` and `Glm4vMoeBridge.provider_bridge()` methods
