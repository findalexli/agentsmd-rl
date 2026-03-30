The runtime LoRA adapter alias handling in `areal/engine/vllm_ext/areal_vllm_server.py` is fragile after XCCL weight updates.

After a successful `update_weight_lora_xccl` call, the code updates the LoRA name in the `openai_serving_models.lora_requests` registry by:
1. Iterating over existing entries to find one matching `lora_int_id`
2. Deleting the old entry and mutating `req.lora_name` on the existing `LoRARequest` object
3. Re-inserting it under the new name

This approach has several problems:
- It mutates the existing `LoRARequest` object instead of creating a proper new one, which can leave stale metadata.
- It does not handle the case where the adapter is not found in the registry (only logs a warning but does not register a new entry).
- The `lora_path` is not preserved or inferred -- runtime XCCL updates do not come with a filesystem path, so there is no fallback.
- There is no cleanup of stale aliases when the same adapter id gets a new name.

Harden the registration path by introducing a dedicated helper that:
- Infers or preserves the `lora_path` from existing registry entries (falling back to a synthetic `xccl://` path for runtime updates)
- Creates a proper new `LoRARequest` with the correct metadata
- Removes stale aliases for the same adapter id
- Only updates the registry after confirming all XCCL weight updates succeeded
