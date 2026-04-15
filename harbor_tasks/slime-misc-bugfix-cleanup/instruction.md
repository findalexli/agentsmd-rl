# Fix bugs in checkpoint loading, data batching, and processor kwargs

## Bug Description

There are three bugs in the slime codebase that need to be fixed.

### 1. Checkpoint loading ignores caller-specified path

In `slime/backends/megatron_utils/checkpoint.py`, the function `_load_checkpoint_hf` accepts a parameter specifying the checkpoint path to load from. However, when calling `AutoBridge.from_hf_pretrained()`, it ignores this parameter and reads the checkpoint path from a global config attribute instead. This means the function does not respect the caller-specified path and may load the wrong checkpoint or fail when the global config points elsewhere.

### 2. Dead tracking metadata accumulated on batch

In `slime/backends/megatron_utils/data.py`, the `get_batch` function creates a dictionary that tracks per-sequence item counts for each multimodal key and attaches it to the batch. No downstream code ever reads this data — it is dead code that adds unnecessary complexity to the batch dictionary.

### 3. Missing processor flag causing downstream errors

In `slime/utils/processing_utils.py`, the `build_processor_kwargs` function does not configure the text processor to suppress `mm_token_type_ids` from its output. In newer versions of the Transformers library, the processor returns this field by default. Since it is not a tensor and is not used by Megatron, its presence causes errors when the batch is processed downstream.

## Files to Modify

- `slime/backends/megatron_utils/checkpoint.py`
- `slime/backends/megatron_utils/data.py`
- `slime/utils/processing_utils.py`
