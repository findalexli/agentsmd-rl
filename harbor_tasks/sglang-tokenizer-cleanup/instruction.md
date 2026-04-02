# TokenizerManager cleanup: dead code, validation layering, and trace priority

The `TokenizerManager` in `python/sglang/srt/managers/tokenizer_manager.py` has accumulated several issues that need attention:

## 1. Dead code in health check

The `health_generate` function in `python/sglang/srt/entrypoints/http_server.py` references `tokenizer_manager.is_image_gen`, but this attribute is always `False` — the image generation codepath is never reached. The dead branch (and the `is_image_gen` attribute on `TokenizerManager`) should be removed.

## 2. Unused state in TokenizerManager

`TokenizerManager` initializes `current_load` and `current_load_lock` in its `init_running_status()` method, but these are never used anywhere. They should be removed.

## 3. Request ID validation is in the wrong layer

The method that validates request ID uniqueness currently lives on `TokenizerManager._validate_rid()`. The **intra-batch** duplicate check (verifying that a batch request doesn't contain duplicate rids) is a property of the request itself and should be moved into the request classes (`BaseReq` in `io_struct.py`), called from `normalize_batch_and_arguments()`.

The remaining **in-flight** check (verifying that rids aren't already being processed) should stay on the tokenizer manager but can be simplified using set intersection instead of a loop.

## 4. Trace header priority

In `_req_stats_init()`, the code checks HTTP request headers before checking `obj.external_trace_header`. This is backwards — when a request comes from the gRPC server or Engine, there's no real HTTP request object but the trace context is explicitly passed via `obj.external_trace_header`. The explicit trace context should be checked first.

## 5. CPU monitor thread placement

The `start_cpu_monitor_thread("tokenizer")` call is in `__init__` guarded by `self.enable_metrics`, but it should be inside `init_metric_collector_watchdog()` alongside the other metric initialization code.
