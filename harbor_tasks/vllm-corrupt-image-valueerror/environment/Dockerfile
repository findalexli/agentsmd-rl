FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone vllm at the base commit (before the fix)
# Use --filter=blob:none for a treeless clone — vllm is huge, this fetches
# only the blobs needed for the checked-out commit instead of all history.
RUN git init /testbed && \
    cd /testbed && \
    git remote add origin https://github.com/vllm-project/vllm.git && \
    git fetch --depth=1 origin 3683fe6c0651fe54a0201552ae7dfb7acb1e0cea && \
    git checkout FETCH_HEAD

# Install only the minimal deps needed for testing image loading
RUN pip install --no-cache-dir pillow pybase64 pytest pytest-json-ctrf

ENV PYTHONPATH=/testbed
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN mkdir -p /logs/verifier

WORKDIR /testbed