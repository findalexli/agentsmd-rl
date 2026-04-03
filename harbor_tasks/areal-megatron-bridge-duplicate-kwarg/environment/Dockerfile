FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at the buggy base commit (before the fix)
RUN git init /workspace/AReaL && \
    cd /workspace/AReaL && \
    git remote add origin https://github.com/inclusionAI/AReaL.git && \
    git fetch --depth=1 origin 722e235a37e4a9f3e288e54629179befa494156b && \
    git checkout FETCH_HEAD

# Install only minimal deps needed for syntax checking / AST parsing
# No torch/GPU needed — tests are syntax and AST-based
RUN mkdir -p /logs/verifier

WORKDIR /workspace/AReaL

ENV PYTHONPATH="/workspace/AReaL:${PYTHONPATH:-}"