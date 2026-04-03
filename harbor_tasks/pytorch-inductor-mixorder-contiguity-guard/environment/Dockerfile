FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone pytorch at the base commit (before the fix)
RUN git init /workspace && \
    cd /workspace && \
    git remote add origin https://github.com/pytorch/pytorch.git && \
    git fetch --depth=1 origin 63fcbe1040ffef63e82abd4e66da1d7554d23aa4 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace

# Minimal setup: just ensure the python package is importable for AST analysis.
# We do NOT install torch (too heavy / needs GPU); tests use targeted extraction.
ENV PYTHONPATH="/workspace"
RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"
