#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotent: skip if already applied
if grep -q 'def trace_phase_sync' gradio/profiling.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/gradio/profiling.py b/gradio/profiling.py
index 2c9782592f..c50580ace3 100644
--- a/gradio/profiling.py
+++ b/gradio/profiling.py
@@ -4,8 +4,9 @@ import contextvars
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
@@ -47,6 +62,19 @@ class RequestTrace:
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
@@ -134,3 +207,7 @@ if not PROFILING_ENABLED:
     @asynccontextmanager
     async def trace_phase(name: str):  # noqa: ARG001
         yield
+
+    @contextmanager
+    def trace_phase_sync(name: str):  # noqa: ARG001
+        yield
diff --git a/scripts/benchmark/README.md b/scripts/benchmark/README.md
index 441d4b5c25..9c05f8c5ff 100644
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
