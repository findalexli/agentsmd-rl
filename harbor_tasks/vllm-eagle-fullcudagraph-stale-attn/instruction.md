# Bug: Stale attention metadata in EAGLE speculative decoding FULL cudagraph path

## Context

In the EAGLE speculative decoding speculator (`vllm/v1/worker/gpu/spec_decode/eagle/speculator.py`), the `EagleSpeculator` class contains several methods that must all be preserved: `propose`, `generate_draft`, `capture_model`, `run_model`, `load_model`, and `set_attn`.

The `propose()` method handles draft token generation. After the initial prefill step, it dispatches a batch descriptor and then runs the draft decode steps using either FULL cudagraph, piecewise cudagraph, or eager mode. During execution, `propose()` accesses `self.input_buffers`, `self.block_tables`, and `self.draft_tokens`.

## Problem

When the batch descriptor's cudagraph mode is `CUDAGraphMode.FULL`, the code takes a shortcut that skips rebuilding the attention metadata before replaying the full cudagraph. This means the attention metadata builder state retains stale values from previous runs.

Slot mappings must also be computed within `propose()` for all cudagraph modes (via a method or function whose name contains `slot_mapping`).

The consequence is that draft tokens at positions > 0 (i.e., after the first draft token) have significantly lower acceptance rates compared to what they should be. The stale attention metadata causes the draft model to produce lower quality predictions at these positions.

## Expected behavior

- The attention metadata should be rebuilt before every draft decode execution, including when using the FULL cudagraph path.
- The `propose()` method must not contain an early return in the FULL cudagraph branch that bypasses attention metadata construction.
- The method must contain substantial logic (conditionals, function calls, attribute access to `self.input_buffers`, `self.block_tables`, and `self.draft_tokens`) — it must not be stubbed or simplified to the point of losing functionality.
- All six `EagleSpeculator` methods (`propose`, `generate_draft`, `capture_model`, `run_model`, `load_model`, `set_attn`) must remain present after the fix.

## Files to investigate

- `vllm/v1/worker/gpu/spec_decode/eagle/speculator.py` — the `EagleSpeculator` class's `propose()` method, specifically the control flow around the FULL cudagraph path vs. attention metadata rebuilding

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
- `mypy (Python type checker)`
- `typos (spell-check)`
