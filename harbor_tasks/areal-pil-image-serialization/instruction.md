AReaL's RPC serialization layer (`areal/infra/rpc/serialization.py`) cannot serialize two types of objects that are needed for VLM (Vision-Language Model) multimodal training workloads:

1. **PIL images** (e.g., `JpegImageFile`): When rollout data containing images is submitted via RPC, the `serialize_value()` function does not recognize PIL Image objects and they fall through to the default handling, which cannot JSON-serialize them.

2. **Hugging Face processors** (e.g., `Qwen2_5_VLProcessor` from `transformers.ProcessorMixin`): When checkpoint metadata containing a processor is serialized for RPC transmission, the `serialize_value()` function does not handle processor objects, causing serialization to fail.

The existing code already handles `torch.Tensor`, `numpy.ndarray`, dataclasses, and Hugging Face tokenizers via dedicated `Serialized*` Pydantic models, but has no equivalent for PIL images or HF processors.

Add serialization support for both types in `serialization.py`:
- PIL images should be serialized to PNG bytes encoded as base64, with a `"pil_image"` type marker. Deserialization should reconstruct the original PIL Image with the correct mode.
- HF processors should be serialized by archiving the output of `save_pretrained()` into a ZIP (with optional zstd compression for large payloads), base64-encoding it, and using a `"processor"` type marker. Deserialization should use `AutoProcessor.from_pretrained()` on the extracted archive.

Both types need to be wired into `serialize_value()` and `deserialize_value()`.
