# Bug: `encode_image_base64` crashes on torch.Tensor input & unnecessary base64 encoding in detokenizer

## Problem 1: `encode_image_base64` doesn't handle tensor inputs

The function `encode_image_base64()` in `python/sglang/utils.py` handles `str` (file paths) and `bytes` inputs correctly, but when a GPU-decoded image is passed as a `torch.Tensor` (e.g., from torchvision or nvJPEG decode), the function falls into the `else` branch that assumes a PIL Image. It then tries to call `.save()` on the tensor, which crashes with an `AttributeError`.

The function needs to detect `torch.Tensor` inputs, convert them to PIL Images (handling the CHW uint8 format and potential GPU residence), and then proceed with the normal PIL encoding path.

## Problem 2: Redundant base64 encoding in the detokenizer

In `python/sglang/srt/managers/detokenizer_manager.py`, the `_extract_routed_experts` method converts routed expert tensors to base64 strings before wrapping them in `BatchStrOutput`. However, `BatchStrOutput` is serialized via pickle over ZMQ, so this base64 conversion at the IPC boundary is wasteful — the tensors can be passed through as-is.

The base64 encoding should instead happen in `python/sglang/srt/managers/tokenizer_manager.py`, in the `_handle_batch_output` method, right before the data is placed into the HTTP response `meta_info`. This is the actual serialization boundary where base64 is needed (JSON over HTTP).

The `_extract_routed_experts` method should be removed from the detokenizer, and the `routed_experts` field should be passed through directly from `BatchTokenIDOutput` to `BatchStrOutput`. Then in the tokenizer manager, each individual `routed_experts` tensor should be base64-encoded when building the per-request metadata.

## Problem 3: Noisy NUMA warning

In `python/sglang/srt/utils/numa_utils.py`, a `logger.warning()` fires every time `numactl` is not found when NUMA binding is enabled. In containerized environments where numactl is irrelevant, this creates unnecessary log noise. It should be `logger.debug()` instead.

## Files to modify

- `python/sglang/utils.py` — add torch.Tensor handling to `encode_image_base64`
- `python/sglang/srt/managers/detokenizer_manager.py` — remove `_extract_routed_experts`, pass tensors through
- `python/sglang/srt/managers/tokenizer_manager.py` — add base64 encoding for routed_experts in `_handle_batch_output`
- `python/sglang/srt/utils/numa_utils.py` — change warning to debug
