FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
ARG BASE_COMMIT=882ffdbbd6b8ad50feaa860d702e70950cfc95d0
RUN git init /workspace/transformers && \
    cd /workspace/transformers && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

# Install minimal deps needed for testing (no torch/GPU)
RUN cd /workspace/transformers && \
    pip install --no-cache-dir pyyaml gitpython requests

# Configure git
RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

ENV PYTHONPATH=/workspace/transformers
RUN mkdir -p /logs/verifier

WORKDIR /workspace/transformers

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
