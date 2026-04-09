# Isolate Spec V1 path in decode post-processing

## Problem

The current `process_batch_result_decode` method in the scheduler output processor handles multiple speculative decoding variants (non-spec, Spec V1, Spec V2) in a complex, interleaved manner. This creates several issues:

1. **Code coupling**: Spec V1 reasoning token tracking is done in post-processing, while everything else (output_ids, check_finished, grammar) lives in the verify phase of eagle_info.py and ngram_info.py.

2. **Hard to maintain**: The V1-specific code is mixed with V2 and non-spec paths, making it difficult to locate and delete when V1 is eventually deprecated.

3. **Inconsistent state**: Reasoning tokens for Spec V1 are tracked differently than other variants.

The code needs to be refactored to isolate V1-specific handling with an early-continue pattern, and move reasoning token tracking into the verify phase where it belongs.

## Expected Behavior

After the refactoring:
- Spec V1 should have a dedicated early-exit path in `process_batch_result_decode`
- A new helper function `_handle_finished_req` should be extracted to handle request cleanup logic
- Reasoning token tracking should happen in `eagle_info.py` and `ngram_info.py` verify methods
- `model_config.py` should declare the `think_end_id` field (previously dynamically patched)
- The scheduler should set `model_config.think_end_id` when the reasoning parser is enabled

## Files to Look At

- `python/sglang/srt/managers/scheduler_output_processor_mixin.py` — Main decode post-processing logic that needs refactoring
- `python/sglang/srt/speculative/eagle_info.py` — Eagle speculative decoding verify method
- `python/sglang/srt/speculative/ngram_info.py` — Ngram speculative decoding fill_requests method
- `python/sglang/srt/configs/model_config.py` — Model configuration, needs think_end_id field
- `python/sglang/srt/managers/scheduler.py` — Scheduler initialization, needs to set model_config.think_end_id

## Context

This is a code organization refactoring that prepares for eventual Spec V1 deprecation. The key insight is that V1 handles output_ids, check_finished, grammar, and reasoning tokens in its verify phase (inside eagle_info.py and ngram_info.py), so the post-processing in process_batch_result_decode should recognize this and avoid duplicate handling.

Look for patterns like `is_spec_v1`, `batch.spec_algorithm.is_none()`, and `batch.is_spec_v2` to understand the conditional branches.
