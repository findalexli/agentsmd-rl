FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at the base commit (BEFORE the fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin 28e1cc59ecf479ea674f2cc4b443a2969aae3a69 && \
    git checkout FETCH_HEAD

RUN pip install --no-cache-dir ruff

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Install minimal deps for config import (no torch needed)
RUN pip install --no-cache-dir -e ".[quality]" 2>&1 | tail -5

ENV PYTHONPATH=/repo/src