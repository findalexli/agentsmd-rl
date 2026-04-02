FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
ARG BASE_COMMIT=44686173b26bb174f3c7eb6e59f08a338d1adf54
RUN git clone --filter=blob:none https://github.com/huggingface/transformers.git /workspace/transformers && \
    cd /workspace/transformers && \
    git checkout ${BASE_COMMIT}

# Install minimal deps needed for testing (no torch/GPU)
RUN cd /workspace/transformers && \
    pip install --no-cache-dir ruff

# Configure git
RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

ENV PYTHONPATH=/workspace/transformers
RUN mkdir -p /logs/verifier

WORKDIR /workspace/transformers