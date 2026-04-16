# Fix CUDA Event Reuse Race in Model Runner V2

## Problem

In vLLM's Model Runner V2, the async output path for D→H (device-to-host) copies uses a CUDA event to signal completion. A race condition exists where a CUDA event is shared across successive inference steps: when step N+1 records into the same event before step N's synchronization has completed, the thread waiting for step N's results won't unblock until step N+1's results are ready. This adds unnecessary latency to step N's completion.

The relevant code is in the async output handling classes that manage D→H copy and synchronization, and the model runner class that orchestrates per-step execution.

## Expected Behavior

Each async output (both for decoding and pooling) should have its own independent CUDA event, so that synchronization for one step cannot be delayed by event reuse from a subsequent step. Specifically:

- The async output class for decoding must not receive a shared event from its caller; it should create its own event internally
- The async output class for pooling must not receive a shared event from its caller; it should create its own event internally
- The model runner class must not maintain a shared event attribute for output copying

## Files to Look At

- `vllm/v1/worker/gpu/async_utils.py` — Contains async output classes that handle async D→H copy and synchronization via CUDA events
- `vllm/v1/worker/gpu/model_runner.py` — Contains the GPUModelRunner class that manages per-step execution
