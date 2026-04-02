When piecewise CUDA graphs are enabled with the FlashInfer attention backend, the server crashes during the replay phase of the extend (prefill) path with a shape mismatch error:

```
ValueError: q.shape[0] does not match qo_indptr[-1]
```

The root cause is in the extend metadata setup in `python/sglang/srt/layers/attention/flashinfer_backend.py`. During piecewise CUDA graph replay, the input tensors (e.g. `q`) are padded to a static size (`static_num_tokens`) to fit the captured graph, but `qo_indptr[-1]` only reflects the actual (unpadded) token count. FlashInfer's prefill kernel validates that `q.shape[0] == qo_indptr[-1]`, so the mismatch causes a crash.

The problem spans three files:

1. **`python/sglang/srt/layers/attention/flashinfer_backend.py`** — The `call_begin_forward` method in `FlashInferMultiStepDraftExtendMetadataHandler` (and the equivalent extend path) builds `qo_indptr` and `kv_indptr` based only on real requests, without accounting for the padding tokens that piecewise CUDA graphs add. The attention backend also doesn't know the static token count because it isn't propagated from the CUDA graph runner.

2. **`python/sglang/srt/compilation/piecewise_context_manager.py`** — `ForwardContext` and `set_forward_context` don't carry a static token count, so there's no way for the attention backend to learn how many tokens the CUDA graph expects.

3. **`python/sglang/srt/model_executor/piecewise_cuda_graph_runner.py`** — The `replay` method in `PiecewiseCudaGraphRunner` calls `init_forward_metadata` before entering `set_forward_context`, so the attention backend can't access the forward context when it needs to set up metadata.

Fix the shape mismatch so that `qo_indptr[-1]` equals `static_num_tokens` during piecewise CUDA graph replay, without corrupting the causal attention masks for real requests. The padding tokens' attention output will be discarded by the existing `[:raw_num_tokens]` slice in the replay path, so correctness of real requests must be preserved.
