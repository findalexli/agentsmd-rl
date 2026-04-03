FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone sglang at the base commit (before the fix)
RUN git init /workspace/sglang && \
    cd /workspace/sglang && \
    git remote add origin https://github.com/sgl-project/sglang.git && \
    git fetch --depth=1 origin fc9de157f9ea51e93dc58b8abacd688b5d5474b7 && \
    git checkout FETCH_HEAD

RUN pip install --no-cache-dir pybase64

RUN mkdir -p /logs/verifier

WORKDIR /workspace/sglang

# Install minimal deps for testing (no torch/GPU — tests use AST + subprocess)
# We need torch for the behavioral tests that exercise ShmPointerMMData
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir numpy pytest pytest-json-ctrf

ENV PYTHONPATH="/workspace/sglang/python:${PYTHONPATH}"