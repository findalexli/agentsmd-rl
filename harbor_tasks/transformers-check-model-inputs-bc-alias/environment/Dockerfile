FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

# Clone transformers at the base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/huggingface/transformers.git /workspace/transformers && \
    cd /workspace/transformers && \
    git checkout 2620c4ddd41afcc8d3b1d1134803bd418ffa45a7

RUN mkdir -p /logs/verifier

WORKDIR /workspace/transformers

# Install minimal deps for testing (no torch/GPU)
RUN pip install --no-cache-dir -e ".[quality]" 2>/dev/null || pip install --no-cache-dir -e . 2>/dev/null || true

ENV PYTHONPATH=/workspace/transformers/src