# Bug: ShmPointerMMData breaks on multiple pickle round-trips and unwraps too early

## Context

SGLang's multimodal pipeline uses `ShmPointerMMData` (in `python/sglang/srt/managers/mm_utils.py`) to wrap tensor data as shared-memory pointers for efficient cross-process communication. The class is pickled/unpickled when sent between the tokenizer manager and the scheduler via ZMQ.

## Problem 1: Multiple pickle round-trips create duplicate shared memory

In multi-GPU (tensor-parallel) setups, requests received by the scheduler are broadcast to other ranks via `dist.broadcast_pyobj`. This means `ShmPointerMMData` objects get pickled a second time after being unpickled from ZMQ.

The current `__getstate__` implementation has a fallback path: if the `shm` attribute is `None` (which happens after `__setstate__`), it re-creates a brand new shared memory segment from the stored tensor. This means every pickle round-trip allocates a new shared memory block and copies all the tensor data again, leaking the previous segments and adding significant latency that scales with image count.

The fix should make `ShmPointerMMData` safely survive multiple pickle/unpickle cycles without re-creating shared memory — the `shm_name` should be the stable identifier that persists across serialization.

## Problem 2: Shared memory unwrapped before broadcast

In `python/sglang/srt/managers/scheduler.py`, the `recv_requests` method calls `unwrap_shm_features()` immediately after receiving each request from ZMQ — *before* the request is broadcast to other TP ranks. This means the full tensor data (not just the lightweight shm pointer metadata) gets serialized during `broadcast_pyobj`, defeating the purpose of shared memory transport.

The unwrap should be deferred to after all broadcasts complete, so only the compact shm metadata travels over the broadcast channel.

## Problem 3: unwrap_shm_features doesn't handle batch requests

The `unwrap_shm_features` function only handles single requests with `mm_inputs`. It does not recurse into batch request objects that contain a `.batch` list of sub-requests, leaving their `ShmPointerMMData` wrappers in place.

## Files to investigate

- `python/sglang/srt/managers/mm_utils.py` — `ShmPointerMMData` class and `unwrap_shm_features` function
- `python/sglang/srt/managers/scheduler.py` — `recv_requests` method where unwrap is called
