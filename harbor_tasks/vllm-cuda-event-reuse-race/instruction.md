# Fix CUDA Event Reuse Race in Model Runner V2

## Problem

In vLLM's Model Runner V2, the async output path for D→H (device-to-host) copies uses a CUDA event to signal completion. Currently, a single `torch.cuda.Event` is created once and reused across successive steps. This causes a race condition: recording the event for step N+1 before the position recorded by step N has been reached means the thread waiting for step N's results won't unblock until step N+1's results are ready, adding unnecessary latency.

## Expected Behavior

Each async output (both for decoding and pooling) should have its own independent CUDA event, so that synchronization for one step cannot be delayed by event reuse from a subsequent step.

## Files to Look At

- `vllm/v1/worker/gpu/async_utils.py` — Contains `AsyncOutput` and `AsyncPoolingOutput` classes that handle async D→H copy and synchronization via CUDA events
- `vllm/v1/worker/gpu/model_runner.py` — `GPUModelRunner` creates and manages the shared event, passing it to async output constructors
