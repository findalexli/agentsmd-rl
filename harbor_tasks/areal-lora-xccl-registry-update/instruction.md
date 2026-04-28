# LoRA XCCL Weight Update Breaks Model Name Registry

## Problem

After performing a LoRA weight update through the XCCL (cross-collective communication) path, the model name registry still references the previous versioned LoRA name. This means subsequent inference requests targeting the new versioned LoRA adapter fail to resolve because the name-to-ID mapping was never updated.

Additionally, the distributed weight update request builder may not be forwarding the LoRA metadata payload to the XCCL update endpoint, so the server endpoint never receives the information it would need to update the registry.

## Where to Look

The fix requires changes in two locations:

1. **Distributed weight update request builder**: The `VLLMBackend` class contains a method `build_distributed_weight_update_requests` that constructs the HTTP requests sent during XCCL weight updates. This method lives in the engine's remote module.

2. **XCCL LoRA weight update endpoint handler**: The async function `update_weight_lora_xccl` is registered at the `/areal_update_weights_lora_xccl` endpoint. This function, defined in the server's vLLM extension module, receives the weight update request and must update the registry after weights are updated.

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

- `ruff format` and `ruff check`
