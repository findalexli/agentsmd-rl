FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone vllm at base commit (before the fix) — blobless clone for speed
RUN git clone --filter=blob:none https://github.com/vllm-project/vllm.git /workspace/vllm \
    && cd /workspace/vllm \
    && git checkout 7b54f60db0f55d74dac8aa3040c02363b7a9f6ec \
    && git config user.email "agent@test.com" \
    && git config user.name "Agent"

# No torch/GPU deps needed — tests use AST and code extraction

ENV PYTHONPATH="/workspace/vllm"
RUN mkdir -p /logs/verifier

WORKDIR /workspace/vllm