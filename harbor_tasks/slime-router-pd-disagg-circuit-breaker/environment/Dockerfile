FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

# Clone repo at base commit (BEFORE the fix) — shallow to avoid timeout
RUN git init /workspace/slime && \
    cd /workspace/slime && \
    git remote add origin https://github.com/THUDM/slime.git && \
    git fetch --depth=1 origin 183e525f60fcf435f82f273e9eb69702d3ce431a && \
    git checkout FETCH_HEAD

ENV PYTHONPATH=/workspace/slime
RUN mkdir -p /logs/verifier

WORKDIR /workspace/slime