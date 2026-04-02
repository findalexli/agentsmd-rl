# Redundant Device Copies for Pooling Token IDs

## Problem

When running pooling models (e.g., embedding, reranking), the `PoolingMetadata` object only provides token IDs on the model device (GPU). However, several pooler implementations — such as `BertForSequenceClassificationWithMultiVector` in `vllm/model_executor/models/bert.py`, the special pooler in `vllm/model_executor/layers/pooler/special.py`, and the GritLM pooler in `vllm/model_executor/models/gritlm.py` — only need token IDs on the CPU to make per-sequence trimming decisions (e.g., stripping BOS/EOS tokens).

Currently, the code path in `vllm/v1/worker/gpu_input_batch.py` builds a CPU tensor of prompt token IDs and then immediately transfers it to the GPU device. Downstream poolers that need CPU access must then transfer the data back to CPU (e.g., calling `.cpu()` or `.item()`), resulting in a wasteful CPU → GPU → CPU round-trip for every batch.

This round-trip is especially costly for embedding/reranking workloads where the pooling step dominates, causing significant throughput degradation.

## Expected Behavior

Pooler implementations that only need CPU-resident token IDs should be able to access them directly without incurring a device transfer. The GPU-resident copy should only be created when actually needed for device-side operations (e.g., penalty computation during sampling).

## Relevant Files

- `vllm/v1/pool/metadata.py` — `PoolingMetadata` dataclass that holds token ID tensors
- `vllm/v1/worker/gpu_input_batch.py` — `InputBatch` class, specifically the method that builds the prompt token ID tensor and the `get_pooling_metadata()` method
- `vllm/model_executor/layers/pooler/special.py` — `SpecialTokenStripPooler.forward()` accesses token IDs
- `vllm/model_executor/models/bert.py` — `BertForSequenceClassificationWithMultiVector.forward()` accesses token IDs
- `vllm/model_executor/models/gritlm.py` — `GritLMPooler.forward()` accesses token IDs
- `vllm/v1/worker/gpu_model_runner.py` — constructs dummy `PoolingMetadata` for profiling
