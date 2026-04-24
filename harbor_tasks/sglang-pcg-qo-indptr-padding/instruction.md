# Task: sglang-pcg-qo-indptr-padding

## Bug Summary

When piecewise CUDA graphs (PCG) are enabled with the FlashInfer attention backend,
the server crashes during the replay phase of the extend (prefill) path with:

```
ValueError: q.shape[0] does not match qo_indptr[-1]
```

## Files to Modify

All three files are under `/workspace/sglang/python/sglang/srt/`:

1. `layers/attention/flashinfer_backend.py`
2. `compilation/piecewise_context_manager.py`
3. `model_executor/piecewise_cuda_graph_runner.py`

## Expected API Surface (tests verify these)

### ForwardContext (`piecewise_context_manager.py`)

- `ForwardContext` must have a `num_tokens` attribute (type `Optional[int]`)
- `num_tokens` defaults to `None` when not set

### set_forward_context (`piecewise_context_manager.py`)

- `set_forward_context` must accept a `num_tokens` keyword argument (type `Optional[int]`, default `None`)
- When called with `num_tokens=N`, `get_forward_context().num_tokens` inside the block must equal `N`
- Different values (e.g., 42, 256) must propagate correctly; default `None` when not passed

### PiecewiseCudaGraphRunner.replay (`piecewise_cuda_graph_runner.py`)

- `replay` must pass a token count to `set_forward_context`
- `init_forward_metadata` must be called **inside** the `set_forward_context` with-block

### call_begin_forward (`flashinfer_backend.py`)

- Must use the forward context's token count to extend internal index buffers
- Must guard the extension logic with a conditional (non-zero padding tokens)

## Symptom Description

FlashInfer's prefill kernel validates that `q.shape[0] == qo_indptr[-1]`. During PCG
replay, the input tensors are padded to a static size (`static_num_tokens`) to fit the
captured CUDA graph, but `qo_indptr[-1]` reflects only the actual (unpadded) token
count. The fix must make `qo_indptr[-1]` account for the padding tokens while
preserving correct causal attention masks for real requests.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `typos (spell-check)`
