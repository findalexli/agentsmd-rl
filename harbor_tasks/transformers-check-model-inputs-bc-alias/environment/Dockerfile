FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

# Clone transformers at the base commit (before the fix)
RUN git init /workspace/transformers && \
    cd /workspace/transformers && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin 2620c4ddd41afcc8d3b1d1134803bd418ffa45a7 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/transformers

# Install minimal deps for testing (no torch/GPU)
RUN pip install --no-cache-dir -e ".[quality]" 2>/dev/null || pip install --no-cache-dir -e . 2>/dev/null || true

ENV PYTHONPATH=/workspace/transformers/src