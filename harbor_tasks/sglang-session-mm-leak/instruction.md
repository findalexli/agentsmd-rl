# Multimodal features leak when sessions close

## Problem

In `python/sglang/srt/managers/session_controller.py`, when a session is closed via `SessionController._close()`, multimodal feature tensors held by requests in that session are never released. This causes a GPU memory leak.

The normal request lifecycle releases multimodal features in two places:
- `Scheduler._maybe_clear_mm_inputs()` skips session requests (they need features for continuation)
- `SchedulerOutputProcessorMixin.process_batch_result_decode()` also skips session requests

But when the session finally closes, nothing frees those features. They stay alive on the GPU until the process exits.

Additionally, the inline cleanup pattern for releasing features (iterating `mm_items` and setting `feature = None`) is duplicated in both `scheduler.py` and `scheduler_output_processor_mixin.py`. This should be unified into a method on the `MultimodalInputs` class.

## Secondary issue

In `session_controller.py`, the `Session.create_req()` method adjusts multimodal item offsets when stripping the BOS token from appended requests. The adjustment `(s - 1, e - 1)` can produce negative offsets when `s` is already 0 (i.e., the item is at the BOS position). This edge case should be handled defensively.

## Where to look

- `python/sglang/srt/managers/schedule_batch.py` — `MultimodalInputs` class (around line 360)
- `python/sglang/srt/managers/session_controller.py` — `SessionController._close()` method and `Session.create_req()` BOS offset logic
- `python/sglang/srt/managers/scheduler.py` — `_maybe_clear_mm_inputs()` (around line 1674)
- `python/sglang/srt/managers/scheduler_output_processor_mixin.py` — `process_batch_result_decode()` (around line 438)

## Expected behavior

- When a session closes, all multimodal feature tensors held by its requests are released
- The feature release logic should be a reusable method, not copy-pasted inline code
- Offset adjustments should not produce negative values when the start offset is already 0
