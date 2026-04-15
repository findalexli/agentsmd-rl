# LoRA XCCL Weight Update Breaks Model Name Registry

## Problem

After performing a LoRA weight update through the XCCL (cross-collective communication) path, the `OpenAIServingModels` registry still references the previous versioned LoRA name (e.g., `lora-gsm8k-v0`). This means subsequent inference requests targeting the new versioned LoRA adapter (e.g., `lora-gsm8k-v1`) fail to resolve because the name-to-ID mapping was never updated.

Additionally, the distributed weight update request builder does not forward the LoRA metadata payload to the XCCL update endpoint, so the server endpoint never receives the information it would need to update the registry.

## Expected Behavior

After a successful LoRA weight update via XCCL:

1. **Payload forwarding**: When `use_lora=True`, the XCCL update request to the LoRA-specific endpoint must include a payload containing:
   - `lora_name`: the versioned LoRA name in format `{lora_name}-v{version}` (e.g., `gsm8k-lora-v1`)
   - `lora_int_id`: the integer LoRA identifier

   For the non-LoRA XCCL endpoint, the payload must be empty.

2. **Registry update**: After the LoRA XCCL weight update completes, the `openai_serving_models.lora_requests` registry must be updated to map the new versioned LoRA name to its `lora_int_id`, and the old versioned name entry must be removed.

## Files to Look At

- `areal/engine/vllm_remote.py` — Contains the distributed weight update request builder for the vLLM backend. It constructs the HTTP requests sent to the XCCL update endpoints.
- `areal/engine/vllm_ext/areal_vllm_server.py` — FastAPI server endpoints for vLLM weight updates. One endpoint handles XCCL-based LoRA weight updates.
