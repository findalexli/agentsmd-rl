# areal-lora-alias-handling

**Repo:** `inclusionAI/AReaL` @ `02a25454bc8ff348b05ae2a62040d5ec48237e16`
**PR:** `1039`
**Target:** `areal/engine/vllm_ext/areal_vllm_server.py`

## Background

After a successful `update_weight_lora_xccl` call, the code currently updates the LoRA name in the `openai_serving_models.lora_requests` registry by:
1. Iterating over existing entries to find one matching `lora_int_id`
2. Mutating `req.lora_name` on the existing `LoRARequest` object
3. Re-inserting it under the new name

This approach has problems:
- Mutating the existing `LoRARequest` object instead of creating a proper new one can leave stale metadata
- It only logs a warning when the adapter is not found in the registry; it does not register a new entry
- `lora_path` is not preserved or inferred — runtime XCCL updates do not come with a filesystem path, so there is no fallback
- No cleanup of stale aliases when the same adapter id gets a new name

## Required Changes

### 1. Path Inference Helper

Add a helper named `_infer_runtime_lora_path` that accepts `(serving_models, lora_name, lora_int_id)` and returns a `str`:

- If an entry with `lora_name` already exists in `serving_models.lora_requests` and that entry has a non-empty `lora_path`, return that path
- Otherwise, scan all entries in the registry and return the `lora_path` from the first entry whose `lora_int_id` matches — but only if that entry also has a non-empty `lora_path`
- If neither condition yields a path, return a synthetic path of the form `xccl://{lora_name}` (e.g., `xccl://adapter-v1`)

### 2. Registration Helper

Add a helper named `_register_runtime_lora_name` that accepts `(app, *, lora_name, lora_int_id, base_model_name)`:

- Access `app.state.openai_serving_models.lora_requests`
- Compute `runtime_lora_path` by calling `_infer_runtime_lora_path(serving_models, lora_name, lora_int_id)`
- **Remove stale aliases**: iterate over all entries in `lora_requests` and delete any entry whose `lora_int_id` matches `lora_int_id` but whose `lora_name` differs from `lora_name` (keep unrelated adapters untouched)
- Create a new `LoRARequest` object with `lora_name`, `lora_int_id`, and `lora_path=runtime_lora_path`
- If `base_model_name` is not `None`, set `lora_request.base_model_name` to that value
- Insert the new `LoRARequest` into `lora_requests` under the key `lora_name`
- Log the registration using `logger.info`

### 3. Gate Registration on XCCL Success

In `update_weight_lora_xccl`, the registry update must be conditional on XCCL success. After the call to `llm.engine_core.call_utility_async("areal_injected_update_weight_lora_xccl")` returns `ret_list`, only invoke `_register_runtime_lora_name` if `all(success for success, _ in ret_list)` is true.

## Expected Outcomes

- `_infer_runtime_lora_path` returns the existing filesystem path when one is already registered for the adapter, or `xccl://{name}` when no path is available
- `_register_runtime_lora_name` always creates a new `LoRARequest` object (not a mutated one), propagates `base_model_name`, and removes any prior alias for the same adapter id
- The `update_weight_lora_xccl` function does not mutate `req.lora_name` inline; it delegates to `_register_runtime_lora_name` only after confirming all XCCL operations succeeded