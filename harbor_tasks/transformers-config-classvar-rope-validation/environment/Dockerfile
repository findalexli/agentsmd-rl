FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
ARG BASE_COMMIT=eb3d67aaafe368863afc77e4b60fa60c2077c8b5
RUN git init /workspace/transformers && \
    cd /workspace/transformers && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/transformers

# Install minimal deps for testing (no torch/GPU)
RUN pip install --no-cache-dir -e ".[quality]" pyyaml 2>/dev/null || \
    pip install --no-cache-dir -e . pyyaml

ENV PYTHONPATH="/workspace/transformers/src"
