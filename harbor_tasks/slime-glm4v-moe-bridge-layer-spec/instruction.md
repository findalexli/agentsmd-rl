# GLM-4.6V Megatron Bridge: Incorrect Layer Spec Construction

## Bug Description

The GLM-4.6V MoE megatron bridge in `slime_plugins/megatron_bridge/glm4v_moe.py` has two related bugs in how it constructs transformer layer specifications for the mixed dense/MoE architecture.

### Issue 1: Wrong layer spec function

The `provide()` method in `Glm4vMoeVLModelProvider` (around line 430) calls a layer spec function that produces a single uniform spec for all layers. However, GLM-4.6V uses a mixed architecture where layer 0 is dense and remaining layers are MoE. The current function doesn't respect the per-layer MoE frequency configuration, so all layers get the same MoE spec instead of having the first layer(s) be dense.

The layer spec construction needs to be aware of the per-layer MoE configuration so that dense and MoE layers get different specs.

### Issue 2: Wrong type for `moe_layer_freq`

In `provider_bridge()` (around line 480), the `moe_layer_freq` value is constructed as a Python expression string (e.g., `"[0]*1+[1]*45"`) instead of an actual list. The downstream megatron-core code expects this to be a proper Python list of integers indicating which layers are dense (0) vs MoE (1). The string representation causes incorrect behavior when megatron-core tries to index into it.

### Relevant Context

- The model has `first_k_dense_replace` dense layers followed by MoE layers
- The provider class inherits from `Qwen3MoEModelProvider` and acts as a `TransformerConfig`
- The layer spec function needs access to the full config to determine per-layer types

### Files to Modify

- `slime_plugins/megatron_bridge/glm4v_moe.py`
