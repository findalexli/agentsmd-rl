# Add synchronous profiling utilities to gradio/profiling.py

## Problem

The Gradio profiling module (`gradio/profiling.py`) currently only has an async context manager `trace_phase` for recording per-phase timing of requests. However, many component pre/post processing functions are synchronous — they run in threads via `anyio.to_thread.run_sync()`. There is no way to instrument these synchronous code paths with the existing async-only profiling API.

Additionally, the `RequestTrace` dataclass only tracks high-level phases (queue_wait, preprocess, fn_call, postprocess, streaming_diff, total). There's no granularity for individual component operations like image format conversion, audio file loading, video transcoding, file cache writes, or upload timing.

## Expected Behavior

1. **Synchronous profiling context manager**: A `trace_phase_sync` function (synchronous counterpart of `trace_phase`) that records timing for a named phase into the current `RequestTrace`. It should behave identically to `trace_phase` but work in sync code. When no trace is active, it should be a no-op.

2. **Profiling decorators**: `traced` (async) and `traced_sync` (sync) decorators that wrap functions to automatically record their execution time under a named phase. When profiling is disabled (`PROFILING_ENABLED` is False), these should return the original function unmodified for zero overhead.

3. **Component-level phase fields**: `RequestTrace` needs additional fields for granular timing of component operations: upload, cache moves, image/audio/video pre/post processing, etc. These fields must also appear in `to_dict()`.

4. **No-op fallback**: When `GRADIO_PROFILING` is not set, `trace_phase_sync` should have a no-op replacement (matching the existing pattern for `trace_phase`).

## Files to Look At

- `gradio/profiling.py` — The profiling module where all changes go. Study the existing `trace_phase` async context manager and `RequestTrace` dataclass.
- `scripts/benchmark/README.md` — The benchmark documentation should be updated to document the results directory structure produced by benchmark runs, including per-tier output files and A/B test layouts. This helps users understand where profiling data ends up.
