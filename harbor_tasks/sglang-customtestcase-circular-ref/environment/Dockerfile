FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone sglang at the base commit (before the fix)
RUN git init /workspace/sglang && \
    cd /workspace/sglang && \
    git remote add origin https://github.com/sgl-project/sglang.git && \
    git fetch --depth=1 origin afb32d76224e39d1226273d4a4a7fc568bd36b8c && \
    git checkout FETCH_HEAD

# Install minimal deps — only what test.sh needs (dill for serialization test)
RUN cd /workspace/sglang && pip install --no-cache-dir dill

# Configure git user for potential patch application
RUN cd /workspace/sglang && git config user.email "test@test.com" && git config user.name "Test"

ENV PYTHONPATH="/workspace/sglang/python"
RUN mkdir -p /logs/verifier

WORKDIR /workspace/sglang