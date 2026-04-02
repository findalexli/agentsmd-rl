# Flaky GPTQ Compile Correctness Test on ROCm

## Bug Description

The compile correctness test (`tests/compile/fullgraph/test_basic_correctness.py`) is flaky when running the GPTQ-quantized model test setting on ROCm (AMD GPUs). Identical compile configurations produce divergent outputs across separate server processes, even though they should be deterministic.

### Root Cause Area 1: Dummy Weight Initialization

In `vllm/model_executor/model_loader/weight_utils.py`, the `initialize_single_dummy_weight` function is responsible for initializing model parameters with deterministic dummy values. However, it only handles floating-point parameters. Integer parameters — such as the `int32` tensors used by GPTQ quantization (`qweight`, `qzeros`) — are not initialized at all. On ROCm, these parameters are allocated via `torch.empty()` and contain whatever garbage values happen to be in GPU memory. When multiple processes each get different uninitialized values, their outputs diverge.

### Root Cause Area 2: Test List Construction

In the same test file, the eager-backend section of `test_compile_correctness` has a list construction bug:

- For each compile mode, `all_args` gets one entry but `all_envs` gets **two** entries (there is a duplicate append call). This causes a length mismatch.
- After the loop, `all_args` is tripled (`all_args * 3`), creating 12 entries vs 8 environment entries. Python's `zip()` silently truncates to the shorter list, so some configurations run twice in separate processes while others are skipped entirely.

Additionally, the inductor-backend comparison section above the eager loop never populates `all_envs` during its inner loop, making `zip()` produce zero pairs. The inductor comparison is effectively dead code that never runs.

## Files to Fix

- `vllm/model_executor/model_loader/weight_utils.py` — `initialize_single_dummy_weight` function (~line 1345)
- `tests/compile/fullgraph/test_basic_correctness.py` — `test_compile_correctness` function (~line 100)
