# Fix CUDA Event Reuse Race in Model Runner V2

## Problem

In vLLM's Model Runner V2, the async output path for D→H (device-to-host) copies uses a CUDA event to signal completion. Currently, a single `torch.cuda.Event` is created once in `GPUModelRunner.__init__` and stored as `self.output_copy_event`, then passed as the `copy_event` parameter to `AsyncOutput.__init__` and `AsyncPoolingOutput.__init__`. This shared event is reused across successive steps, which causes a race condition: recording the event for step N+1 before the position recorded by step N has been reached means the thread waiting for step N's results won't unblock until step N+1's results are ready, adding unnecessary latency.

## Expected Behavior

Each async output (both for decoding and pooling) should have its own independent CUDA event, so that synchronization for one step cannot be delayed by event reuse from a subsequent step. Concretely:

- `AsyncOutput` must not accept a `copy_event` parameter; it must create its own `torch.cuda.Event()` internally in `__init__`
- `AsyncPoolingOutput` must not accept a `copy_event` parameter; it must create its own `torch.cuda.Event()` internally in `__init__`
- `GPUModelRunner` must not store `self.output_copy_event`

## Files to Look At

- `vllm/v1/worker/gpu/async_utils.py` — Contains `AsyncOutput` and `AsyncPoolingOutput` classes that handle async D→H copy and synchronization via CUDA events
- `vllm/v1/worker/gpu/model_runner.py` — `GPUModelRunner` class manages per-step execution and creates the shared `output_copy_event` attribute
