FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Configure git
RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test User"

# Clone repo at the base commit (before the fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin b7164eca8675e5223cf73fb430a6aaf6ceafc9cc && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Install core transformers only (no [testing] extras — avoids torch/tf timeout)
RUN pip install --no-cache-dir -e . 2>&1 | tail -5

ENV PYTHONPATH=/repo/src