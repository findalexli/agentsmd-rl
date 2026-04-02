FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Install CPU-only torch + minimal deps for testing
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir packaging numpy ruff pytest pytest-json-ctrf

# Clone vllm at the base commit (BEFORE the fix) — shallow fetch for speed
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/vllm-project/vllm.git && \
    git fetch --depth 1 origin bea23536f627b2b4153f2e672753b6034b78dedb && \
    git checkout FETCH_HEAD && \
    git config user.email "test@test.com" && \
    git config user.name "Test"

ENV PYTHONPATH=/repo
RUN mkdir -p /logs/verifier

WORKDIR /repo