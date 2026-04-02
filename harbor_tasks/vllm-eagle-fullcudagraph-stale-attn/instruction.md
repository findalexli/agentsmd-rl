# Bug: Stale attention metadata in EAGLE speculative decoding FULL cudagraph path

## Context

In the EAGLE speculative decoding speculator (`vllm/v1/worker/gpu/spec_decode/eagle/speculator.py`), the `propose()` method handles draft token generation. After the initial prefill step, it dispatches a batch descriptor and then runs the draft decode steps using either FULL cudagraph, piecewise cudagraph, or eager mode.

## Problem

When the batch descriptor's cudagraph mode is `CUDAGraphMode.FULL`, the code takes a shortcut that skips rebuilding the attention metadata before replaying the full cudagraph. This means the attention metadata builder state retains stale values from previous runs.

The consequence is that draft tokens at positions > 0 (i.e., after the first draft token) have significantly lower acceptance rates compared to what they should be. The stale attention metadata causes the draft model to produce lower quality predictions at these positions.

## Expected behavior

The attention metadata should be rebuilt before every draft decode execution, including when using the FULL cudagraph path. This ensures the attention metadata builder state is fresh and reflects the current batch, resulting in higher quality draft tokens and better speculative decoding acceptance rates.

## Files to investigate

- `vllm/v1/worker/gpu/spec_decode/eagle/speculator.py` — the `propose()` method, specifically the control flow around the FULL cudagraph early return vs. attention metadata rebuilding
