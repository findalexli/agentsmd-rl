FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone sglang at the base commit (before the fix)
RUN git init /workspace/sglang && \
    cd /workspace/sglang && \
    git remote add origin https://github.com/sgl-project/sglang.git && \
    git fetch --depth=1 origin f3970b17ef043c069e30a5cb9ffa83bd97f8679c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/sglang

# No heavy deps needed — tests use AST parsing and grep, not runtime imports
# (sglang imports torch at top-level, which we don't need for validation tests)

ENV PYTHONPATH="/workspace/sglang/python:${PYTHONPATH}"