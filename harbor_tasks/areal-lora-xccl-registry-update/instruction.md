# LoRA XCCL Weight Update Breaks Model Name Registry

## Problem

After performing a LoRA weight update through the XCCL (cross-collective communication) path, the model name registry still references the previous versioned LoRA name. This means subsequent inference requests targeting the new versioned LoRA adapter fail to resolve because the name-to-ID mapping was never updated.

Additionally, the distributed weight update request builder may not be forwarding the LoRA metadata payload to the XCCL update endpoint, so the server endpoint never receives the information it would need to update the registry.

## Expected Behavior

After a successful LoRA weight update via XCCL:

1. **Payload forwarding**: When a LoRA weight update is requested, the XCCL update request to the LoRA-specific endpoint must include metadata that identifies the LoRA adapter being updated, so the server can update its registry accordingly.

2. **Registry update**: After the LoRA XCCL weight update completes, the server's registry must reflect the new versioned LoRA name and its integer identifier. The old versioned name entry should no longer be present.

## Notes

- The LoRA naming convention uses a version suffix in the format `{lora_name}-v{version}` (e.g., `gsm8k-lora-v1`).
- When LoRA is not in use, the XCCL weight update payload should remain empty.
- Only the LoRA entries in the registry should be modified; other adapters must remain untouched.