FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin a9532bcf887b364bfedcc33a13be2b1d1acbef85 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Install CPU-only torch (needed by continuous_batching modules at import time)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install transformers with base deps + ruff
RUN pip install --no-cache-dir -e . && \
    pip install --no-cache-dir ruff

RUN git config user.name "solver" && \
    git config user.email "solver@bench"

ENV PYTHONPATH=/repo/src