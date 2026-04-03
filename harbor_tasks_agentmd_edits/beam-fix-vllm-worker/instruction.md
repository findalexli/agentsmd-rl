# Fix vLLM text completion example for memory-constrained GPUs

## Problem

The `vllm_text_completion.py` example pipeline fails on GPUs with ~16 GiB of memory (e.g. NVIDIA T4). During vLLM engine startup, the default `max_num_seqs` and `gpu_memory_utilization` values cause CUDA out-of-memory errors:

```
torch.OutOfMemoryError: CUDA out of memory.
RuntimeError: CUDA out of memory occurred when warming up sampler with 256 dummy requests.
```

The example currently creates `VLLMCompletionsModelHandler` and `VLLMChatModelHandler` without passing any `vllm_server_kwargs`, so vLLM uses its built-in defaults which are too aggressive for smaller GPUs.

## Expected Behavior

The example should pass conservative memory-related vLLM server flags (`max-num-seqs`, `gpu-memory-utilization`) via the existing `vllm_server_kwargs` parameter, following the same pattern already used in other vLLM examples like `vllm_gemma_batch.py`. Users with larger GPUs should be able to override these defaults through CLI arguments.

The `run()` function should also accept an optional `vllm_server_kwargs` parameter for programmatic use (e.g. from tests or other scripts).

After fixing the code, update the relevant documentation to describe the new GPU memory settings and when they're needed.

## Files to Look At

- `sdks/python/apache_beam/examples/inference/vllm_text_completion.py` — the example pipeline that needs memory-aware vLLM server flags
- `sdks/python/apache_beam/ml/inference/vllm_inference.py` — the `VLLMCompletionsModelHandler` class that accepts `vllm_server_kwargs`
- `sdks/python/apache_beam/examples/inference/README.md` — documents the vLLM example usage
