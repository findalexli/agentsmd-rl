#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotent: skip if already applied
if grep -q 'trace_phase_sync' gradio/profiling.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/gradio/blocks.py b/gradio/blocks.py
--- a/gradio/blocks.py
+++ b/gradio/blocks.py
@@ -1771,11 +1771,14 @@ async def preprocess_data(
                     inputs[i].get("value", None) if is_prop_input else inputs[i]
                 )

-                inputs_cached = await processing_utils.async_move_files_to_cache(
-                    value_to_process,
-                    block,
-                    check_in_upload_folder=not explicit_call,
-                )
+                from gradio.profiling import trace_phase
+
+                async with trace_phase("preprocess_move_to_cache"):
+                    inputs_cached = await processing_utils.async_move_files_to_cache(
+                        value_to_process,
+                        block,
+                        check_in_upload_folder=not explicit_call,
+                    )
                 if getattr(block, "data_model", None) and inputs_cached is not None:
                     data_model = cast(
                         Union[GradioModel, GradioRootModel], block.data_model
@@ -1793,7 +1796,9 @@ async def preprocess_data(
                 state._update_value_in_config(block._id, inputs_serialized)

                 if block_fn.preprocess:
-                    processed_value = block.preprocess(inputs_cached)
+                    processed_value = await anyio.to_thread.run_sync(
+                        block.preprocess, inputs_cached, limiter=self.limiter
+                    )
                 else:
                     processed_value = inputs_serialized

@@ -1855,6 +1860,8 @@ async def postprocess_data(
         predictions: list | dict,
         state: SessionState | None,
     ) -> list[Any]:
+        from gradio.profiling import trace_phase
+
         state = state or SessionState(self)
         if (
             isinstance(predictions, dict)
@@ -1943,33 +1950,36 @@ async def postprocess_data(
                         )
                     if block._id in state:
                         block = state[block._id]
-                    prediction_value = block.postprocess(prediction_value)
+                    prediction_value = await anyio.to_thread.run_sync(
+                        block.postprocess, prediction_value, limiter=self.limiter
+                    )
                     if isinstance(prediction_value, (GradioModel, GradioRootModel)):
                         prediction_value_serialized = prediction_value.model_dump()
                     else:
                         prediction_value_serialized = prediction_value
-                    prediction_value_serialized = (
-                        await processing_utils.async_move_files_to_cache(
-                            prediction_value_serialized,
-                            block,
-                            postprocess=True,
+                    async with trace_phase("postprocess_update_state_in_config"):
+                        prediction_value_serialized = (
+                            await processing_utils.async_move_files_to_cache(
+                                prediction_value_serialized,
+                                block,
+                                postprocess=True,
+                            )
+                        )
+                        if block._id not in state:
+                            state[block._id] = block
+                        state._update_value_in_config(
+                            block._id, prediction_value_serialized
                         )
-                    )
-                    if block._id not in state:
-                        state[block._id] = block
-                    state._update_value_in_config(
-                        block._id, prediction_value_serialized
-                    )
                 elif not block_fn.postprocess:
                     if block._id not in state:
                         state[block._id] = block
                     state._update_value_in_config(block._id, prediction_value)
-
-                outputs_cached = await processing_utils.async_move_files_to_cache(
-                    prediction_value,
-                    block,
-                    postprocess=True,
-                )
+                async with trace_phase("postprocess_move_to_cache"):
+                    outputs_cached = await processing_utils.async_move_files_to_cache(
+                        prediction_value,
+                        block,
+                        postprocess=True,
+                    )
                 output.append(outputs_cached)

         return output
diff --git a/gradio/profiling.py b/gradio/profiling.py
--- a/gradio/profiling.py
+++ b/gradio/profiling.py
@@ -4,8 +4,9 @@
 import os
 import time
 from collections import deque
-from contextlib import asynccontextmanager
+from contextlib import asynccontextmanager, contextmanager
 from dataclasses import dataclass, field
+from functools import wraps
 from typing import Any

 PROFILING_ENABLED = os.environ.get("GRADIO_PROFILING", "").strip() in ("1", "true")
@@ -25,6 +26,20 @@ class RequestTrace:
     streaming_diff_ms: float = 0.0
     total_ms: float = 0.0
     n_iterations: int = 0
+    upload_ms: float = 0.0
+    preprocess_move_to_cache_ms: float = 0.0
+    preprocess_format_image_ms: float = 0.0
+    postprocess_save_img_array_to_cache_ms: float = 0.0
+    preprocess_audio_from_file_ms: float = 0.0
+    postprocess_save_audio_to_cache_ms: float = 0.0
+    preprocess_video_ms: float = 0.0
+    postprocess_video_convert_video_to_playable_mp4_ms: float = 0.0
+    postprocess_update_state_in_config_ms: float = 0.0
+    postprocess_move_to_cache_ms: float = 0.0
+    postprocess_video_ms: float = 0.0
+    postprocess_save_pil_to_cache_ms: float = 0.0
+    postprocess_save_bytes_to_cache_ms: float = 0.0
+    save_file_to_cache_ms: float = 0.0

     def set_phase(self, name: str, duration_ms: float):
         attr = f"{name}_ms"
@@ -47,6 +62,19 @@ def to_dict(self) -> dict[str, Any]:
             "streaming_diff_ms": self.streaming_diff_ms,
             "total_ms": self.total_ms,
             "n_iterations": self.n_iterations,
+            "preprocess_move_to_cache_ms": self.preprocess_move_to_cache_ms,
+            "preprocess_format_image_ms": self.preprocess_format_image_ms,
+            "postprocess_save_img_array_to_cache_ms": self.postprocess_save_img_array_to_cache_ms,
+            "preprocess_audio_from_file_ms": self.preprocess_audio_from_file_ms,
+            "postprocess_save_audio_to_cache_ms": self.postprocess_save_audio_to_cache_ms,
+            "preprocess_video_ms": self.preprocess_video_ms,
+            "postprocess_video_convert_video_to_playable_mp4_ms": self.postprocess_video_convert_video_to_playable_mp4_ms,
+            "postprocess_update_state_in_config_ms": self.postprocess_update_state_in_config_ms,
+            "postprocess_move_to_cache_ms": self.postprocess_move_to_cache_ms,
+            "postprocess_video_ms": self.postprocess_video_ms,
+            "postprocess_save_pil_to_cache_ms": self.postprocess_save_pil_to_cache_ms,
+            "postprocess_save_bytes_to_cache_ms": self.postprocess_save_bytes_to_cache_ms,
+            "save_file_to_cache_ms": self.save_file_to_cache_ms,
         }


@@ -78,6 +106,51 @@ async def trace_phase(name: str):
         trace.set_phase(name, duration_ms)


+@contextmanager
+def trace_phase_sync(name: str):
+    """Context manager that records timing for a named phase into the current trace."""
+    trace = _current_trace.get()
+    if trace is None:
+        yield
+        return
+    start = time.monotonic()
+    try:
+        yield
+    finally:
+        duration_ms = (time.monotonic() - start) * 1000
+        trace.set_phase(name, duration_ms)
+
+
+def traced(phase):
+    if not PROFILING_ENABLED:
+        return lambda f: f
+
+    def _factory(f):
+        @wraps(f)
+        async def wrapper(*args, **kwargs):
+            async with trace_phase(phase):
+                return await f(*args, **kwargs)
+
+        return wrapper
+
+    return _factory
+
+
+def traced_sync(phase):
+    if not PROFILING_ENABLED:
+        return lambda f: f
+
+    def _factory(f):
+        @wraps(f)
+        def wrapper(*args, **kwargs):
+            with trace_phase_sync(phase):
+                return f(*args, **kwargs)
+
+        return wrapper
+
+    return _factory
+
+
 class TraceCollector:
     def __init__(self, maxlen: int = 100_000):
         self._traces: deque[RequestTrace] = deque(maxlen=maxlen)
@@ -134,3 +207,7 @@ def clear(self):
     @asynccontextmanager
     async def trace_phase(name: str):  # noqa: ARG001
         yield
+
+    @contextmanager
+    def trace_phase_sync(name: str):  # noqa: ARG001
+        yield
diff --git a/scripts/benchmark/README.md b/scripts/benchmark/README.md
--- a/scripts/benchmark/README.md
+++ b/scripts/benchmark/README.md
@@ -83,20 +83,46 @@ python scripts/benchmark/remote_runner.py ab \
     --hardware cpu-upgrade
 ```

-This submits two identical jobs (one per branch) to HF Jobs. Results are uploaded to a shared HF bucket path for easy comparison:
+This submits two identical jobs (one per branch) to HF Jobs. Results are uploaded to a shared HF bucket path for easy comparison. Use `--dry-run` to preview the generated bash script without submitting.
+
+### Results Directory Structure
+
+Each branch produces the following structure in the HF bucket:
+
+```
+hf://buckets/gradio/backend-benchmarks/{run_name}/{branch}/
+├── runner.py                          # Copy of the benchmark runner script (for reproducibility)
+├── run_params.json                    # Job parameters (branch, commit, apps, tiers, etc.)
+└── {app_stem}/                        # One directory per app (e.g. "echo_text")
+    └── {timestamp}/                   # e.g. "20260330_142500"
+        ├── summary.json               # Overall results: app name, timestamp, all tier results
+        ├── summary_table.txt          # Human-readable table (client/server p50/p90/p99, success%)
+        ├── tier_1/
+        │   ├── client_latencies.jsonl  # One JSON object per request (client-side timing)
+        │   └── traces.jsonl            # Server-side profiling traces
+        ├── tier_10/
+        │   ├── client_latencies.jsonl
+        │   └── traces.jsonl
+        └── tier_100/
+            ├── client_latencies.jsonl
+            └── traces.jsonl
+```
+
+For A/B tests, both branches share the same `{run_name}` prefix:

 ```
 hf://buckets/gradio/backend-benchmarks/{run_name}/
-  main/
-    run_params.json
-    runner.py              # exact runner script used
-    echo_text/summary.json
-    streaming_chat/...
-  avoid-asyncio-sleep-sse/
-    ...
+├── main/
+│   ├── runner.py
+│   ├── run_params.json
+│   └── {app_stem}/{timestamp}/...
+└── {compare_branch}/
+    ├── runner.py
+    ├── run_params.json
+    └── {app_stem}/{timestamp}/...
 ```

-Use `--dry-run` to preview the generated bash script without submitting.
+The `tier_{N}` directories are created for each value in `--tiers` (default `1,10,100`), and each app passed via `--apps` gets its own `{app_stem}/` directory.

 ### Remote Runner Options


PATCH

echo "Patch applied successfully."
