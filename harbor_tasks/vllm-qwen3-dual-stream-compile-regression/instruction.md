# Qwen3 / Qwen3.5 Cold Compile Time Regression

## Problem

After a recent change to the Qwen3 and Qwen3.5 model implementations, cold compile times have regressed by approximately **4x**. The root cause is the use of a custom op for input projection in the GDN attention layers. This custom op passes a `layer_name` string argument, which interacts badly with `torch.compile` — each unique string causes a separate compilation trace, dramatically inflating startup time.

## Affected Files

- `vllm/model_executor/models/qwen3_next.py` — The `Qwen3NextGatedDeltaNet` class uses a custom op (`gdn_in_proj`) for the input projection that orchestrates dual-stream CUDA execution. The custom op, its fake implementation, and its registration are all in this file.
- `vllm/model_executor/models/qwen3_5.py` — The `Qwen3_5GatedDeltaNet` class similarly calls the same custom op in its `forward` method.

## Expected Behavior

Input projection in both models should use direct linear layer calls rather than routing through a custom op that forces recompilation. The dual-stream execution optimization needs to be disabled until the underlying `torch.compile` compatibility issue is resolved.

## Hints

- Look at how the `forward` method performs input projection — it should call the linear layers directly
- The `Qwen3NextGatedDeltaNet.__init__` sets up CUDA stream/event infrastructure that is no longer needed
- There is a helper method and supporting functions (including a fake implementation for `torch.compile`) that should be removed
- Unused imports should be cleaned up
