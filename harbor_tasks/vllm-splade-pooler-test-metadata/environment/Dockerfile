FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone vllm at the base commit (BEFORE the fix)
ARG BASE_COMMIT=85c0950b1f647e0b0654fbf3e91a9757b8233752
RUN git init /testbed && \
    cd /testbed && \
    git remote add origin https://github.com/vllm-project/vllm.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /testbed

# Install torch CPU-only (smaller, no CUDA needed for this test)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install minimal vllm deps needed for the test imports
# PoolingMetadata requires: numpy, msgspec (for PoolingParams)
# SPLADESparsePooler requires: torch.nn (already from torch)
# vllm.config requires: transformers, pydantic, etc.
RUN pip install --no-cache-dir \
    numpy msgspec pydantic transformers tokenizers \
    pytest filelock packaging py-cpuinfo pillow \
    partial-json cloudpickle blake3 lark \
    prometheus-client psutil watchfiles compressed-tensors \
    depyf opentelemetry-api opentelemetry-sdk requests \
    typing_extensions importlib-metadata aiohttp

# Try to install vllm in editable mode (CPU-only, skip C extensions)
# This makes all vllm.* imports work
RUN VLLM_TARGET_DEVICE=cpu pip install --no-cache-dir -e . 2>/dev/null || \
    pip install --no-cache-dir -e . --no-build-isolation 2>/dev/null || \
    echo "vllm editable install failed; falling back to PYTHONPATH"

ENV PYTHONPATH=/testbed
RUN git config --global user.name "test" && \
    git config --global user.email "test@test.com"
