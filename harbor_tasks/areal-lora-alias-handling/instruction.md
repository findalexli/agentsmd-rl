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

1. **No runtime path fallback**: When an adapter is updated through XCCL without a filesystem path, the registry has no `lora_path` to record. A runtime-generated fallback path should be used instead so vLLM can still construct a `LoRARequest` for routing.

2. **Stale aliases accumulate**: Registering a new name for an existing adapter id does not clean up the old name entry, so the same adapter appears under multiple aliases in the registry.

3. **Inline mutation**: The existing code mutates `req.lora_name` directly instead of creating a new registry entry.

4. **Unconditional registry update**: The registry is updated regardless of whether the XCCL operation succeeded, which can leave stale data when XCCL fails.

## Required Behaviors

### Path Inference Helper

Add a path inference helper function that accepts `serving_models`, `lora_name`, and `lora_int_id` as parameters. The function must:

1. If an entry with the given `lora_name` already exists in `serving_models.lora_requests` and has a non-empty `lora_path`, return that path
2. Otherwise, search the registry for any entry with a matching `lora_int_id` that has a non-empty `lora_path`, and return it
3. If no path is found, generate and return a stable runtime identifier that encodes the adapter name so vLLM can construct a valid `LoRARequest` for routing

### Registry Registration Helper

Add a registration helper that accepts `app` (the FastAPI app), `lora_name`, `lora_int_id`, and `base_model_name` (which may be `None`). The helper must:

1. Access the `lora_requests` registry from `app.state.openai_serving_models`
2. Remove any existing registry entries for the same `lora_int_id` but with a different `lora_name` (stale aliases)
3. Create a new `LoRARequest` object with the provided `lora_name`, `lora_int_id`, and the inferred `lora_path` from the path inference helper
4. If `base_model_name` is provided, propagate it to the new `LoRARequest`
5. Insert the new entry under `lora_name` as the key
6. Log the registration using `logger.info`

### Success Gating

The XCCL update handler must only update the registry after confirming all XCCL operations succeeded. The registry update call must be conditional on the success of all operations in the result list — failed XCCL operations must not modify the registry.

### Import

The `LoRARequest` class from `vllm.lora.request` must be imported to create registry entries.

## Expected Outcomes

- Path inference returns an existing filesystem path when available, or a stable runtime-generated identifier when no path exists
- Registration creates a new `LoRARequest` object (not an in-place mutation) and propagates all fields including `base_model_name`
- Stale aliases (same adapter id, different name) are removed when a new name is registered
- Registry updates are gated on XCCL success; failed XCCL operations do not update the registry