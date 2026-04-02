FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone transformers at the base commit (before the fix)
RUN git clone https://github.com/huggingface/transformers.git /workspace/transformers && \
    cd /workspace/transformers && \
    git checkout a269c990e8571d9b9f8adfc1add9472eec3f252d && \
    git config user.email "agent@test.com" && \
    git config user.name "Agent"

# Install minimal deps for testing (no torch/GPU needed)
RUN cd /workspace/transformers && \
    pip install --no-cache-dir -e ".[quality]" 2>/dev/null || \
    pip install --no-cache-dir -e . && \
    pip install --no-cache-dir pyyaml pytest pytest-json-ctrf

ENV PYTHONPATH=/workspace/transformers/src
RUN pip install --no-cache-dir ruff

RUN mkdir -p /logs/verifier

WORKDIR /workspace/transformers