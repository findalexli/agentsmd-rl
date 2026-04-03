FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin e5ad3946209fb96db5e9965b3eb67d69cc3749e0 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Install transformers with base deps only (no torch/GPU)
RUN pip install --no-cache-dir -e .

RUN git config user.name "solver" && \
    git config user.email "solver@bench"

ENV PYTHONPATH=/repo/src