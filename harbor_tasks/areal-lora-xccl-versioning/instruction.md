There is a LoRA versioning bug across two files in AReaL's vLLM engine integration:

**1. Missing registry update in `areal/engine/vllm_ext/areal_vllm_server.py`**

The `update_weight_lora_xccl` endpoint updates LoRA weights in the vLLM engine via XCCL, but does not update the corresponding LoRA name in the `OpenAIServingModels` registry. The registry maintains the mapping between `lora_name` and `lora_int_id`. After a weight update, the registry still references the previous versioned LoRA name (e.g., `lora-gsm8k-v0`) even though the weights correspond to the new version (e.g., `lora-gsm8k-v1`). This causes requests targeting the new versioned LoRA name to fail resolution.

The endpoint currently takes no request body parameter (`raw_request: Request` only), so it has no access to the new LoRA name or int ID to update the registry.

**2. Empty payload in `areal/engine/vllm_remote.py`**

In `build_distributed_weight_update_requests`, the `update_endpoint` request always sends an empty payload `{}`, even for LoRA XCCL updates. This means the LoRA metadata (name, int_id, base_model_name, etc.) is not forwarded to the vLLM server's update endpoint, so even if the endpoint accepted a request body, it would not receive the necessary fields.

Fix both issues:
1. Add an `UpdateWeightsFromXcclRequestLora` request parameter to the `update_weight_lora_xccl` endpoint and update the registry after successful weight updates.
2. Pass the full LoRA payload (not empty `{}`) in the update request when `meta.use_lora` is true.
