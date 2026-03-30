# Fix: renderer_num_workers > 1 with multimodal processor cache causes race conditions

## Problem

Using `--renderer-num-workers > 1` causes race conditions on the multimodal processor cache, leading to crashes or data corruption. Neither the LRU nor SHM multimodal processor cache is thread-safe. The renderer's `ThreadPoolExecutor` dispatches multimodal preprocessing to multiple threads, which concurrently read/write the cache without synchronization.

The SHM cache uses a `SingleWriterShmRingBuffer` that assumes a single writer, and the LRU cache is backed by `cachetools.LRUCache` which provides no thread-safety guarantees.

## Expected Behavior

Add a config-time validation in `ModelConfig.__post_init__` that raises `ValueError` when `--renderer-num-workers > 1` is used with the cache enabled (`--mm-processor-cache-gb > 0`), directing users to either keep the default single worker or disable the cache.

## File to Modify

- `vllm/config/model.py` -- add validation in `__post_init__`
