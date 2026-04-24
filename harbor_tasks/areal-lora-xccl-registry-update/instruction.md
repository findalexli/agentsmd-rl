# LoRA XCCL Weight Update Breaks Model Name Registry

## Problem

After performing a LoRA weight update through the XCCL (cross-collective communication) path, the model name registry still references the previous versioned LoRA name. This means subsequent inference requests targeting the new versioned LoRA adapter fail to resolve because the name-to-ID mapping was never updated.

Additionally, the distributed weight update request builder may not be forwarding the LoRA metadata payload to the XCCL update endpoint, so the server endpoint never receives the information it would need to update the registry.

## Files to Modify

The fix requires changes in two files:

1. **`areal/engine/vllm_remote.py`**: Contains the `build_distributed_weight_update_requests` method in the `VLLMBackend` class. This method constructs the HTTP requests sent during XCCL weight updates.

2. **`areal/engine/vllm_ext/areal_vllm_server.py`**: Contains the `update_weight_lora_xccl` async function (registered at the `/areal_update_weights_lora_xccl` endpoint). This function receives the weight update request and must update the registry after weights are updated.

## Expected Behavior

After a successful LoRA weight update via XCCL:

1. **Payload forwarding**: When a LoRA weight update is requested (when `use_lora` is True in the metadata), the XCCL update request to the LoRA-specific endpoint (`/areal_update_weights_lora_xccl`) must include a payload with the following keys:
   - `lora_name`: The versioned LoRA name in the format `{lora_name}-v{version}` (e.g., `gsm8k-lora-v1`)
   - `lora_int_id`: The integer identifier for the LoRA adapter

   When LoRA is not in use (`use_lora` is False), the XCCL weight update payload should remain empty (`{}`).

2. **Registry update**: After the LoRA XCCL weight update completes, the server's `openai_serving_models.lora_requests` registry must reflect the new versioned LoRA name and its integer identifier. The old versioned name entry should no longer be present. The endpoint must:
   - Access the models registry via `raw_request.app.state.openai_serving_models`
   - Find the existing LoRA entry with matching `lora_int_id` in `lora_requests`
   - Remove the old entry and add a new entry with the updated `lora_name`

## Notes

- The LoRA naming convention uses a version suffix in the format `{lora_name}-v{version}` (e.g., `gsm8k-lora-v1`).
- When LoRA is not in use, the XCCL weight update payload to the non-LoRA endpoint (`/areal_update_weights_xccl`) should remain empty.
- Only the LoRA entries in the registry should be modified; other adapters must remain untouched.
- The gold solution uses the existing logger instance (`logger.info`, `logger.warning`) rather than print statements.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
