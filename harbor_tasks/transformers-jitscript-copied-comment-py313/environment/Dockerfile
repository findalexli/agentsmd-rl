FROM python:3.13-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
RUN git init /workspace/huggingface__transformers && \
    cd /workspace/huggingface__transformers && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin 0e1978c9eb69ec64b55245212dbf63deab19d25b && \
    git checkout FETCH_HEAD

# Install minimal deps for testing (no torch — tests are source-level)
RUN pip install --no-cache-dir ruff pytest pytest-json-ctrf

ENV PYTHONPATH="/workspace/huggingface__transformers/src"
RUN mkdir -p /logs/verifier

WORKDIR /workspace/huggingface__transformers