# Continuous Batching CUDA Graph Capture Crashes Under Multi-Threaded Use

## Bug Description

When running continuous batching inference with multiple threads — each thread managing its own model instance on a separate device — the CUDA graph capture step crashes with graph errors. The threads interfere with each other during `torch.cuda.graph()` capture even though they operate on independent model instances and streams.

The issue is in `src/transformers/generation/continuous_batching/continuous_api.py`, in the `_generation_step` method. When the code path enters CUDA graph creation (the `else` branch where a new graph is captured), the graph capture call does not account for the possibility of concurrent captures from other threads in the same process.

## Reproduction

1. Load two separate instances of the same model (e.g., Llama) in a single process.
2. Launch two threads, each running continuous batching generation on its own model instance.
3. Both threads will attempt to capture CUDA graphs around the same time.
4. The capture fails with PyTorch CUDA graph errors because the default capture mode does not isolate per-thread graph operations.

## Expected Behavior

Each thread should be able to independently capture and replay CUDA graphs without interfering with other threads' captures. The graph capture needs to operate in a mode that is safe for concurrent multi-threaded use.

## Relevant Code

- `src/transformers/generation/continuous_batching/continuous_api.py` — look at `_generation_step`, specifically where `torch.cuda.CUDAGraph()` is created and `torch.cuda.graph(...)` is called.
