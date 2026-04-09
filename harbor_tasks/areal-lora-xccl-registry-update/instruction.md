# LoRA XCCL Weight Update Breaks Model Name Registry

## Problem

After performing a LoRA weight update through the XCCL (cross-collective communication) path, the `OpenAIServingModels` registry still references the previous versioned LoRA name (e.g., `lora-gsm8k-v0`). This means subsequent inference requests targeting the new versioned LoRA adapter (e.g., `lora-gsm8k-v1`) fail to resolve because the name-to-ID mapping was never updated.

Additionally, the distributed weight update request builder does not forward the LoRA metadata payload to the XCCL update endpoint, so the server endpoint never receives the information it would need to update the registry.

## Expected Behavior

After a successful LoRA weight update via XCCL:

1. The XCCL update endpoint should receive the LoRA metadata (name, int_id, etc.) in the request payload
2. The `openai_serving_models.lora_requests` registry should be updated to map the new versioned LoRA name to the correct `lora_int_id`, and the old name entry should be removed

## Files to Look At

- `areal/engine/vllm_remote.py` — Builds the HTTP requests for distributed weight updates. The `build_distributed_weight_update_requests` method in `VLLMBackend` constructs the payload sent to the XCCL update endpoint.
- `areal/engine/vllm_ext/areal_vllm_server.py` — FastAPI server endpoints for vLLM weight updates. The `update_weight_lora_xccl` endpoint handles the XCCL-based LoRA weight update but does not currently update the model name registry.
