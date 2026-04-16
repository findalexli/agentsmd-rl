# Cache sub-objects in __getitem__ to ensure identity stability

## Problem

The `GenerateReqInput` and `EmbeddingReqInput` classes in `python/sglang/srt/managers/io_struct.py` implement `__getitem__` to return sub-objects for batched requests. However, each call to `obj[i]` returns a NEW instance, which can cause subtle bugs where different call sites get divergent objects that fall out of sync.

For example, if code modifies one reference to `obj[0]`, other code holding a different reference to `obj[0]` won't see the change because they're different objects.

A specific case occurs in the LoRA path resolution: when `_resolve_lora_path` assigns `lora_id` to the parent object, cached sub-objects created by prior `__getitem__` calls don't receive the update because they're separate instances.

## Expected Behavior

1. Repeated calls to `req[i]` should return the **same object instance** (identity check: `req[0] is req[0]` should be True)
2. The cache should be stored in a way that survives across multiple accesses
3. When `lora_id` is assigned after sub-objects have been accessed, those cached sub-objects should reflect the update

## Implementation Requirements

To fix the identity instability:

1. In `GenerateReqInput.__getitem__` and `EmbeddingReqInput.__getitem__`, use a cache stored as `_sub_obj_cache` on the instance
2. Initialize the cache using `setdefault` on the instance's `__dict__`
3. Check the cache for existing sub-objects before creating new ones
4. Store newly created sub-objects in `cache[i]` before returning them
5. In `_resolve_lora_path`, propagate `lora_id` to any cached sub-objects by iterating over `_sub_obj_cache`

## Files to Look At

- `python/sglang/srt/managers/io_struct.py` — Contains `GenerateReqInput` and `EmbeddingReqInput` classes with `__getitem__` methods
- `python/sglang/srt/managers/tokenizer_manager.py` — The `_resolve_lora_path` method
