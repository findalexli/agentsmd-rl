FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin ed003b4482aabdf8377250f22826dd31f378269c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Install minimal deps (no vision/torch extras) for import testing
RUN pip install --no-cache-dir -e ".[dev-sklearn]" 2>/dev/null || \
    pip install --no-cache-dir -e . && \
    pip install --no-cache-dir numpy huggingface_hub tokenizers safetensors

# Make sure Pillow is NOT installed (to reproduce the bug)
RUN pip uninstall -y Pillow pillow 2>/dev/null || true

# Configure git
RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

ENV PYTHONPATH=/repo/src