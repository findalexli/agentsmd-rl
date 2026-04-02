FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

# Clone repo at base commit (before the fix) — shallow fetch for speed
RUN git init /workspace/slime && \
    cd /workspace/slime && \
    git remote add origin https://github.com/THUDM/slime.git && \
    git fetch --depth 1 origin e4d22dc929169fcc2cdf538d1798d9a5473f4d1d && \
    git checkout FETCH_HEAD

# No heavy deps needed - tests use AST parsing only (megatron not available on CPU)

RUN mkdir -p /logs/verifier

WORKDIR /workspace/slime
ENV PYTHONPATH="/workspace/slime:${PYTHONPATH:-}"