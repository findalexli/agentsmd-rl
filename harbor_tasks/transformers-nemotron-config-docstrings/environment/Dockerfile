FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

# Clone transformers at the base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/huggingface/transformers.git /workspace/transformers && \
    cd /workspace/transformers && \
    git checkout 8dc7a52d766efe76c121c0654a5d24d633bffe9e

# Install minimal deps for testing (no torch/GPU)
RUN cd /workspace/transformers && \
    pip install --no-cache-dir -e ".[quality]" 2>/dev/null || \
    pip install --no-cache-dir -e . && \
    pip install --no-cache-dir ruff pyyaml pytest pytest-json-ctrf

ENV PYTHONPATH=/workspace/transformers/src
RUN mkdir -p /logs/verifier

WORKDIR /workspace/transformers