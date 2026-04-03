FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
ARG BASE_COMMIT=8a6f4ef3bfe644c7fd1e33841aa66c6f3a4c26a4
RUN git init /workspace/prime-rl && \
    cd /workspace/prime-rl && \
    git remote add origin https://github.com/PrimeIntellect-ai/prime-rl.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/prime-rl

# Install only transformers (needed for NemotronHConfig and model code) - no torch/GPU deps
RUN pip install --no-cache-dir transformers pydantic

ENV PYTHONPATH=/workspace/prime-rl/src