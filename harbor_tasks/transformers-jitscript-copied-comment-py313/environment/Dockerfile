FROM python:3.13-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
RUN git clone --filter=blob:none --single-branch https://github.com/huggingface/transformers.git /workspace/huggingface__transformers && \
    cd /workspace/huggingface__transformers && \
    git checkout 0e1978c9eb69ec64b55245212dbf63deab19d25b && \
    git config user.email "agent@test.com" && \
    git config user.name "Agent"

# Install minimal deps for testing (no torch — tests are source-level)
RUN pip install --no-cache-dir ruff pytest pytest-json-ctrf

ENV PYTHONPATH="/workspace/huggingface__transformers/src"
RUN mkdir -p /logs/verifier

WORKDIR /workspace/huggingface__transformers