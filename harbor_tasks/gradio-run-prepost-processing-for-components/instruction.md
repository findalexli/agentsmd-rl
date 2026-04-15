# Add synchronous profiling utilities to gradio/profiling.py

## Problem

The Gradio profiling module (`gradio/profiling.py`) currently only has an async context manager `trace_phase` for recording per-phase timing of requests. However, many component pre/post processing functions are synchronous — they run in threads via `anyio.to_thread.run_sync()`. There is no way to instrument these synchronous code paths with the existing async-only profiling API.

Additionally, the `RequestTrace` dataclass only tracks high-level phases (queue_wait, preprocess, fn_call, postprocess, streaming_diff, total). There's no granularity for individual component operations like image format conversion, audio file loading, video transcoding, file cache writes, or upload timing.

## Expected Behavior

1. **Synchronous profiling context manager**: A `trace_phase_sync` function (synchronous counterpart of `trace_phase`) that records timing for a named phase into the current `RequestTrace`. It should behave identically to `trace_phase` but work in sync code. When no trace is active, it should be a no-op.

2. **Profiling decorators**: `traced` (async) and `traced_sync` (sync) decorators that wrap functions to automatically record their execution time under a named phase. When profiling is disabled (`PROFILING_ENABLED` is False), these should return the original function unmodified for zero overhead.

3. **Component-level phase fields**: `RequestTrace` needs additional fields for granular timing of component operations. Add these fields (all defaulting to `0.0`):
   - Upload: `upload_ms`
   - Cache operations: `preprocess_move_to_cache_ms`, `postprocess_move_to_cache_ms`, `save_file_to_cache_ms`
   - Image processing: `preprocess_format_image_ms`, `postprocess_save_pil_to_cache_ms`, `postprocess_save_bytes_to_cache_ms`, `postprocess_save_img_array_to_cache_ms`
   - Audio processing: `preprocess_audio_from_file_ms`, `postprocess_save_audio_to_cache_ms`
   - Video processing: `preprocess_video_ms`, `postprocess_video_ms`, `postprocess_video_convert_video_to_playable_mp4_ms`
   - State management: `postprocess_update_state_in_config_ms`

   All of these fields must also appear as keys in `to_dict()` output.

4. **No-op fallback**: When `GRADIO_PROFILING` is not set, `trace_phase_sync` should have a no-op replacement (matching the existing pattern for `trace_phase`).

## Files to Look At

- `gradio/profiling.py` — The profiling module where all changes go. Study the existing `trace_phase` async context manager and `RequestTrace` dataclass.
- `scripts/benchmark/README.md` — The benchmark documentation should be updated to document the results directory structure. Add a "Results Directory Structure" section that documents:
  - The tier subdirectories: `tier_1`, `tier_10`, `tier_100`
  - The output files: `client_latencies.jsonl` and `traces.jsonl`
  - The A/B test directory layout using placeholders like `{compare_branch}`, `{app_stem}`, and `tier_{N}`
