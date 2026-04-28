# Fix vLLM text completion example for memory-constrained GPUs

## Problem

The `vllm_text_completion.py` example pipeline fails on GPUs with ~16 GiB of memory (e.g. NVIDIA T4). During vLLM engine startup, the default `max_num_seqs` and `gpu_memory_utilization` values cause CUDA out-of-memory errors:

```
torch.OutOfMemoryError: CUDA out of memory.
RuntimeError: CUDA out of memory occurred when warming up sampler with 256 dummy requests.
```

The example currently creates `VLLMCompletionsModelHandler` and `VLLMChatModelHandler` without passing any `vllm_server_kwargs`, so vLLM uses its built-in defaults which are too aggressive for smaller GPUs.

## What to do

1. **Add CLI arguments** to `parse_known_args()` in `vllm_text_completion.py` so users can control vLLM's memory-related server flags from the command line:
   - `--vllm_max_num_seqs` (int, default 32) — passed to the vLLM server as `--max-num-seqs`
   - `--vllm_gpu_memory_utilization` (float, default 0.72) — passed to the vLLM server as `--gpu-memory-utilization`

2. **Add a helper function** `build_vllm_server_kwargs(known_args)` that returns a dict mapping server flag names to their values. The dict must use the exact keys `max-num-seqs` and `gpu-memory-utilization`, with string values (since these are CLI flags passed to the vLLM server).

3. **Wire the defaults into `run()`**: the `VLLMCompletionsModelHandler` and `VLLMChatModelHandler` must receive the memory-conservative server kwargs by default. The `run()` function should also accept an optional `vllm_server_kwargs` parameter for programmatic use (e.g. from tests or other scripts).

4. **Update the README** at `sdks/python/apache_beam/examples/inference/README.md` to document these new CLI flags and explain GPU memory constraints (~16 GiB, CUDA OOM).

## Files to look at

- `sdks/python/apache_beam/examples/inference/vllm_text_completion.py` — the example pipeline to modify
- `sdks/python/apache_beam/examples/inference/README.md` — documentation to update
- `sdks/python/apache_beam/ml/inference/vllm_inference.py` — `VLLMCompletionsModelHandler` accepts `vllm_server_kwargs`; no changes needed here

## References

- Other vLLM examples (e.g. `vllm_gemma_batch.py`) already pass server kwargs via `vllm_server_kwargs` — follow the same pattern
- vLLM server CLI flags: `--max-num-seqs` and `--gpu-memory-utilization` (see [vLLM docs](https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html))

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `flake8` (Python syntax/error checker)
- `pycodestyle` (PEP 8 style guide checker)
- `yapf` (Python code formatter)
- `pylint` (Python static analysis linter)
