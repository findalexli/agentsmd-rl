# Task: areal-lora-alias-handling
**Repo:** `inclusionAI/AReaL` @ `02a25454bc8ff348b05ae2a62040d5ec48237e16`
**PR:** `1039`
**Target:** `areal/engine/vllm_ext/areal_vllm_server.py`

## Background

After a successful XCCL-based LoRA weight update, the `openai_serving_models.lora_requests` registry can end up with stale entries:

- The existing code mutates `req.lora_name` in-place on the existing `LoRARequest` object
- When an adapter is updated at runtime via XCCL (no filesystem path involved), there is no fallback path to record
- When the same adapter id is assigned a new name, any previous alias for that adapter remains in the registry, creating duplicates

## Problem Symptoms

1. **No runtime path fallback**: When an adapter is updated through XCCL without a filesystem path, the registry has no `lora_path` to record. A runtime-generated fallback path should be used instead.

2. **Stale aliases accumulate**: Registering a new name for an existing adapter id does not clean up the old name entry, so the same adapter appears under multiple aliases in the registry.

3. **Inline mutation**: The existing code mutates `req.lora_name` directly instead of creating a new registry entry.

4. **Unconditional registry update**: The registry is updated regardless of whether the XCCL operation succeeded, which can leave stale data when XCCL fails.

## Required Behaviors

### Path Inference Helper

Add a path inference helper function named `_infer_runtime_lora_path` that accepts exactly three parameters in this order: `serving_models`, `lora_name`, `lora_int_id`. The function must:

1. If an entry with the given `lora_name` already exists in `serving_models.lora_requests` and has a non-empty `lora_path`, return that path
2. Otherwise, search the registry for any entry with a matching `lora_int_id` that has a non-empty `lora_path`, and return it
3. If no path is found, generate and return a synthetic runtime path with the prefix `xccl://` followed by the `lora_name` (e.g., `xccl://my-adapter`)

### Registry Registration Helper

Add a registration helper function named `_register_runtime_lora_name` that accepts exactly these parameters: `app` (the FastAPI app), `lora_name`, `lora_int_id`, and `base_model_name` (which may be `None`). The function must:

1. Access `app.state.openai_serving_models.lora_requests` as the registry
2. Remove any existing registry entries for the same `lora_int_id` but with a different `lora_name` (stale aliases)
3. Create a new `LoRARequest` object with the provided `lora_name`, `lora_int_id`, and the inferred `lora_path` from the path inference helper
4. If `base_model_name` is provided (not `None`), propagate it to the new `LoRARequest`
5. Insert the new entry under `lora_name` as the key
6. Log the registration using `logger.info`

### Success Gating

In `update_weight_lora_xccl`, the registry update must only occur after confirming all XCCL operations succeeded. The call to the registration helper must be gated inside an `if all(success for success, _ in ret_list):` check (or equivalent) that verifies every entry in `ret_list` succeeded.

### Import

The `LoRARequest` class from `vllm.lora.request` must be imported to create registry entries.

## Expected Outcomes

- Path inference returns an existing filesystem path when available, or a synthetic `xccl://`-prefixed path when no path exists
- Registration creates a new `LoRARequest` object (not an in-place mutation) and propagates all fields including `base_model_name`
- Stale aliases (same adapter id, different name) are removed when a new name is registered
- Registry updates are gated on XCCL success; failed XCCL operations do not update the registry