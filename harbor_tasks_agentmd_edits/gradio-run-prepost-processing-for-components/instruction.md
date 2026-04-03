# Run Pre/Post Processing in a Separate Thread

## Problem

Gradio's component `preprocess()` and `postprocess()` methods (e.g., for image, audio, and video components) run synchronously on the async event loop. For apps that do heavy file I/O in these methods, this blocks the GIL and causes significant latency under concurrent load. At 100 concurrent users, latency can be 2-4x worse than a single user.

## Expected Behavior

Component `preprocess()` and `postprocess()` calls in `gradio/blocks.py` should be offloaded to a thread pool so they don't block the async event loop. The existing `self.limiter` on the `Blocks` class should be used to control thread pool capacity.

Additionally, the profiling infrastructure in `gradio/profiling.py` currently only supports async context managers (`trace_phase`). Synchronous equivalents are needed so that synchronous functions running in threads can also record profiling data. Specifically:

- A `trace_phase_sync` synchronous context manager (mirrors the existing async `trace_phase`)
- A `traced_sync` decorator for wrapping synchronous functions with timing
- A `traced` decorator for wrapping async functions with timing
- Granular timing fields on `RequestTrace` for sub-phases like file caching, image formatting, audio processing, video conversion, etc.

## Files to Look At

- `gradio/blocks.py` — `preprocess_data()` and `postprocess_data()` methods call `block.preprocess()` and `block.postprocess()` synchronously; these should be offloaded to threads
- `gradio/profiling.py` — profiling infrastructure; add synchronous tracing utilities and granular timing fields
- `scripts/benchmark/README.md` — after adding the new profiling capabilities and benchmark improvements, update the documentation to describe the results directory structure that benchmarks produce, including per-tier output organization
